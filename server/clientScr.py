
import wx
from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
from DB import DB
from server_protocol import server_protocol
import requests
import webbrowser


class SetLimitsDialog(wx.Dialog):
    def __init__(self, cpu_limit, memory_limit):
        """Constructor"""
        super().__init__(None, title="Set Limits", size=(250, 200))
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.cpuTextCtrl = wx.TextCtrl(panel, value=str(cpu_limit))
        self.memTextCtrl = wx.TextCtrl(panel, value=str(memory_limit))

        vbox.Add(wx.StaticText(panel, label="CPU Limit (%)"), 0, wx.ALL, 5)
        vbox.Add(self.cpuTextCtrl, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(wx.StaticText(panel, label="Memory Limit (%)"), 0, wx.ALL, 5)
        vbox.Add(self.memTextCtrl, 0, wx.EXPAND | wx.ALL, 5)

        self.okButton = wx.Button(panel, label="OK")
        self.okButton.Bind(wx.EVT_BUTTON, self.onOk)
        vbox.Add(self.okButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(vbox)

    def onOk(self, event):
        self.cpu_limit = float(self.cpuTextCtrl.GetValue())
        self.memory_limit = float(self.memTextCtrl.GetValue())

        self.EndModal(wx.ID_OK)


class MainPanel(wx.Panel):
    """
    Main panel class for the GUI, handling layout and update of process information.
    """
    def __init__(self, parent):
        """
        Constructor: Sets up the GUI elements.
        """
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent
        self.procs = []
        self.bad_procs = []
        self.sort_col = 0
        self.total_cpu = 0
        self.total_mem = 0
        cpu, memory = self.frame.myDB.get_comp_limits(self.frame.mac)

        self.cpu_limit = cpu  # Example CPU usage limit for classification.
        self.memory_limit = memory  # Example memory usage limit for classification.
        self.io_limit = 10

        # Column widths for the ObjectListView
        self.col_w = {"name": 175,
                      "pid": 80,
                      "user": 175,
                      "cwd": 175,
                      "cpu": 120,
                      "mem": 120,
                      "io": 120,
                      "threads": 100}

        self.procmonOlv = ObjectListView(self, style=wx.LC_REPORT | wx.BORDER_DEFAULT)
        self.procmonOlv.Bind(wx.EVT_LIST_COL_CLICK, self.onColClick)
        self.procmonOlv.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onSelect)

        self.setProcs()  # Initialize the ObjectListView with process columns.

        # Layout setup
        downSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.setLimitsBtn = wx.Button(self,  label="Set Limits")
        self.setLimitsBtn.Bind(wx.EVT_BUTTON, self.onSetLimits)

        self.processNum = wx.StaticText(self, -1, label="Number of Processes", style=wx.ALIGN_RIGHT)
        self.cpu_label = wx.StaticText(self, -1, label=f"CPU Limits - {self.cpu_limit}%", style=wx.ALIGN_RIGHT)
        self.mem_label = wx.StaticText(self, -1, label=f"memory Limits - {self.memory_limit}%", style=wx.ALIGN_RIGHT)

        downSizer.Add(self.setLimitsBtn, 1,  wx.ALL, 30)
        downSizer.Add(self.processNum, 1,  wx.ALL, 30)
        downSizer.Add(self.cpu_label, 1,  wx.ALL, 30)
        downSizer.Add(self.mem_label, 0,  wx.ALL, 30)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.procmonOlv, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(downSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(mainSizer)

        msg2send = server_protocol.build_set_cpu(self.cpu_limit)
        self.frame.comm.send_msg(self.frame.ip, msg2send)
        self.cpu_label.SetLabel(f"manager CPU Limits - {self.cpu_limit}%")
        self.frame.myDB.edit_cpu_limits(self.frame.mac, self.cpu_limit)

        msg2send = server_protocol.build_set_memory(self.memory_limit)
        self.frame.comm.send_msg(self.frame.ip, msg2send)
        self.mem_label.SetLabel(f"manager memory Limits - {self.memory_limit}%")
        # Update the screen based on the new limits if necessary
        self.frame.myDB.edit_mem_limits(self.frame.mac, self.memory_limit)

        pub.subscribe(self.updateDisplay, f"update-{self.frame.mac}")  # Subscribe to updates from the background thread.

    def close_window(self):
        wx.CallAfter(pub.sendMessage, "close scr", self.frame.mac)

    def onSetLimits(self, event):
        dialog = SetLimitsDialog(self.cpu_limit, self.memory_limit)
        if dialog.ShowModal() == wx.ID_OK:
            if not self.cpu_limit == dialog.cpu_limit:
                self.cpu_limit = dialog.cpu_limit
                msg2send = server_protocol.build_set_cpu(self.cpu_limit)
                self.frame.comm.send_msg(self.frame.ip, msg2send)
                self.cpu_label.SetLabel(f"manager CPU Limits - {self.cpu_limit}%")
                self.frame.myDB.edit_cpu_limits(self.frame.mac, self.cpu_limit)
            if not self.memory_limit == dialog.memory_limit:
                self.memory_limit = dialog.memory_limit
                msg2send = server_protocol.build_set_memory(self.memory_limit)
                self.frame.comm.send_msg(self.frame.ip, msg2send)
                self.mem_label.SetLabel(f"manager memory Limits - {self.memory_limit}%")
                # Update the screen based on the new limits if necessary
                self.frame.myDB.edit_mem_limits(self.frame.mac, self.memory_limit)

        dialog.Destroy()

    def onColClick(self, event):
        """
        Handles column click events to sort the process list.
        """
        self.sort_col = event.GetColumn()
        self.setProcs()

    def onSelect(self, event):
        """Handle selection of a process from the list."""
        item = event.GetItem()
        itemId = item.GetId()
        self.currentSelection = itemId
        obj = self.procmonOlv.GetSelectedObject()
        if obj is not None:
            self.currentProcess = obj  # Store the selected process object for later use
            menu = wx.Menu()

            # Create a non-clickable menu item as a title with the process name
            titleItem = wx.MenuItem(menu, wx.ID_ANY, obj.name, kind=wx.ITEM_NORMAL)
            titleItem.Enable(False)  # Make it non-clickable
            menu.Append(titleItem)
            menu.AppendSeparator()


            for option in ["search online", "kill process", "close"]:
                menu_item = menu.Append(wx.ID_ANY, option)
                self.Bind(wx.EVT_MENU, self.onStuff, menu_item)

            self.PopupMenu(menu)
            menu.Destroy()

            self.currentSelection = None
            self.setProcs()

        # ----------------------------------------------------------------------
    def internet_connection(self):
        """"
        checks if able to connect to thr internet
        """
        try:
            response = requests.get("https://www.tutorialspoint.com", timeout=5)

            return True

        except requests.ConnectionError:
            return False


    def onStuff(self, event):
        """Handle selection from the context menu."""
        # Directly use event.GetId() to differentiate actions
        menuItemId = event.GetId()
        menu = event.GetEventObject()
        item = menu.FindItemById(menuItemId)
        text = item.GetItemLabel()  # Use GetItemLabel to get the text of the menu item

        if text == "search online" and self.currentProcess is not None:
            # Display the process info in a popup window or message box
            if self.internet_connection():

                url = f"https://www.google.com/search?q={self.currentProcess.name}"

                webbrowser.open(url)
            else:
                wx.MessageBox("The Internet is not connected.","info", wx.OK | wx.ICON_INFORMATION)

        elif text == "kill process" and self.currentProcess is not None:
            # Attempt to kill the selected process
            pid = int(self.currentProcess.pid)
            msg2send = server_protocol.build_close_proc(pid)
            print("send kill process ------")
            self.frame.comm.send_msg(self.frame.ip, msg2send)

    def setProcs(self):
        """
        Updates the process list display.
        """
        cw = self.col_w
        cols = [
            ColumnDefn("Name", "left", cw["name"], "name"),
            ColumnDefn("PID", "left", cw["pid"], "pid"),
            ColumnDefn("User", "left", cw["user"], "user"),
            ColumnDefn("CWD", "left", cw["cwd"], "cwd"),
            ColumnDefn("CPU (%)", "left", cw["cpu"], "cpu"),
            ColumnDefn("Memory (%)", "left", cw["mem"], "mem"),
            ColumnDefn("io (num)", "left", cw["io"], "io"),
            ColumnDefn("Threads", "left", cw["threads"], "threads"),
        ]



        self.procmonOlv.SetColumns(cols)
        all_procs = self.procs + self.bad_procs  # Combine good and bad processes
        self.procmonOlv.SetObjects(all_procs)

        # Define a row formatter to color bad processes in red (entire row)
        def rowFormatter(listItem, process):
            if float(process.cpu) > self.cpu_limit or float(process.mem) > self.memory_limit:
                listItem.SetTextColour(wx.WHITE)  # Set text color
                listItem.SetBackgroundColour(wx.RED)  # Set background color
            else:
                listItem.SetTextColour(wx.BLACK)  # BLACK text color
                listItem.SetBackgroundColour(wx.WHITE)  # WHITE background color

        self.procmonOlv.rowFormatter = rowFormatter
        self.procmonOlv.RepopulateList()  # Apply the row formatter to current list items
        self.procmonOlv.SortBy(self.sort_col)



    def updateDisplay(self, good_procs, bad_procs, total_cpu, total_mem):
        """
        Callback function to update the GUI with new process information.
        """
        if not self.frame or not self.frame.IsShown():  # Check if the frame still exists
            return  # Exit early if the frame is gone
        print("in clientScr updateDisplay-----")
        self.procs = good_procs
        self.bad_procs = bad_procs
        self.total_cpu = total_cpu
        self.total_mem = total_mem

        self.setProcs()
        self.processNum.SetLabel(f"Number of Processes: {len(good_procs) + len(bad_procs)}")

class MainFrame(wx.Frame):
    """
    Main frame for the application.
    """
    def __init__(self, comm, computer_name,computer_ip):
        """
        Constructor: Initializes the main frame and panel.
        """
        wx.Frame.__init__(self, None, title=computer_name, size=(1024, 768))
        self.comm = comm
        self.mac = computer_name
        self.myDB = DB()
        self.ip = computer_ip
        self.Bind(wx.EVT_CLOSE, self.myClose)
        self.panel = MainPanel(self)
        self.Show()
        self.Maximize()  # Make the frame full screen with window decorations


    def myClose(self, evt):
        # Ensure any cleanup or final actions are done before closing
        # Unsubscribe from any pub/sub topics to avoid dangling references
        pub.unsubscribe(self.panel.updateDisplay, f"update-{self.mac}")
        wx.CallAfter(pub.sendMessage, "close scr", computer_name=self.mac)
        self.Destroy()  # Properly destroy the frame to close the application




if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()

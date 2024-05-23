import psutil
import wx
import webbrowser
from ObjectListView import ObjectListView, ColumnDefn
from threading import Thread
from pubsub import pub
from all.process import Process
import requests
import time
from ClientProtocol import ClientProtocol


# ----------------------------------------------------------------------
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
        self.okButton.Bind(wx.EVT_BUTTON, self.on_ok)
        vbox.Add(self.okButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(vbox)

    def on_ok(self, event):
        self.cpu_limit = float(self.cpuTextCtrl.GetValue())
        self.memory_limit = float(self.memTextCtrl.GetValue())

        self.EndModal(wx.ID_OK)


# ----------------------------------------------------------------------
class ProcThread(Thread):
    """
    Thread class for fetching and processing process information.
    """
    def __init__(self, comm, cpu_limit, memory_limit):
        Thread.__init__(self)
        self.comm = comm
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.start()

    def run(self):
        """
        Overrides the Thread.run method. Fetches process information and posts it for the GUI to update.
        """
        for proc in psutil.process_iter():
            try:
                # Initialize cpu_percent for accurate measurement later.
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        time.sleep(1)  # Wait a short time for more accurate CPU usage info.

        procs = []      # List to hold information on processes considered 'good'
        bad_procs = []  # List to hold information on processes considered 'bad'
        total_cpu = 0
        total_mem = 0

        send_msg = []
        for proc in psutil.process_iter():
            try:
                p = psutil.Process(proc.pid)
                cpu_usage = proc.cpu_percent(interval=None)
                proc_cpu = round(cpu_usage / 8, 3)
                proc_mem = round(p.memory_percent(), 3)
                proc_io = p.io_counters()
                proc_io = proc_io[0] + proc_io[1]  # total read a& write operations

                new_proc = Process(p.name(), str(p.pid), p.username(), p.cwd(), str(proc_cpu), str(proc_mem),
                                   str(proc_io), str(p.num_threads()))

                if p.pid != 0:
                    total_cpu += cpu_usage / 8
                total_mem += p.memory_percent()

                proc_msg = f"{p.name()},{str(p.pid)},{p.username()},{p.cwd()},{str(proc_cpu)},{str(proc_mem)}," \
                           f"{str(proc_io)},{str(p.num_threads())}"
                send_msg.append(proc_msg)

                if proc_cpu > self.cpu_limit or proc_mem > self.memory_limit:
                    bad_procs.append(new_proc)
                else:
                    procs.append(new_proc)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Use wxPython's CallAfter to safely update the GUI from this thread.
        wx.CallAfter(pub.sendMessage, 'update', good_procs=procs, bad_procs=bad_procs,
                     total_mem=total_mem, total_cpu=total_cpu)
        msg2send = ClientProtocol.build_process_details(send_msg, total_mem, total_cpu)
        self.comm.send(msg2send)


# ----------------------------------------------------------------------
class MainPanel(wx.Panel):
    """
    Main panel class for the GUI, handling layout and update of process information.
    """
    def __init__(self, parent, params=(5, 5, 5)):
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
        self.currentSelection = None
        self.currentProcess = None

        self.manager_cpu_limit = 5  # manager limits
        self.manager_memory_limit = 5  # manager limits
        self.cpu_limit = self.manager_cpu_limit
        self.memory_limit = self.manager_memory_limit

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
        self.procmonOlv.Bind(wx.EVT_LIST_COL_CLICK, self.on_col_click)
        self.procmonOlv.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_select)

        self.set_procs()  # Initialize the ObjectListView with process columns.

        # Layout setup
        down_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.setLimitsBtn = wx.Button(self,  label="Set Limits")
        self.setLimitsBtn.Bind(wx.EVT_BUTTON, self.on_set_limits)

        # setting labels to show on thw screen
        self.processNum = wx.StaticText(self, -1, label="Number of Processes", style=wx.ALIGN_RIGHT)

        self.cpu_label = wx.StaticText(self, -1, label=f"CPU Limits - {self.cpu_limit}%"
                                                       f"    manager limits - {self.manager_cpu_limit}",
                                       style=wx.ALIGN_RIGHT)

        self.mem_label = wx.StaticText(self, -1, label=f"memory Limits - {self.memory_limit}%"
                                                       f"    manager limits- {self.manager_memory_limit}",
                                       style=wx.ALIGN_RIGHT)

        down_sizer.Add(self.setLimitsBtn, 1,  wx.ALL, 30)
        down_sizer.Add(self.processNum, 1,  wx.ALL, 30)
        down_sizer.Add(self.cpu_label, 1,  wx.ALL, 30)
        down_sizer.Add(self.mem_label, 0,  wx.ALL, 30)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.procmonOlv, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(down_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)

        # set timer to know when to update the screen
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.update("")  # Initial update

        pub.subscribe(self.update_display, 'update')  # Subscribe to updates from the background thread.
        pub.subscribe(self.update_mgr_limits, 'update_mgr_limits')  # Subscribe to updates from the background thread.
        pub.subscribe(self.update_my_limits, 'update_my_limits')  # Subscribe to updates from the background thread.
        pub.subscribe(self.kill_process, 'kill process')  # Subscribe to updates from the background thread.

    # ----------------------------------------------------------------------
    def kill_process(self, pid):
        # Attempt to kill the selected process
        pid = int(pid)

        try:
            p = psutil.Process(pid)
            p.terminate()  # Terminate the process
            wx.MessageBox(f"Process (PID: {pid}) terminated successfully.",
                          "Process Terminated by manager", wx.OK | wx.ICON_INFORMATION)
            self.update("")  # Update the process list to reflect the change
        except psutil.NoSuchProcess:
            wx.MessageBox(f"No process found with PID: {pid}", "Error", wx.OK | wx.ICON_ERROR)
        except psutil.AccessDenied:
            wx.MessageBox(f"Access denied when trying to kill PID: {pid}. You might need higher privileges.",
                          "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"An error occurred while trying to kill PID: {pid}. Error: {str(e)}", "Error",
                          wx.OK | wx.ICON_ERROR)

    # ----------------------------------------------------------------------
    def update_my_limits(self, limits):
        print("in limits", limits)
        cpu, memory, disk = limits

        self.manager_cpu_limit = cpu  # manager limits
        self.manager_memory_limit = memory  # manager limits
        self.cpu_limit = self.manager_cpu_limit
        self.memory_limit = self.manager_memory_limit

    # ----------------------------------------------------------------------
    def update_mgr_limits(self, limits):
        print("in limits", limits)
        self.manager_cpu_limit, self.manager_memory_limit = limits

        if self.cpu_limit > float(self.manager_cpu_limit):
            self.cpu_limit = float(self.manager_cpu_limit)

        if self.memory_limit > float(self.manager_memory_limit):
            self.memory_limit = float(self.manager_memory_limit)

        self.cpu_label.SetLabel(f"CPU Limits - {self.cpu_limit}%"
                                f"    manager limits- {self.manager_cpu_limit}")
        self.mem_label.SetLabel(f"memory Limits - {self.memory_limit}%"
                                f"    manager limits- {self.manager_memory_limit}")

    # ----------------------------------------------------------------------
    def on_set_limits(self, event):
        dialog = SetLimitsDialog(self.cpu_limit, self.memory_limit)
        if dialog.ShowModal() == wx.ID_OK:
            self.cpu_limit = dialog.cpu_limit
            self.memory_limit = dialog.memory_limit

            if self.cpu_limit > float(self.manager_cpu_limit):
                self.cpu_limit = float(self.manager_cpu_limit)

            if self.memory_limit > float(self.manager_memory_limit):
                self.memory_limit = float(self.manager_memory_limit)

            self.cpu_label.SetLabel(f"CPU Limits - {self.cpu_limit}%"
                                    f"    manager limits- {self.manager_cpu_limit}")
            self.mem_label.SetLabel(f"memory Limits - {self.memory_limit}%"
                                    f"    manager limits- {self.manager_memory_limit}")
            # Update the screen based on the new limits if necessary
        dialog.Destroy()

    # ----------------------------------------------------------------------
    def on_col_click(self, event):
        """
        Handles column click events to sort the process list.
        """
        self.sort_col = event.GetColumn()
        self.set_procs()

    # ----------------------------------------------------------------------
    def on_select(self, event):
        """Handle selection of a process from the list."""
        item = event.GetItem()
        item_id = item.GetId()
        self.currentSelection = item_id
        obj = self.procmonOlv.GetSelectedObject()
        if obj is not None:
            self.currentProcess = obj  # Store the selected process object
            menu = wx.Menu()

            # Create a non-clickable menu item as a title with the process name
            title_item = wx.MenuItem(menu, wx.ID_ANY, obj.name, kind=wx.ITEM_NORMAL)
            title_item.Enable(False)  # Make it non-clickable
            menu.Append(title_item)
            menu.AppendSeparator()

            # menu options below the title
            for option in ["search online", "kill process", "close"]:
                menu_item = menu.Append(wx.ID_ANY, option)
                self.Bind(wx.EVT_MENU, self.on_stuff, menu_item)

            self.PopupMenu(menu)
            menu.Destroy()

            self.currentSelection = None
            self.set_procs()

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



    def on_stuff(self, event):
        """Handle selection from the context menu."""
        # Directly use event.GetId() to differentiate actions
        menu_item_id = event.GetId()
        menu = event.GetEventObject()
        item = menu.FindItemById(menu_item_id)
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
            try:
                p = psutil.Process(pid)
                p.terminate()  # Terminate the process
                wx.MessageBox(f"Process {self.currentProcess.name} (PID: {pid}) terminated successfully.",
                              "Process Terminated", wx.OK | wx.ICON_INFORMATION)
                self.update("")  # Update the process list to reflect the change
            except psutil.NoSuchProcess:
                wx.MessageBox(f"No process found with PID: {pid}", "Error", wx.OK | wx.ICON_ERROR)
            except psutil.AccessDenied:
                wx.MessageBox(f"Access denied when trying to kill PID: {pid}. You might need higher privileges.",
                              "Error", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f"An error occurred while trying to kill PID: {pid}. Error: {str(e)}", "Error",
                              wx.OK | wx.ICON_ERROR)

    # ----------------------------------------------------------------------
    def set_procs(self):
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
        def row_formatter(list_item, process):
            if float(process.cpu) > self.cpu_limit or float(process.mem) > self.memory_limit:
                list_item.SetTextColour(wx.WHITE)  # Set text color
                list_item.SetBackgroundColour(wx.RED)  # Set background color
            else:
                list_item.SetTextColour(wx.BLACK)  # Default text color
                list_item.SetBackgroundColour(wx.WHITE)  # Default background color

        self.procmonOlv.rowFormatter = row_formatter
        self.procmonOlv.RepopulateList()  # Apply the row formatter to current list items
        self.procmonOlv.SortBy(self.sort_col)

    # ----------------------------------------------------------------------
    def update(self, event):
        # Start a thread to get the pid information and limits
        ProcThread(self.frame.comm, self.cpu_limit, self.memory_limit)

    # ----------------------------------------------------------------------
    def update_display(self, good_procs, bad_procs, total_cpu, total_mem):
        """
        Callback function to update the GUI with new process information.
        """
        self.procs = good_procs
        self.bad_procs = bad_procs
        self.total_cpu = total_cpu
        self.total_mem = total_mem

        self.set_procs()
        self.processNum.SetLabel(f"Number of Processes: {len(good_procs) + len(bad_procs)}")
        if not self.timer.IsRunning():
            self.timer.Start(10000)


# ----------------------------------------------------------------------
class MainFrame(wx.Frame):
    """
    Main frame for the application.
    """
    def __init__(self, comm):
        """
        Constructor: Initializes the main frame and panel.
        """
        wx.Frame.__init__(self, None, title="double task manager", size=(1024, 768))
        self.comm = comm
        panel = MainPanel(self)
        self.Show()
        self.Maximize()  # Make the frame full screen with window decorations


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()

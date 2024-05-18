import wx
from DB import DB
from pubsub import pub
from clientScr import MainFrame
from server_protocol import server_protocol
import NetworkStaff


class MyFrame(wx.Frame):
    def __init__(self, comm, parent=None):
        super(MyFrame, self).__init__(parent, title="login", size=(500, 500))
        self.SetBackgroundColour(wx.LIGHT_GREY)
        # create status bar
        self.server = comm
        self.myDB = DB()
        self.CreateStatusBar(1)
        self.SetStatusText("")
        # Make the frame full screen
        self.Maximize()  # Make the frame full screen with window decorations
        # create main panel - to put on the others panels
        main_panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(main_panel, 1, wx.EXPAND)
        # arrange the frame
        self.curr = main_panel
        self.SetSizer(box)
        self.Layout()
        self.Show()

    def replace(self, new_pnl):
        self.curr.Hide()
        box = self.GetSizer()
        box.Replace(self.curr, new_pnl)
        self.SetSizer(box)
        self.curr = new_pnl
        self.curr.Show()
        self.Layout()


class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.SetSize(self.frame.GetSize())


        v_box = wx.BoxSizer(wx.VERTICAL)
        # create object for each panel
        self.login = LoginPanel(self, self.frame)
        self.registration = RegistrationPanel(self, self.frame)
        self.mainScreen = MainComputersPanel(self, self.frame)
        self.setting = SettingPanel(self, self.frame)

        self.prev_scr = self.mainScreen

        # self.files = FilesPanel(self,self.frame)
        v_box.Add(self.login, 1, wx.EXPAND)
        v_box.Add(self.registration, 1, wx.EXPAND)
        v_box.Add(self.mainScreen, 1, wx.EXPAND)
        v_box.Add(self.setting, 1, wx.EXPAND)



        # The first panel to show
        self.login.Show()

        self.SetSizer(v_box)
        self.Layout()


class LogoPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.SetSize(self.frame.GetSize())
        self.parent = parent
        self.SetBackgroundColour(wx.CYAN)

class LoginPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.SetSize(self.frame.GetSize())
        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)
        # Get the panel size
        panel_width, panel_height = self.GetSize()
        # Define the desired logo size as a percentage of the panel size
        logo_width = int(panel_width * 0.5)
        logo_height = int(panel_height * 0.3)


        # Load and scale the logo image
        logo = wx.Image("logo.png", wx.BITMAP_TYPE_ANY).Scale(logo_width, logo_height).ConvertToBitmap()
        static_logo = wx.StaticBitmap(self, -1, logo, (10, 5), (logo.GetWidth(), logo.GetHeight()))

        sizer.Add(static_logo, 0, wx.CENTER | wx.TOP, 10)

        # title
        title = wx.StaticText(self, -1, label="Login Panel")
        title_font = wx.Font(30, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(title_font)

        # username
        name_box = wx.BoxSizer(wx.HORIZONTAL)
        name_text = wx.StaticText(self, 1, label="UserName: ")
        self.nameField = wx.TextCtrl(self, -1, name="username", size=(250, -1))

        name_box.Add(name_text, 0, wx.ALL, 10)
        name_box.Add(self.nameField, 0, wx.ALL, 10)

        # password
        pass_box = wx.BoxSizer(wx.HORIZONTAL)
        pass_text = wx.StaticText(self, 1, label="Password: ")

        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(250, -1))

        pass_box.Add(pass_text, 0, wx.ALL, 10)
        pass_box.Add(self.passField, 0, wx.ALL, 10)

        # login & registration buttons
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        login_btn = wx.Button(self, wx.ID_ANY, label="login", size=(225, 90))
        login_btn.SetBackgroundColour("#3399FF")  # Blue background
        login_btn.Bind(wx.EVT_BUTTON, self.handle_login)

        btn_box.Add(login_btn, 0, wx.ALL, 10)

        reg_btn = wx.Button(self, wx.ID_ANY, label="Registration", size=(225, 90))
        reg_btn.Bind(wx.EVT_BUTTON, self.handle_reg)
        reg_btn.SetBackgroundColour("#3399FF")  # Blue background
        btn_box.Add(reg_btn, 1, wx.ALL, 10)

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, logo_height-100)
        sizer.AddSpacer(40)
        sizer.Add(name_box, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(pass_box, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(5)
        sizer.Add(btn_box, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_login(self, event):

        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password:
            self.frame.SetStatusText("Must enter name and password")
        elif self.frame.myDB.getMng_pass(username) == password:
            self.handle_connection(event)
        else:
            self.nameField.Clear()
            self.passField.Clear()
            self.frame.SetStatusText("wrong user name or password")

    def handle_connection(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.mainScreen.Show()

    def handle_reg(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.registration.Show()


class RegistrationPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.SetSize(self.frame.GetSize())
        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)

        # title
        title = wx.StaticText(self, -1, label="registration Panel")
        title_font = wx.Font(30, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(title_font)

        # username
        name_box = wx.BoxSizer(wx.HORIZONTAL)
        name_text = wx.StaticText(self, 1, label="UserName: ")
        self.nameField = wx.TextCtrl(self, -1, name="username", size=(250, -1))

        name_box.Add(name_text, 0, wx.ALL, 10)
        name_box.Add(self.nameField, 0, wx.ALL, 10)

        # password
        pass_box = wx.BoxSizer(wx.HORIZONTAL)
        pass_text = wx.StaticText(self, 1, label="Password: ")
        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(250, -1))

        pass_box.Add(pass_text, 0, wx.ALL, 10)
        pass_box.Add(self.passField, 0, wx.ALL, 10)

        # registration & back-to-login buttons
        btn_box = wx.BoxSizer(wx.HORIZONTAL)

        reg_btn = wx.Button(self, wx.ID_ANY, label="Register", size=(150, 60))
        reg_btn.SetBackgroundColour("#3399FF")  # Blue background
        reg_btn.Bind(wx.EVT_BUTTON, self.handle_reg)

        btn_box.Add(reg_btn, 0, wx.ALL, 10)

        # Back to Login button
        back_btn = wx.Button(self, wx.ID_ANY, label="Back to Login", size=(150, 60))
        back_btn.Bind(wx.EVT_BUTTON, self.back_to_login)
        back_btn.SetBackgroundColour("#3399FF")  # Blue background
        btn_box.Add(back_btn, 1, wx.ALL, 10)

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 10)
        sizer.AddSpacer(100)
        sizer.Add(name_box, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(pass_box, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(5)
        sizer.Add(btn_box, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()


    def back_to_login(self, event):
        self.Hide()  # Hide the registration panel
        self.parent.login.Show()  # Show the login panel

    def handle_reg(self, event):

        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password:
            self.frame.SetStatusText("Must enter name and password")
        else:
            status = self.frame.myDB.add_username(username, password)
            if status:
                self.frame.SetStatusText("waiting for Server approve")
                self.after_reg(event)
            else:
                self.nameField.Clear()
                self.passField.Clear()
                self.frame.SetStatusText("user name already exist")

    def after_reg(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.login.Show()


class MainComputersPanel(wx.Panel):
    def __init__(self, parent, frame):
        super(MainComputersPanel, self).__init__(parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.SetSize(self.frame.GetSize())
        self.parent = parent

        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self, -1, label="Main Computers Panel")
        title_font = wx.Font(30, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(title_font)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer(1)  # Pushes the button to the right
        image = wx.Image("set.png", wx.BITMAP_TYPE_ANY).Scale(50, 50)  # Adjust the path and size as needed
        bitmap = wx.Bitmap(image)

        # Create a BitmapButton
        set_btn = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bitmap, size=(50, 50), name="setting")  # Adjust size as needed
        set_btn.Bind(wx.EVT_BUTTON, self.handle_setting)


        button_sizer.Add(set_btn, 0, wx.ALL | wx.BOTTOM, 10)
        # Setup a grid sizer for computer icons
        self.computer_icons_sizer = wx.GridSizer(rows=4, cols=4, vgap=3, hgap=3)

        self.sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        self.sizer.AddSpacer(10)
        self.sizer.Add(self.computer_icons_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(button_sizer, 0, wx.EXPAND | wx.BOTTOM, 50)
        self.SetSizer(self.sizer)
        self.Layout()
        self.Hide()

        # Track computer widgets for removal
        self.computer_widgets = {}  # [mac]:[button, flag, ip, windows_bad_color]


        pub.subscribe(self.add_computer, "new computer")
        pub.subscribe(self.remove_computer, "delete computer")
        pub.subscribe(self.close_computer_scr, "close scr")
        pub.subscribe(self.bad_comp, "bad comp")



    def handle_setting(self, event):
        self.parent.prev_scr = self.parent.mainScreen
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.setting.Show()

    def close_computer_scr(self, computer_name):
        self.computer_widgets[computer_name][1] = False

        print("close--------------")

    def on_computer_click(self, event): #, computer_name):

        computer_name = event.GetEventObject().GetName()

        print(f"Clicked on {computer_name}-{computer_name}")  # Placeholder action

        if not self.computer_widgets[computer_name][1]:
            self.computer_widgets[computer_name][1] = True
            client_screen = MainFrame(self.frame.server, computer_name, self.computer_widgets[computer_name][2])

    def bad_comp(self, computer_name, status):

        print("in bad_com-----", computer_name,self.computer_widgets[computer_name][1],self.computer_widgets[computer_name][2], status)

        if computer_name in self.computer_widgets.keys():

            comp = self.computer_widgets[computer_name][0].GetChildren()[0].GetWindow()

            if status and not self.computer_widgets[computer_name][1] and not self.computer_widgets[computer_name][3]:
                # Access the BitmapButton for the computer
                print("in bad com -=-==--==-=-=-==-=-=-=-=-")

                # Load the new image and update the button
                image = wx.Image("red.png", wx.BITMAP_TYPE_ANY).Scale(50, 50)  # Adjust the path and size as needed
                bitmap = wx.Bitmap(image)
                wx.Button.SetBitmap(comp, bitmap)

                self.computer_widgets[computer_name][3] = True

                # Refresh the button to show the updated image
                comp.Refresh()

            elif not status and not self.computer_widgets[computer_name][1] and  self.computer_widgets[computer_name][3]:
                # Access the BitmapButton for the computer
                print("in bad com -=-==--==-=-=-==-=-=-=-=-")

                # Load the new image and update the button
                image = wx.Image("comp.png", wx.BITMAP_TYPE_ANY).Scale(50, 50)  # Adjust the path and size as needed
                bitmap = wx.Bitmap(image)
                wx.Button.SetBitmap(comp, bitmap)

                self.computer_widgets[computer_name][2] = False

                # Refresh the button to show the updated image
                comp.Refresh()


            self.Layout()



    def add_computer(self, computer_name, computer_ip):
        # Create a vertical box sizer to hold the image and the name label
        computer_sizer = wx.BoxSizer(wx.VERTICAL)

        # Load the image and create a bitmap
        image = wx.Image("comp.png", wx.BITMAP_TYPE_ANY).Scale(50, 50)
        bitmap = wx.Bitmap(image)

        # Create a BitmapButton
        computer_button = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bitmap, size=(60, 70), name=computer_name)
        computer_button.Bind(wx.EVT_BUTTON, self.on_computer_click)
        computer_button.Bind(wx.EVT_RIGHT_DOWN, self.on_computer_right_click)

        # Create a StaticText for the computer name
        computer_label = wx.StaticText(self, label=computer_name)
        computer_label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL))


        # Add the BitmapButton and StaticText to the vertical sizer
        computer_sizer.Add(computer_button, 0, wx.ALL | wx.CENTER, 5)
        computer_sizer.Add(computer_label, 0, wx.ALL | wx.CENTER, 5)


        # Add the computer_sizer to the main sizer and update tracking
        self.computer_icons_sizer.Add(computer_sizer, 0, wx.ALL, 5)
        self.computer_widgets[computer_name] = [computer_sizer, False, computer_ip, False]

        print("in add - ",self.computer_widgets)

        # Ensure the layout is updated to reflect the changes
        self.Layout()

    def on_computer_right_click(self, event): #, computer_name):

        self.computer_name = event.GetEventObject().GetName()

        self.selected_computer = self.computer_name
        # Create a popup menu
        popup_menu = wx.Menu()

        # Add menu items
        menu_close = popup_menu.Append(-1, "Close Menu")
        menu_shutdown = popup_menu.Append(-1, "Shutdown Computer")

        # Bind menu item events to handlers
        self.Bind(wx.EVT_MENU, self.on_close_menu, menu_close)
        self.Bind(wx.EVT_MENU, self.on_shutdown_computer, menu_shutdown)

        # Display the menu
        self.PopupMenu(popup_menu, event.GetPosition())
        popup_menu.Destroy()

    def on_close_menu(self, event):
        # This can be used to perform any cleanup or actions needed when closing the menu
        pass

    def on_shutdown_computer(self, event): #, computer_name):
        msg2send = server_protocol.build_close_pc()
        self.frame.server.send_msg(self.computer_widgets[self.selected_computer][2], msg2send)

        self.remove_computer(self.selected_computer)

    def remove_computer(self, computer_name):
        print("compter_name: ",computer_name)

        print("in remove - ", self.computer_widgets)

        if computer_name in self.computer_widgets.keys():
            # Retrieve the BitmapButton directly

            computer_box = self.computer_widgets[computer_name][0]

            windows = []
            for child in computer_box.GetChildren():
                windows.append(child.GetWindow())

            for child in windows:
                print(child)
                child.Destroy()

            self.computer_icons_sizer.Remove((computer_box))

            # Remove the entry from the tracking dictionary
            del self.computer_widgets[computer_name]  #[0]

            print("box:", computer_box)

            # Update the layout
            self.Layout()

            print("in end remove - ", self.computer_widgets)
        else:
            print(f"Computer {computer_name} not found")


class AddComputerDialog(wx.Dialog):
    def __init__(self, db):
        """Constructor"""
        super().__init__(None, title="Add Computer", size=(250, 400))
        self.myDB = db
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.macTextCtrl = wx.TextCtrl(panel, name="mac")
        self.descTextCtrl = wx.TextCtrl(panel, name="desc")
        self.cpuTextCtrl = wx.TextCtrl(panel, name="cpu")
        self.memoryTextCtrl = wx.TextCtrl(panel, name="memory")
        self.msgText = wx.StaticText(panel, name="msg", label="")

        vbox.Add(wx.StaticText(panel, label="MAC address (XX:XX:XX:XX:XX:XX)"), 0, wx.ALL, 5)
        vbox.Add(self.macTextCtrl, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(wx.StaticText(panel, label="Description"), 0, wx.ALL, 5)
        vbox.Add(self.descTextCtrl, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(wx.StaticText(panel, label="CPU limit"), 0, wx.ALL, 5)
        vbox.Add(self.cpuTextCtrl, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(wx.StaticText(panel, label="MEMORY limit"), 0, wx.ALL, 5)
        vbox.Add(self.memoryTextCtrl, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.msgText, 0, wx.ALL, 20)

        self.cancelButton = wx.Button(panel, label="cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.on_cancel)
        vbox.Add(self.cancelButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.okButton = wx.Button(panel, label="Add")
        self.okButton.Bind(wx.EVT_BUTTON, self.on_add)
        vbox.Add(self.okButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(vbox)

    def on_cancel(self, event):
        print("in olk")

        self.EndModal(wx.ID_OK)

    def on_add(self, event):

        self.data_checked = False

        print("in check")
        mac = self.macTextCtrl.GetValue()
        desc = self.descTextCtrl.GetValue()
        cpu = self.cpuTextCtrl.GetValue()
        memory = self.memoryTextCtrl.GetValue()

        print("ssss",mac,desc,cpu,memory)
        if mac == "" or desc=="":
            print("set msg")
            self.msgText.SetLabelText("you must enter MAC and desc")
        elif mac:
            if self.myDB.is_mac_exist(mac):
                self.msgText.SetLabelText("MAC already exist..")
            else:

                if not NetworkStaff.check_mac_in_network(mac):
                    self.msgText.SetLabelText("MAC not alive in LAN..")

                else:
                    if not cpu:
                        cpu = 5
                    if not memory:
                        memory = 5

                    status = self.myDB.add_mac(mac, desc, int(cpu), int(memory))
                    self.msgText.SetLabelText("data is ok..")
                    self.EndModal(wx.ID_OK)



class SettingPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent)
        self.frame = frame
        self.parent = parent
        self.SetSize(self.frame.GetSize())


        self.v_box = wx.BoxSizer(wx.VERTICAL)

        # title
        title = wx.StaticText(self, -1, label="Setting Panel")
        title_font = wx.Font(30, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(title_font)

        self.v_box.Add(title, 0, wx.CENTER | wx.TOP, 50)
        self.v_box.AddSpacer(10)

        self.compuersList = wx.ListCtrl(self, size=(600,400),style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.compuersList.InsertColumn(0, 'MAC', width=150)
        self.compuersList.InsertColumn(1, 'Description', width=150)
        self.compuersList.InsertColumn(2, 'CPU limit', width=150)
        self.compuersList.InsertColumn(3, 'MEMORY limit', width=146)
        self.compuersList.Bind(wx.EVT_LEFT_DCLICK, self.on_item_selected)  #wx.EVT_LIST_ITEM_SELECTED
        self.index = 0
        self.curr_mac = None

        self.display_details()

        self.v_box.Add(self.compuersList, 0, wx.CENTER | wx.ALL, 10)

        btn_box = wx.BoxSizer(wx.HORIZONTAL)

        add_btn = wx.Button(self, wx.ID_ANY, label="add computer", size=(225, 90))
        add_btn.SetBackgroundColour("#3399FF")  # Blue background
        add_btn.Bind(wx.EVT_BUTTON, self.add_computer)
        btn_box.Add(add_btn, 0, wx.RIGHT,20)

        back_btn = wx.Button(self, wx.ID_ANY, label="back", size=(225, 90))
        back_btn.SetBackgroundColour("#3399FF")  # Blue background
        back_btn.Bind(wx.EVT_BUTTON, self.go_back)
        btn_box.Add(back_btn, 0, wx.LEFT, 20)

        self.v_box.Add(btn_box, 1, wx.CENTER | wx.BOTTOM, 100)

        self.SetSizer(self.v_box)
        self.Layout()
        self.Hide()

    def add_computer(self, event):
        print("in add")

        dialog = AddComputerDialog(self.frame.myDB)
        if dialog.ShowModal() == wx.ID_OK:
            self.mac = dialog.macTextCtrl
            self.desc = dialog.descTextCtrl
            self.cpu_limit = dialog.cpuTextCtrl
            self.memory_limit = dialog.memoryTextCtrl
            print(self.cpu_limit, "======")
            self.compuersList.DeleteAllItems()
            self.display_details()
        dialog.Destroy()

    def go_back(self, event):
        print("in go back")
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.prev_scr.Show()
        self.Layout()

    def on_item_selected(self, event):
        print("in select", event)
        item = self.compuersList.GetFirstSelected()
        self.curr_mac = self.compuersList.GetItem(item,0).GetText()
        print(self.curr_mac)

        self.menu = wx.Menu()


        menu_title = wx.MenuItem(self.menu, wx.ID_ANY, f"delete computer {self.curr_mac} are you shure?", kind=wx.ITEM_NORMAL)
        menu_title.Enable(False)  # Make it non-clickable
        self.menu.Append(menu_title)
        self.menu.AppendSeparator()

        # menu options below the title
        for option in ["YES", "NO"]:
            menu_item = self.menu.Append(wx.ID_ANY, option)
            self.Bind(wx.EVT_MENU, self.on_stuff, menu_item)

        self.PopupMenu(self.menu)
        self.menu.Destroy()
        event.Skip()


    def on_stuff(self, ev):
        """Handle selection from the context menu."""
        # Directly use event.GetId() to differentiate actions
        menu_item_id = ev.GetId()
        menu = ev.GetEventObject()
        item = menu.FindItemById(menu_item_id)
        text = item.GetItemLabel()  # Use GetItemLabel to get the text of the menu item

        if text == "YES":
            status = self.frame.myDB.del_mac(self.curr_mac)
            if status:

                self.compuersList.DeleteAllItems()
                self.display_details()


        else:
            pass


    def display_details(self):
        computers = self.frame.myDB.get_computers_details()
        self.index = 0
        for data in computers:
            mac, desc, cpu, memory = data
            print(self.index)
            self.compuersList.InsertItem(self.index, mac)
            self.compuersList.SetItem(self.index, 1, desc)
            self.compuersList.SetItem(self.index, 2, str(cpu))
            self.compuersList.SetItem(self.index, 3, str(memory))
            self.index += 1

        self.SetSizer(self.v_box)
        self.Layout()





if __name__ == "__main__":
    app = wx.App()
    myDB = DB()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()

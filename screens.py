from tkinter import Button, Frame, Label, Entry, messagebox, GROOVE, NORMAL, DISABLED
import tkinter
import threading
import ftp_options

class Screen(object):
    """ Inherited by all screen objects and provides common solutions """
    def __init__(self):
        self.next_window=None
        # create widgets for screen
        self.create_widgets()
        
    def kill_window(self):
        # kill the screen
        self.master.destroy()
        
    def get_next_window(self):
        # get the next screen to be loaded
        return self.next_window

class Main_Menu(Frame, Screen):
    """ The first and main menu that appears when the program starts. """
    def __init__(self, master):
        super(Main_Menu, self).__init__(master)
        Screen.__init__(self)
    
    def create_widgets(self):
        # create option buttons for menu
        Button(height=1, width=7, 
               font=('times',33,'bold'), 
               text='Backup', 
               command=self.backup_pressed).place(x=28,y=20)
        Button(height=1, width=8, 
               font=('times',20), 
               text='Exit', 
               command=self.exit_pressed).place(x=60,y=120)
        
    def backup_pressed(self):
        # the next screen to load will be 'login'
        self.kill_window()
        self.next_window = 'login'
        
    def exit_pressed(self):
        # the program will exit on return
        self.kill_window()
        self.next_window = ''
        
class Login(Frame, Screen):
    """ Asks for FTP server IP, user and password and is tested """
    def __init__(self, master, config):
        super(Login, self).__init__(master)
        self.ftp_ip = tkinter.StringVar()
        self.ftp_user = tkinter.StringVar()
        self.ftp_pass = tkinter.StringVar()
        self.config = config
        self.ftp = None
        Screen.__init__(self)
    
    def create_widgets(self):
        # create a field for server IP, the default IP from the cfg is loaded into entry box
        Label(borderwidth=1, 
              text='Server IP:',
              font=('times',10,'bold')).place(x=10,y=10)
        self.ip_entry_widget = Entry(font=('times',10),
                                     textvariable=self.ftp_ip,
                                     relief=GROOVE,
                                     width=25)
        self.ip_entry_widget.place(x=80,y=10)
        self.ip_entry_widget.insert(0,self.config.ftp_ip)
        # create a field for server Username
        Label(borderwidth=1, 
              text='Username:',
              font=('times',10,'bold')).place(x=10,y=35)
        self.user_entry_widget = Entry(font=('times',10),
                                       textvariable=self.ftp_user,
                                       relief=GROOVE,
                                       width=25)
        self.user_entry_widget.place(x=80,y=35)
        # create a field for server Password
        Label(borderwidth=1, 
              text='Password:',
              font=('times',10,'bold')).place(x=10,y=60)
        self.pass_entry_widget = Entry(font=('times',10),
                                       textvariable=self.ftp_pass,
                                       relief=GROOVE,
                                       show="*",
                                       width=25)
        self.pass_entry_widget.place(x=80,y=60)
        Button(width= 8, 
               font=('times',20,'bold'),
               text='Start', 
               command=self.login_pressed).place(x=55,y=90)
        
    def login_pressed(self):
        # tests and saves connection with the server based on user input
        self.ftp, error = ftp_options.connect_to_ftp(self.ftp_ip.get(), self.ftp_user.get(), self.ftp_pass.get())
        # if an error occurs rephrase it into a useful message
        if error:
            error_msg = "Cannot connect to server, "
            if (str(error)).startswith("[Errno 11004]"):
                error_msg += "Check the IP address"
            elif (str(error)).startswith("530"):
                error_msg += "Login incorrect"
            elif (str(error)).startswith("[WinError 10060]"):
                error_msg += "Check the IP address and the server you are trying to connect to supports FTP"
            else:
                error_msg += error
            messagebox.showerror(title='Error', message=error_msg)
            return
        self.kill_window()
        # the next screen to load will be 'backup'
        self.next_window = 'backup'
        
    def exit_pressed(self):
        # the program will exit on return
        self.kill_window()
        self.next_window = ''
        
    def get_ftp_connection(self):
        # return FTP connection instance
        return self.ftp

        
class Backup(Frame, Screen):
    """ Starts and monitors backup process  """
    def __init__(self, master, ftp_connection, config):
        super(Backup, self).__init__(master)
        self.ftp_connection = ftp_connection
        self.config = config
        Screen.__init__(self)
        self.start_backup()
        self.master.after(1, self.check_current_file())
    
    def create_widgets(self):
        Label(borderwidth=1, 
              text='Backing up ...',
              font=('times',10,'bold')).place(x=10,y=10)
        self.current_file = Label(borderwidth=1, 
                                  text='',
                                  font=('times',10))
        self.current_file.place(x=10,y=30)
        self.stop_button_widget = Button(height=1, width=5,
                                         font=('times',15),
                                         text='Stop',
                                         command=self.stop_pressed)
        self.stop_button_widget.place(x=10,y=55)
        self.done_button_widget = Button(height=1, width=5,
                                         font=('times',15,'bold'),
                                         text='Done',
                                         command=self.go_to_main_menu,
                                         state=DISABLED)
        self.done_button_widget.place(x=620,y=55)
        
    def go_to_main_menu(self):
        # the program will exit on return
        # kill the FTP connection
        ftp_options.kill_ftp_connection(self.ftp_connection)
        self.kill_window()
        self.next_window = 'main_menu'
        
    def stop_pressed(self):
        # kills the backup transfer thread(not clean)
        if self.backup_session.isAlive():
            self.backup_session._stopped = True
        self.go_to_main_menu()
        
    def check_current_file(self):
        if self.backup_local.get_status() == "BACKINGUP":
            # if the backup process is still running, update the current file label 
            self.current_file.config(text=self.backup_local.get_current_file())
            self.master.after(1, self.check_current_file)
        elif self.backup_local.get_status() == "FINISHED":
            # if the process has finished  change the state of the buttons
            end_message = 'Finished.'
            if self.backup_local.get_failed_files():
                end_message += ' One or more files failed to transfer, see \'failed_files.txt\'.'
            self.current_file.config(text=end_message)
            self.stop_button_widget.config(state=DISABLED)
            self.done_button_widget.config(state=NORMAL)
        
    def start_backup(self):
        # this will start a thread to run the backup process
        self.backup_local = ftp_options.Backup(self.ftp_connection, self.config)
        self.backup_session = threading.Thread(target=self.backup_local.start_backup)
        self.backup_session.daemon = True
        self.backup_session.start()
        
from tkinter import Tk
import screens
import parse_settings

class App():
    """ Manages controls the program """
    def __init__(self):
        # start at the 'main_menu' screen
        self.next_window = 'main_menu'
        self.config = parse_settings.Settings_Parser()
        
    def run(self):
        # the main loop for the program, when the loop breaks the
        # program ends.
        program_finished = False
        while not program_finished:
            if self.next_window == 'main_menu':
                self.run_main_menu()
            if self.next_window == 'login':
                self.run_login()
            if self.next_window == 'backup':
                self.run_backup()
            else:
                # will exit the main loop
                program_finished = True
        
    # all the methods below are responsible for setting up and 
    # configuring individual screens.
    # -------start of individual screen configuration--------
    def run_main_menu(self):
        # Creates a main menu
        tMainMenu = Tk()
        tMainMenu.title("Homecloud Menu")
        tMainMenu.geometry("250x190")
        tMainMenu.resizable(0,0)
        m_menu = screens.Main_Menu(tMainMenu)
        m_menu.mainloop()
        self.check_next_window(m_menu)
        
    def run_login(self):
        # Creates a login screen for authentication to the FTP server
        tLogin = Tk()
        tLogin.title("Login to Homecloud")
        tLogin.geometry("250x160")
        tLogin.resizable(0,0)
        s_login = screens.Login(tLogin, self.config)
        s_login.mainloop()
        self.check_next_window(s_login)
        # retrieve the connection instance
        self.ftp_connection = s_login.get_ftp_connection()

    def run_backup(self):
        # Creates a screen to show backup progression
        tBackup = Tk()
        tBackup.title("Backup")
        tBackup.geometry("700x100")
        s_backup = screens.Backup(tBackup, self.ftp_connection, self.config)
        s_backup.mainloop()
        self.check_next_window(s_backup)
    
    # --------end of individual screen configuration---------
        
    def check_next_window(self, frame):
        # will get the name of the next screen to run
        self.next_window=frame.get_next_window()     

# initialise and run program
home_cloud = App()
home_cloud.run()
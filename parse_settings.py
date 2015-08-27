import configparser

CONFIG_FILE = 'config.cfg'
BACKUP_DIRS_FILE = 'backup_directories.txt'

class Settings_Parser():
    def __init__(self):
        self.file_location = CONFIG_FILE
        # Initialise configparser
        self.read_config()
        # Parse cfg file configuration
        self.parse_cfg_file()
        # Get list of directories to backup
        self.get_backup_dirs()

    def read_config(self):
        self.config = configparser.SafeConfigParser()
        self.config.read(self.file_location)
        
    def parse_cfg_file(self):
        # Parse settings section
        self.enable_sync = self.config.getboolean('Settings','enable_sync')
        # Parse defaults section
        self.ftp_ip = self.config.get('Defaults','ftp_server')
        
    def get_backup_dirs(self):
        # get list od directories to back up from a text file
        self.backup_dirs = [line.rstrip('\n') for line in open(BACKUP_DIRS_FILE)]
        for dir_count in range(0,len(self.backup_dirs)):
            print(self.backup_dirs[dir_count])
            self.backup_dirs[dir_count] = self.backup_dirs[dir_count].replace("\\","/")
        print(self.backup_dirs)

    def set_option(self, section, option, value):
        # FOR FUTURE USE, sets a new option to a cfg file
        self.read_config()
        self.config.set(section, option, value)
        self.write_config()

    def write_config(self):
        # FOR FUTURE USE, writes the new config options to the cfg file
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
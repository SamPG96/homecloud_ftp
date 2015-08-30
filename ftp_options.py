import ftplib
import datetime
import time
import os

def connect_to_ftp(ftp_ip, user, passw):
    # creates and returns a connection session to the FTP server
    ftp = None
    error = None
    try:
        ftp = ftplib.FTP(ftp_ip)
        ftp.login(user=user,passwd=passw)
    except Exception as e:
        error = e
    return ftp, error

def kill_ftp_connection(connection):
    # if the connection has timed out, catch the exception
    try:
        connection.quit()
    except (ftplib.error_temp, ConnectionAbortedError, TimeoutError):
        pass


class Backup():
    """ Runs the backup process by either syncing the local
        directories and the server directories or it can delete 
        the server directories entirely and do a whole transfer """

    def __init__(self, ftp_connection, config):
        self.ftp = ftp_connection
        self.config = config
        self.current_file = None
        self.failed_files = []
        self.failed_file = os.getcwd() + '/failed_files.txt'
        self.set_status("NOTHING")
        
    def start_backup(self):
        self.set_status("BACKINGUP")
        # empty failed_files.txt
        open(self.failed_file, 'w').close()
        # transfer each local directory defined in 'backup_directories.txt'
        for path in self.config.backup_dirs:
            if not os.path.isdir(path):
                raise Exception("local directory not found: %s" %path)
            dir_name = path.split("/")[-1]
            # if syning is disabled in the 'cfg' file and the directory already
            # exists in the server, then remove it
            if not self.config.enable_sync and dir_name in self.ftp.nlst():
                self.remove_ftp_directory(dir_name)
            # start directory transfer
            self.transfer_directory(path)
        self.set_status("FINISHED")

    def transfer_directory(self, path):
        os.chdir(path)
        files = os.listdir()
        directory = path.split("/")[-1]
        if not self.ftp_dir(directory):
            self.ftp.mkd(directory)
        self.ftp.cwd(directory)
        # work through each file/directory in the current local directory 
        for f in files:
            # set the path of the current item being backed up
            self.set_current_file(os.getcwd() + "\\" + f)
            if os.path.isfile(path + r'\{}'.format(f)) and self.config.enable_sync:
                # if syning is enabled and the current item in the local directory
                # is a file, then the following options are present
                if self.item_exists(f) and not self.update_file(f):
                    # if the local file already exists in the server directory and it has
                    # not been changed since it was uploaded to it then skip this item
                    continue
                elif self.item_exists(f) and self.update_file(f):
                    # if the local file already exists in the server directory and the local file
                    # has changed since it was uploaded then remove the server copy and replace it with
                    # the updated local file
                    self.ftp.delete(f)
                    # catch encode errors
                    try:
                        with open(f, 'rb') as fh:
                            self.ftp.storbinary('STOR %s' % f, fh)
                    except UnicodeEncodeError as e:
                        with open(self.failed_file, 'a') as f_files:
                            f_files.write('File:%s  Error:%s \n' %((path+'/'+f), e))
                        self.failed_files.append((path+'/'+f, e))
                elif not self.item_exists(f):
                    # if the local file does not exist in the server directory then upload it
                    # catch encode errors
                    try:
                        with open(f, 'rb') as fh:
                            self.ftp.storbinary('STOR %s' % f, fh)
                    except UnicodeEncodeError as e:
                        with open(self.failed_file, 'a') as f_files:
                            f_files.write('File: %s Error: %s \n' %((path+'/'+f), e))
                        self.failed_files.append((path+'/'+ f, e))
            elif os.path.isfile(path + r'\{}'.format(f)) and not self.config.enable_sync:
                # transfer the file
                # catch encode errors
                try:
                    with open(f, 'rb') as fh:
                        self.ftp.storbinary('STOR %s' % f, fh)
                except UnicodeEncodeError as e:
                    with open(self.failed_file, 'a') as f_files:
                        f_files.write('File: %s Error: %s \n' %((path+'/'+f), e))
                    self.failed_files.append((path+'/'+ f, e))
            elif os.path.isdir(path + r'\{}'.format(f)):
                # if the current item is a directory then recursively transfer all files inside it
                self.transfer_directory(path + '/' + f)
            # remove any files inside the server directory that are no longer in the local directory
            deleted_files = [file for file in self.ftp.nlst() if file not in files]
            for file in deleted_files:
                if self.ftp_dir(file):
                    self.remove_ftp_directory(file)
                else:
                    self.ftp.delete(file)
        self.ftp.cwd('..')
        os.chdir('..')
    
    def remove_ftp_directory(self, directory):
        # remove the contents of an FTP directory
        self.ftp.cwd(directory)
        files = self.ftp.nlst() 
        for f in files:
            if not self.ftp_dir(f):
                self.ftp.delete(f)
            elif self.ftp_dir(f):
                # if the item is a directory recursively delete its contents
                self.remove_ftp_directory(f)
        self.ftp.cwd('..')
        self.ftp.rmd(directory)  
        
    def ftp_dir(self, directory):
        # checks if the current item is a directory or a file
        if not self.item_exists(directory):
            # check if the item name exists in the server directory
            return False
        try:
            return self.ftp.size(directory) is None
        except ftplib.error_perm:
            return True
        
    def item_exists(self, file):
        # checks if an item exists in the server directory
        file_list = self.ftp.nlst()
        if file in file_list:
            return True
        else:
            return False
        
    def set_current_file(self, file):
        # sets the path of the file being backed up
        self.current_file = file
        
    def set_status(self, status):
        # sets current backup status, it can be either:
        #    Nothing has started yet  - NOTHING
        #    In process of backing up - BACKINGUP
        #    Finished backing up      - FINISHED
        #    There has been an error  - ERROR(<error_message>)
        if status.startswith("ERROR(") and status.endswith(")"):
            self.status = status
        elif status in ["NOTHING","BACKINGUP","FINISHED"]:
            self.status = status
        else:
            raise Exception("Invalid status choice: %s" %status)
        
    def get_status(self):
        # return backup status
        return self.status

    def get_failed_files(self):
        # return dailed files
        return self.failed_files
        
    def get_current_file(self):
        # returns the file being backed up
        return self.current_file
        
    def update_file(self, file):
        # checks if the local file has been modified since it was last uploaded to the server
        ftp_mod_dt = self.ftp.sendcmd('MDTM %s' %file)
        ftp_year = int(ftp_mod_dt[4:8])
        ftp_month = int(ftp_mod_dt[8:10])
        ftp_day = int(ftp_mod_dt[10:12])
        ftp_mod_date = datetime.datetime.strptime('%s %s %s' %(ftp_year,ftp_month,ftp_day), '%Y %m %d')
        ftp_hour = ftp_mod_dt[12:14]
        ftp_minute = ftp_mod_dt[14:16]
        ftp_second = ftp_mod_dt[16:18]
        ftp_mod_time = datetime.datetime.strptime('%s:%s:%s' %(ftp_hour,ftp_minute,ftp_second), '%H:%M:%S')
        local_mod_dt = time.ctime(os.path.getmtime(file)).split()
        local_mod_dt[1] = time.strptime(local_mod_dt[1],'%b').tm_mon
        local_mod_date = datetime.datetime.strptime('%s %s %s' %(local_mod_dt[4],local_mod_dt[1],local_mod_dt[2]), '%Y %m %d')
        local_mod_time = datetime.datetime.strptime('%s' %local_mod_dt[3], '%H:%M:%S')
        if local_mod_date.date() > ftp_mod_date.date():
            return True
        elif local_mod_date.date() < ftp_mod_date.date():
            return False
        if local_mod_time.time() > ftp_mod_time.time():
            return True
        elif local_mod_time.time() < ftp_mod_time.time():
            return False
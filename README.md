#Homecloud FTP

##Introduction:
I wanted a script that would sync my local directories with the directories on my FTP server
and didn't want to satisfy dependencies such as 'rsync' with 'ssh' or 'lftp' with 'ftp'.
This is because the machine I developed and tested on ran Windows 7 and satisfying these
dependencies would involve a complex installation script and assumed knowledge.
I produced a simple algorithm as part of this script to sync the directories manually, which
requires no dependencies to be satisfied.
A graphical interface is provided for ease of use and monitoring so that anyone of any
skill set can use this the program without a problem.
The object oriented structure of this script allows for easy development and expansion.

##Prerequisites:
  - Python 3.3 (has only been tested on this version)
  - The connected server is running FTP. In my case using 'vsftpd'.
  - A user account has been set up that is accessible by FTP.
  - The FTP user account has write/delete privileges.
Note: At the moment all local directories will be sync/added to the root directory of
	  the FTP user account.

##Download and install
  1. Pull down git the repository 'https://github.com/sammypg/homecloud_ftp.git'

##How to use:
  1. Set a default address for the FTP server in 'config.cfg'.
     This can be changed manually in the login screen.
  2. Decide to either sync your local directories with the FTP directories
     or to overwrite what is already on the server.
     By default sync is enabled, to disable this change the option 'enable_sync'
     to false in 'config.cfg'.
  3. List the local directories you want backed up by declaring there absolute paths
     line by line in 'backup_directories.txt'.
     Ensure there are no unwanted white spaces at the end of each line.
     See the text file for examples(delete the examples before running).
  4. Run the 'homecloud.py' script and select the 'Backup' option.
  5. If you entered an address for the FTP server you are connecting to in the 'config.cfg'
     then it should appear in the first box.
     You can change this as a one of here.
  6. Enter the user name and password to start an FTP session with the server and press
     the 'Start' button.
  7. The backup process will now begin and the window will tell you what is currently being
     backed up.
     Once this process has finished the 'Done' button will become active and you
     can exit the screen.
     The process can be stopped at any time by selecting the 'Stop' button.

##Build for Windows
To build homecloud_ftp into an '_.exe_' file for windows do the following(ensure py2exe
package for python is installed):
  1. Open the '_setup.py_' file in '_homecloud_ftp_' and check the annotation for more details.
  2. Open CMD as administrator.
  3. Go into the 'homecloud_ftp' directory.
  4. Run the following command:
         _Python setup.py py2exe_
     Or if Python is not in your '_PATH_' then replace '_Python_' with the path to the Python
     executable file, for example '_C:\Python33\python.exe_'
  5. A new directory in 'homecloud_ftp' should of been created called '_dist_', which
     holds the '_homecloud.exe_' file.

##Ideas for the future:
  - Add restore functionality.
  - Allow all configuration options to be changed in the GUI.
  - More useful on screen statistics during backup process, such as time left till completion.
  - Add logging.
  - Securely store user name and password.
  - Support for defining the FTP server root directory to sync local directories to.

 ##Known bugs
  - An encoding error appears rarely when trying to send a file to the FTP server, the error is:
    "UnicodeEncodeError: Error: 'latin-1' codec can't encode character '\u2013' in position 11: ordinal not in range(256)",
    I am unsure to why this is happening, what I do know is that it is not down to the format of the file
    because I can still successfully send files with the same format type as the failed files.
    As a temporary measure in a previous commit I am catching this this error and writing to a file
    the list of files that failed to send.
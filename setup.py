# For building homecloud_ftp on windows

from distutils.core import setup
import py2exe

# Define where you want homecloud to be built to below
build_dir =
data_files = [('',['config.cfg',
                   'backup_directories.txt',
                   'README.md'])]

options = {'py2exe': {
                      'dist_dir': build_dir}}
setup(
      windows=['homecloud.py'],
      data_files=data_files,
      options=options)
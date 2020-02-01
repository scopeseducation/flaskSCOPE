#!/usr/bin/python
import tarfile
import os
import time
import datetime
import sys
import glob

#function to create tar.gz
def tardir(path, tar_name):
   with tarfile.open(tar_name, "w:gz") as tar_handle:
      for root, dirs, files in os.walk(path):
         for file in files:
            #arcname parameter prevents directory structure to be saved
            tar_handle.add(os.path.join(root, file), arcname=file)
      tar_handle.close()

#prepare a timestamp - mainly to avoid caching of files from browser
#also to help user identify the file

#get folder from command line
if len(sys.argv) < 2:
   exit('give folder as command line argument')
else:
   folder = sys.argv[1].rstrip()

dt = datetime.datetime.now()
timeStamp = dt.strftime("%y%b%d%H%M")

try:
   #remove old tar files if something went wrong
   fileList = glob.glob(folder + '/static/images/images.*.tar.gz')
   for filePath in fileList:
      os.remove(filePath)

   #wrapper for preparing a tarball of imagefolder
   #folders hardcoded for now
   tardir(folder + '/static/images', folder + '/static/images/images.' + timeStamp + '.tar.gz')

   #looks like the process ended successfully
   f = open(folder + "/logs/status.txt", "w+")
   f.write("container_ready")
   f.close()

   #looks like the process ended successfully
   f = open('/media/ramdisk/status.txt', 'w+')
   f.write("container_ready")
   f.close()


except:
   #record exception
   error = sys.exec_info()[0]
   f = open(folder + "/logs/error.txt", "a+")
   f.write("error during tarball creation\n")
   f.write(error)
   f.close()

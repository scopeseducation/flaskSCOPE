#!/usr/bin/python
import tarfile
import os
import time
import glob
import sys

#get folder from command line
if len(sys.argv) < 2:
   exit('give folder as command line argument')
else:
   folder = sys.argv[1].rstrip()

#wrapper for deleting all files in the imagefolder
#folders hardcoded for now
try:
   fileList = glob.glob(folder + '/static/images/image*')
   for filePath in fileList:
      os.remove(filePath)

   #logs are appended to have a record on errors
   f = open(folder + "/logs/status.txt", "w+")
   f.write("idle")
   f.close()

   f = open('/media/ramdisk/status.txt', 'w+')
   f.write("idle")
   f.close()

except:
   #record exception
   error = sys.exec_info()[0]
   #logs are appended to have a record on errors
   f = open(folder + "/logs/error.txt", "a+")
   f.write("error during image removal\n")
   f.write(error)
   f.close()

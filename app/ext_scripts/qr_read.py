#!/usr/bin/python3

#tests camera input for the presence of a QR code 
#if a file was linekd to this code a file is updated in ramdisk
#works with FlaskScope
#needs python3 to read camera input into numpy array

from PIL import Image
from time import sleep
from pyzbar.pyzbar import decode
#import picamera

import blinkt
import os
import time
#import numpy as np

def show_color_line(r,g,b,t):
    blinkt.set_brightness(0.5)
    for i in range(0,8):
        blinkt.set_pixel(i, r, g, b)
        blinkt.show()
        time.sleep(t)

def show_color(r,g,b):
    blinkt.set_brightness(0.5)
    for i in range(0,8):
        blinkt.set_pixel(i, r, g, b)
    blinkt.show()

#current information is found here:
current_file = "/media/ramdisk/qr_current.txt"

QR2file={}
code_list=[]

#read config file - links the QR code to the command
config_file = "/media/ramdisk/qr_config.txt"
cf = open(config_file,'r')
cf_lines = cf.readlines()
cf.close()

for line in cf_lines:
    line = line.replace('\n', '')
    parts = line.split("\t")
    #file to display - for html and movie the actual file, for image the index
    QR2file[parts[1]] = parts[0]
    code_list.append(parts[1])

old_id = ""

#initialise QR code container
QR_id = ""
old_QR_id = QR_id

cont = 1
#do infinite cycle
while cont == 1:
   #capture image - uses raspbians raspistill for this task
   os.system('raspistill -w 320 -h 240 -t 1 -o /media/ramdisk/qr_image.png > /media/ramdisk/qr_image.out')

   #decode all QR codes in the image
   qrcodes = decode(Image.open('/media/ramdisk/qr_image.png'))

   #check if any detected code is registered for a task
   #if more than 1 valid code is detected - the last analysed one is used
   for qrcode in qrcodes:
      code=qrcode.data.decode("utf-8")

      #indicate that a new QR code was detected
      if old_QR_id != code:
         show_color(255,255,0)
         time.sleep(1)
         blinkt.clear()
         blinkt.show()
         old_QR_id = code

         if code in code_list:
            #save oldID
            old_QR_id = QR_id
            QR_id = code
            #valid code detected
            show_color_line(0,255,0,0)
            time.sleep(1)
            blinkt.clear()
            blinkt.show()

         else:
            show_color_line(255,0,0,0)
            time.sleep(1)
            blinkt.clear()
            blinkt.show()

      #save info for for image to be displayed
      if old_QR_id != QR_id and code in code_list:
         f = open(current_file,'w+')
         f.write("current_file\t" + QR2file[QR_id])
         f.close()
      else:
         show_color_line(255,0,0,0)
         time.sleep(1)
         blinkt.clear()
         blinkt.show()

   #check if stop file exists
   if (os.path.exists('/media/ramdisk/qr_code.stop')):
      cont = 0

   sleep(1.5)


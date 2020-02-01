#!/usr/bin/python3

#tests camera input for the presence of a QR code
#3 QR codes need to be present in the image
#if the final stitched to the concatenated QR-codes
#an output is updated to be displayed
#works with FlaskScope

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
current_file = "/media/ramdisk/seq_current.txt"

QR2file={}
code_list=[]

#read config file - links the final sequence code to the file
config_file = "/media/ramdisk/seq_config.txt"
cf = open(config_file,'r')
cf_lines = cf.readlines()
cf.close()

for line in cf_lines:
    line = line.replace('\n', '')
    parts = line.split("\t")
    QR2file[parts[1]] = parts[0]
    #record all QR codes to check if a legible code was given
    code_list.append(parts[1])

old_id = ""

#initialise QR code container
QR_id = ""
old_QR_id = QR_id

cont = 1

#container for the final code
final_code = ''

#do infinite cycle
while cont == 1:
   #capture image - uses raspbians raspistill for this task
   os.system('raspistill -w 640 -h 480 -t 1 -o /media/ramdisk/qr_image.png > /media/ramdisk/qr_image.out')

   #decode all QR codes in the image
   qrcodes = decode(Image.open('/media/ramdisk/qr_image.png'))

   #check if any detected code is registered for a task
   #if more than 1 valid code is detected - the last analysed one is used
   if len(qrcodes) == 3:
      final_code_list = []
      for qrcode in qrcodes:
         code=qrcode.data.decode("utf-8")
         final_code_list.append(code)

      #sort the QR codes to make sure the 
      #filename is concatenated correctly
      final_code_list.sort()
      final_code = final_code_list[0] + final_code_list[1] + final_code_list[2]

      #indicate that three QR codes were detected
      show_color(255,255,0)

      time.sleep(1)
      blinkt.clear()
      blinkt.show()

      print (final_code)

      if final_code in code_list:
         #save oldID
         old_QR_id = QR_id
         QR_id = final_code
         #valid code detected
         show_color_line(0,255,0,0)
         time.sleep(1)
         blinkt.clear()
         blinkt.show()

         #save info for for image to be displayed
         if old_QR_id != QR_id:
            f = open(current_file,'w+')
            f.write("current_file\t" + QR2file[QR_id])
            f.close()
         else:
            show_color_line(255,0,0,0)
            time.sleep(1)
            blinkt.clear()
            blinkt.show()

      else:
         show_color_line(255,0,0,0)
         time.sleep(1)
         blinkt.clear()
         blinkt.show()
         #report invalid sequence
         f = open(current_file,'w+')
         f.write("current_file\tseqscope/no_valid_seq.jpg")
         f.close()
         old_QR_id = ''

   #check if stop file exists - same for DisplayScope and this
   if (os.path.exists('/media/ramdisk/qr_code.stop')):
      cont = 0

   sleep(1.5)


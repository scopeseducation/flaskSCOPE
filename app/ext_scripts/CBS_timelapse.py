#!/usr/bin/python3

#timelapse script - simple wrapper for blinkt and image taking (python)

#blinkt library
import blinkt
import os
import glob
from time import sleep
from datetime import datetime
from picamera import PiCamera
import sys

#get folder from command line
if len(sys.argv) < 2:
   exit('give folder as command line argument')
else:
   folder = sys.argv[1].rstrip()


#add leading zeros to a number - useful for sorting 
def add_zeros(value):
    out = ""
    str_len = len(str(value))
    for i in range(1, 5-str_len):
        out = out + "0"
    out = out + str(value)
    return (out)

cycles = 0
image_n = 0
abort = 0 

#from setup file
f = open("/media/ramdisk/tl_setup.config.txt", "r")
line = f.readline()
f.close()

parameters = line.split('\'')

for i in [1,5,9,13]:
    if parameters[i] == 'interval':
        image_cycle = int(parameters[i+2])
    if parameters[i] == 'green':
        g = int(parameters[i+2])
    if parameters[i] == 'red':
        r = int(parameters[i+2])
    if parameters[i] == 'yellow':
        b = int(parameters[i+2])

print(image_cycle, r, g, b)

#write a 0 to a file in ramdisk and run until this changes
f = open("/media/ramdisk/abort_signal", "w")
f.write("0")
f.close()

camera = PiCamera()

while abort == 0:
    print (cycles, image_cycle)

    #take image
    if cycles == image_cycle:
        #turn light on
        blinkt.set_all(r, g, b, 0.1)
        blinkt.show()

        prefix = add_zeros(image_n)
        #os.system("raspistill -t 1 -o /var/www/FlaskApp/Scopes_CBS/Pictures/image" + prefix +".jpg")

        camera.capture(folder + "/static/images/image." + prefix +".jpg")

        #turn light off
        blinkt.set_all(0, 0, 0)
        blinkt.show()

        image_n += 1
        cycles = 0

    #increment cycle
    cycles += 1
    #wait 1 sec
    sleep(1)
    #read file to check whether an abort was requested
    f = open("/media/ramdisk/abort_signal", "r")
    abort = int(f.read(1))

    f.close()

#turn lights off
blinkt.set_all(0, 0, 0)
blinkt.show()

#read current status - mainly to get starting time
#f = open(folder + "/logs/status.txt", "r")
#status_lines = f.read()
#f.close()

#write out status of proper status with starting time
#f = open(folder + "/logs/status.txt", "w")
#status_lines = status_lines.split("\n")
#status_lines[0] = "t_finished"
#f.write('\n'.join(status_lines))
#f.close()


from pyzbar.pyzbar import decode
import time
import picamera
import numpy as np
from PIL import Image
import os

ramdisk = '/media/ramdisk'

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 24
    time.sleep(2)
    output = np.empty((480, 640, 3), dtype=np.uint8)
    
    cont = 1
    qr2file = {}
    
    #read config file
    f = open(os.path.join(ramdisk, "run_mode.txt"), "r")
    #fill in conversion table
    status = f.read()
    f.close()

    
    while (cont==1):
        camera.capture(output, 'rgb')

        # Convert array to Image
        img = Image.fromarray(output)

        qrcodes = decode(img)

        for qrcode in qrcodes:
            print(qrcode.data.decode("utf-8"))

        time.sleep(1)
        
        f = open(os.path.join(ramdisk, "run_mode.txt"), "r")
        status = f.read()
        f.close()
        
        if not status == 'DisplayScope':
            cont = 0


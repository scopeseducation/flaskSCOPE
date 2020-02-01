#!/bin/bash

#installs flaskSCOPE

# check if script runs as sudo
if [[ $EUID > 0 ]]
    then echo "Please run as root"
    exit
fi

#test if camera has been already enabled
s=$(/opt/vc/bin/vcgencmd get_camera)
sb="supported=1 detected=1"
case $sb in
    $s)
    echo "Camera detected"
  ;;
    *)
    echo "Camera not detected please enable camera using raspi-config first"
    exit
  ;;
esac

#test if script is run in the installation folder
if [[ ! -f "./run_at_startup.sh" ]]
     then echo "Please run the script from within the installation folder"
    exit
fi

echo do you want to set-up FlaskScope on this Pi?
read -p "y/n? " -n 1 -r
echo    # (optional) move to a new line

if [[ $REPLY =~ ^[Yy]$ ]]
then
    #install necessary packages
    #not all are absolutely necessary - todo: remove unnecessary packages

    apt-get install python3-dev -y
    apt-get install libjpeg-dev -y
    apt-get install zlib1g-dev -y
    apt-get install libfreetype6-dev -y
    apt-get install liblcms1-dev -y
    apt-get install libopenjp2-7 -y
    apt-get install libtiff5 -y
    apt-get install python3-picamera -y
    apt-get install python3-pip -y
    apt-get install libzbar0 -y
    apt-get install python3-venv -y

    pip3 install flask flask_sqlalchemy flask_migrate flask_login flask_wtf pillow blinkt pyzbar

    #for full blinkt install
    #curl https://get.pimoroni.com/blinkt | bash

    #create ramdisk to avoid heavy read/write access on sd card
    mkdir /media/ramdisk
    echo "tmpfs /media/ramdisk tmpfs nodev,nosuid,size=10M 0 0" >> /etc/fstab
    mount -a

    #change hostname
    sed -i 's/raspberrypi/flaskscope/' /etc/hosts
    sed -i 's/raspberrypi/flaskscope/' /etc/hostname

    #start flaskscope at each boot so add to rc.local
    #NOTE: this runs flask as root
    
    #NOTE: do this before the 'exit 0' line
    #therefore remove the 'exit 0' line first
    sed -i 's/exit 0//' /etc/rc.local
    echo "$PWD/run_at_startup.sh &" >> /etc/rc.local
    #write the exit 0 back
    echo exit 0 >> /etc/rc.local

    #write current folder to startup script
    #NOTE the comma version of sed to work with the slashes in the folder!
    sed -i "s,dir2change,$PWD,g" run_at_startup.sh

    #set permissions to execute helperscripts
    chmod -R a+rx $PWD/app/ext_scripts
    chmod a+rx $PWD/run_at_startup.sh
    
    #compile mini program to gracefully shut down the Pi
    #this construct also works if not run by sudo 
    #for example if flask is run from apache or nginx server
    gcc -o flask_sd flask_sd.c
    #copy to convenient location and change ownership, group, permissions
    cp flask_sd /bin/.
    chown root /bin/flask_sd
    chgrp root /bin/flask_sd
    chmod 6755 /bin/flask_sd

fi

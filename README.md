**FlaskScope** is a collection of Python scripts.

FlaskSCOPE provides the web interface to interact with our SCOPES didactic device using the microframework Flask (https://www.fullstackpython.com/flask.html).
FlaskSCOPE also provides scripts operate ChronobioScope, DNAscope and DisplaySCOPE (for details see https://scopeseducation.org/).

FlaskSCOPE is designed to operate on a Raspberry Pi Zero W and as a simple install option we will provide a pre-configured image on our webpage https://scopeseducation.org/downloads/ soon.

For instruction on how to copy this image to an SD card we recommend the official tutorial: https://www.raspberrypi.org/documentation/installation/installing-images/README.md.

**NOTE:** if you want to use multiple SCOPES within the same area you have to give a distinct ssid to each SCOPE. Details on how to customise the Raspberry Pi access point are found here: https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

**Installing flaskSCOPE from scratch**

Prepare an SD card with the latest Raspbian operating system following the instruction from: https://www.raspberrypi.org/downloads/raspbian/

We used stretch-lite with timestamp 2019-04-08

On the Raspberry Pi do the following (you need access to the internet):

Follow this tutorial to activate the Pi camera, which includes doing the obligatory updates:
https://www.raspberrypi.org/documentation/configuration/camera.md

Install GIT and clone our github repository

    sudo apt-get install git
    git clone https://github.com/scopeseducation/flaskSCOPE.git

We provide an installer script which has to be run as sudo

    cd flaskSCOPE
    chmod +x install.sh
    sudo ./install.sh

Finally configure the Pi to be a wireless access point.
We provide an installer script that has to be run as sudo.

CARE: after this, you will ***NOT*** be able to connect to the internet via WIFI!

    chmod +x ap_install.sh
    sudo ./ap_install.sh

Comments and pull requests welcome.

For more information on SCOPES visit our website:
https://scopeseducation.org

#!/bin/bash
#access point setup
#gives the PI this static IP: 192.168.4.1 
#if you want to change this modify: dhcpcd.conf.add and dnsmasq.conf

#two variables can be given: [AP name] [AP password]
#defaults to: FlaskScope flaskscope

#based on this tutorial: https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

#give default values
APname=${1:-FlaskScope}
APpass=${2:-flaskscope}

# check if script runs as sudo
if [[ $EUID > 0 ]]
  then echo "Please run as root"
  exit
fi

#check if necessary folder is present
#test if script is run in the installation folder
if [[ ! -d "./AP_setup" ]]
     then echo "Please run the script from within the installation folder"
    exit
fi

echo do you want to set-up a wifi access point?
echo your pi will not be connected to your local wifi any more!

read -p "y/n? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    #TODO: prepare a log file and test if all of them are accessible from current path

    echo setting up AP with name: $APname and password: $APpass
    
    #change placeholder with actual values
    #TODO: this fails at special characters - improve to allow for this

    sed -r "s/APname/$APname/" ./AP_setup/hostapd.conf > ./AP_setup/hostapd.conf.mod
    sed -r -i "s/APpass/$APpass/" ./AP_setup/hostapd.conf.mod

    apt-get install dnsmasq hostapd -y
    systemctl stop dnsmasq
    systemctl stop hostapd

    cat AP_setup/dhcpcd.conf.add >> /etc/dhcpcd.conf

    mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

    cp AP_setup/dnsmasq.conf /etc/dnsmasq.conf

    systemctl reload dnsmasq

    cp AP_setup/hostapd.conf.mod /etc/hostapd/hostapd.conf

    sed -r -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd\.conf"/' /etc/default/hostapd

    systemctl unmask hostapd
    systemctl enable hostapd
    systemctl start hostapd

    sed -i -r 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

    iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
    sh -c "iptables-save > /etc/iptables.ipv4.nat"
    iptables-restore < /etc/iptables.ipv4.nat
fi

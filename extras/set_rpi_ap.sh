#!/bin/bash

: << 'COMMENT'
Download and run :
wget https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/set_rpi_ap.sh -O set_rpi_ap.sh
sudo chmod a+x set_rpi_ap.sh
sudo ./set_rpi_ap.sh

Default access point name and password : [RPi, rpi_ap_pwd]
Default RPi IP : 192.168.4.1
Default DHCP IP range : 192.168.4.2 to 20
COMMENT


function validate_url(){
  if [[ `wget_proxy -S --spider $1  2>&1 | grep 'HTTP/1.1 200 OK'` ]]; then
    return 0
  else
    return 1
  fi
}

function add_line_if_not_exist(){
  grep -qF "$1" "$2"  || echo "$1" | sudo tee --append "$2"
}

function pip3_proxy(){
  if [[ "$answer_proxy" == "n" ]]; then
    sudo pip3 $*
  else
    echo "pip3 using" $answer_proxy "for" $* > /dev/tty
    sudo pip3 --proxy=$answer_proxy $*
  fi
}

function pip3_proxy_not_rust(){
  if [[ "$answer_proxy" == "n" ]]; then
    sudo CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip3 install cryptography==3.4.6 --no-cache-dir
    sudo pip3 $*
  else
    echo "pip3 using" $answer_proxy "for" $* > /dev/tty
    sudo CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip3 --proxy=$answer_proxy install cryptography==3.4.6 --no-cache-dir
    sudo pip3 --proxy=$answer_proxy $*
  fi
}

function apt_proxy(){
  if [[ "$answer_proxy" == "n" ]]; then
    sudo apt-get $*
  else
    echo "apt using" $answer_proxy "for" $* > /dev/tty
    sudo "http_proxy=$answer_proxy" apt-get $*
  fi
}

function wget_proxy(){
  if [[ "$answer_proxy" == "n" ]]; then
    echo "wget no proxy" $* > /dev/tty
    sudo wget --no-proxy $*
  else
    echo "wget using" $answer_proxy "for" $* > /dev/tty
    sudo http_proxy=$answer_proxy https_proxy=$answer_proxy ftp_proxy=$answer_proxy wget $*
  fi
}

echo 'date :'
echo $(date)
read -p "Is the date correct ? [y/n]: " answer_date
if [[ "$answer_date" == "n" ]]; then
  exit
fi

read -p "Use proxy ? [http://proxy:port or n]: " answer_proxy



# Upgrade RPi
apt_proxy update
apt_proxy -y upgrade

# Install AP and Management Software
apt_proxy install hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
apt_proxy install dnsmasq
sudo DEBIAN_FRONTEND=noninteractive apt_proxy -y netfilter-persistent iptables-persistent

# Set up the Network Router
# Define the Wireless Interface IP Configuration
sudo mv /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
sudo echo "interface wlan0" >> /etc/dhcpcd.conf
sudo echo "    static ip_address=192.168.4.1/24" >> /etc/dhcpcd.conf
sudo echo "    nohook wpa_supplicant" >> /etc/dhcpcd.conf

# Enable Routing and IP Masquerading
sudo mv //etc/sysctl.d/routed-ap.conf /etc/sysctl.d/routed-ap.conf.orig
sudo echo "# Enable IPv4 routing" > /etc/sysctl.d/routed-ap.conf
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.d/routed-ap.conf

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo netfilter-persistent save

# Configure the DHCP and DNS services for the wireless network
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo echo "interface=wlan0 # Listening interface" >> /etc/dnsmasq.conf
sudo echo "dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" >> /etc/dnsmasq.conf
sudo echo "                # Pool of IP addresses served via DHCP" >> /etc/dnsmasq.conf
sudo echo "domain=wlan     # Local wireless DNS domain" >> /etc/dnsmasq.conf
sudo echo "address=/gw.wlan/192.168.4.1" >> /etc/dnsmasq.conf
sudo echo "                # Alias for this router" >> /etc/dnsmasq.conf

# Ensure Wireless Operation
sudo rfkill unblock wlan

# Configure the AP Software
sudo mv /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.orig
sudo echo "country_code=FR" > /etc/hostapd/hostapd.conf
sudo echo "interface=wlan0" >> /etc/hostapd/hostapd.conf
sudo echo "ssid=RPi" >> /etc/hostapd/hostapd.conf
sudo echo "hw_mode=g" >> /etc/hostapd/hostapd.conf
sudo echo "channel=7" >> /etc/hostapd/hostapd.conf
sudo echo "macaddr_acl=0" >> /etc/hostapd/hostapd.conf
sudo echo "auth_algs=1" >> /etc/hostapd/hostapd.conf
sudo echo "ignore_broadcast_ssid=0" >> /etc/hostapd/hostapd.conf
sudo echo "wpa=2" >> /etc/hostapd/hostapd.conf
sudo echo "wpa_passphrase=rpi_ap_pwd" >> /etc/hostapd/hostapd.conf
sudo echo "wpa_key_mgmt=WPA-PSK" >> /etc/hostapd/hostapd.conf
sudo echo "wpa_pairwise=TKIP" >> /etc/hostapd/hostapd.conf
sudo echo "rsn_pairwise=CCMP" >> /etc/hostapd/hostapd.conf

echo "
Default access point name and password : [RPi, rpi_ap_pwd]
Default RPi IP : 192.168.4.1
Default DHCP IP range : 192.168.4.2 to 20
Reboot the device to activate."

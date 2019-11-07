#!/bin/bash

function validate_url(){
  if [[ `wget -S --spider $1  2>&1 | grep 'HTTP/1.1 200 OK'` ]]; then
    return 0
  else
    return 1
  fi
}

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install mariadb-server python3-mysqldb
sudo apt-get install -y python3-pip libhdf5-100 libhdf5-dev python3-dev nginx

sudo pip3 install gunicorn pyserial docutils cffi Cython numpy lxml pyvisa pyvisa-py
sudo pip3 install https://github.com/clavay/PyScada/tarball/hmi_tmp
sudo apt-get -y install owfs
sudo pip3 install pyownet
sudo apt-get -y install libffi-dev
sudo pip3 install smbus-cffi
sudo pip3 install psutil
sudo pip3 install pyusb gpiozero https://github.com/clavay/PyScada-Laborem/tarball/master https://github.com/trombastic/PyScada-GPIO/tarball/master https://github.com/trombastic/PyScada-Scripting/tarball/master

#CAS
sudo apt-get -y install libxml2-dev libxslt-dev python-dev
sudo pip3 install --upgrade https://github.com/clavay/django-cas-ng/tarball/clavay-proxy
sudo pip3 install --upgrade https://github.com/clavay/python-cas/tarball/clavay-proxy

#Create pyscada user
sudo useradd -r pyscada
sudo mkdir -p /var/www/pyscada/http
sudo chown -R pyscada:pyscada /var/www/pyscada
sudo mkdir -p /home/pyscada
sudo chown -R pyscada:pyscada /home/pyscada

sudo chmod a+w /var/log

#Add rights for usb, i2c and serial
echo 'SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="pyscada"' | sudo tee -a /etc/udev/rules.d/10-usb.rules
echo 'KERNEL=="ttyS[0-9]", GROUP="dialout", MODE="0777"' | sudo tee -a /etc/udev/rules.d/10-usb.rules
sudo usermod -a -G pyscada www-data
sudo usermod -a -G dialout pyscada
sudo adduser pyscada i2c

#Mjpeg-streamer
cd ~
url='https://github.com/jacksonliam/mjpg-streamer/archive/master.zip'
if `validate_url $url >/dev/null`; then
    wget $url
    sudo apt-get -y install cmake libjpeg62-turbo-dev
    unzip mjpg-streamer-master.zip
    cd mjpg-streamer-experimental/
    make
    sudo make install
    sudo usermod -a -G video pyscada
    sudo wget https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/service/systemd/laborem_camera.service -O /etc/systemd/system/laborem_camera.service
    sudo systemctl enable laborem_camera
    sudo systemctl start laborem_camera;
else echo $url "does not exist"; fi

#create DB
sudo mysql -uroot -p -e "CREATE DATABASE PyScada_db CHARACTER SET utf8;GRANT ALL PRIVILEGES ON PyScada_db.* TO 'PyScada-user'@'localhost' IDENTIFIED BY 'PyScada-user-password';"

cd /var/www/pyscada/
sudo -u pyscada django-admin startproject PyScadaServer

# TODO : Copy settings.py
echo "You need to configure settings.py (look at https://pyscada.readthedocs.io/en/master/django_settings.html#settings-py)"
url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/dev/0.7.x/extras/urls.py'
if `validate_url $url >/dev/null`; then
    sudo wget $url -O /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py
else echo $url "does not exist"; fi

#Migration and static files
cd /var/www/pyscada/PyScadaServer # linux
sudo -u pyscada python3 manage.py migrate
sudo -u pyscada python3 manage.py collectstatic --noinput

# load fixtures with default configuration for chart lin colors and units
sudo -u pyscada python3 manage.py loaddata color
sudo -u pyscada python3 manage.py loaddata units

# initialize the background service system of pyscada
sudo -u pyscada python3 manage.py pyscada_daemon init

cd /var/www/pyscada/PyScadaServer
sudo -u pyscada python3 manage.py createsuperuser

# Nginx
url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/dev/0.7.x/extras/nginx_sample.conf'
if `validate_url $url >/dev/null`; then
    sudo wget $url -O /etc/nginx/sites-available/pyscada.conf
    sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default
    sudo mkdir /etc/nginx/ssl
    # the certificate will be valid for 5 Years,
    sudo openssl req -x509 -nodes -days 1780 -newkey rsa:2048 -keyout /etc/nginx/ssl/pyscada_server.key -out /etc/nginx/ssl/pyscada_server.crt
    sudo systemctl enable nginx.service # enable autostart on boot
    sudo systemctl restart nginx
else echo $url "does not exist"; fi

# Gunicorn and PyScada
url='https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.socket'
if `validate_url $url >/dev/null`; then
    sudo wget $url -O /etc/systemd/system/gunicorn.socket
else echo $url "does not exist"; fi

url='https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.service'
if `validate_url $url >/dev/null`; then
    sudo wget $url -O /etc/systemd/system/gunicorn.service
else echo $url "does not exist"; fi

url='https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_daemon.service'
if `validate_url $url >/dev/null`; then
    sudo wget $url -O /etc/systemd/system/pyscada.service
else echo $url "does not exist"; fi


# enable the services for autostart
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl enable pyscada
sudo systemctl start pyscada
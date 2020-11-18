#!/bin/bash

function validate_url(){
  if [[ `wget -S --spider $1  2>&1 | grep 'HTTP/1.1 200 OK'` ]]; then
    return 0
  else
    return 1
  fi
}

read -p "Update only (don't create db, user, copy services, settings and urls...) ? [y/n]: " answer_update
read -p "Install PyScada clavay fork ? [y/n]: " answer_pyscada
read -p "Install PyScada-Laborem ? [y/n]: " answer_laborem
read -p "Install PyScada-GPIO ? [y/n]: " answer_gpio
read -p "Install PyScada-Scripting ? [y/n]: " answer_scripting
read -p "Install PyScada-Serial ? [y/n]: " answer_serial
read -p "Install PyScada-WebService ? [y/n]: " answer_webservice
if [[ "$answer_laborem" == "y" ]]; then
  read -p "Install CAS ? [y/n]: " answer_cas
  read -p "Install mjpeg-streamer ? [y/n]: " answer_mjpeg
  read -p "Install PiCamera ? [y/n]: " answer_picamera
else
  answer_cas = "n"
  answer_mjpeg = "n"
  answer_picamera = "n"
fi

echo "Stopping PyScada"
sudo systemctl stop pyscada gunicorn gunicorn.socket
echo "PyScada stopped"

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install mariadb-server python3-mysqldb
sudo apt-get install -y python3-pip libhdf5-103 libhdf5-dev python3-dev nginx libffi-dev
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libopenjp2-7
sudo pip3 install gunicorn pyserial docutils cffi Cython numpy lxml pyvisa pyvisa-py

if [[ "$answer_pyscada" == "y" ]]; then
  sudo pip3 install --upgrade https://github.com/clavay/PyScada/tarball/master
else
  sudo pip3 install --upgrade https://github.com/trombastic/PyScada/tarball/master
fi

sudo apt-get -y install owfs
sudo pip3 install pyownet
sudo pip3 install smbus-cffi
sudo pip3 install psutil
sudo pip3 install pyusb gpiozero

if [[ "$answer_laborem" == "y" ]]; then
  sudo pip3 install --upgrade https://github.com/clavay/PyScada-Laborem/tarball/master
fi
if [[ "$answer_gpio" == "y" ]]; then
  sudo pip3 install --upgrade https://github.com/clavay/PyScada-GPIO/tarball/master
fi
if [[ "$answer_scripting" == "y" ]]; then
  sudo pip3 install --upgrade https://github.com/clavay/PyScada-Scripting/tarball/master
fi
if [[ "$answer_serial" == "y" ]]; then
  sudo pip3 install --upgrade https://github.com/clavay/PyScada-Serial/tarball/master
fi
if [[ "$answer_webservice" == "y" ]]; then
  sudo pip3 install --upgrade https://github.com/clavay/PyScada-WebService/tarball/master
fi
sudo pip3 install --upgrade mysqlclient

#CAS
if [[ "$answer_cas" == "y" ]]; then
  sudo apt-get -y install libxml2-dev libxslt-dev python-dev
  sudo pip3 install --upgrade https://github.com/clavay/django-cas-ng/tarball/clavay-proxy
  sudo pip3 install --upgrade https://github.com/clavay/python-cas/tarball/clavay-proxy
fi

if [[ "$answer_update" == "n" ]]; then
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
  sudo adduser pyscada gpio
fi

#Mjpeg-streamer
if [[ "$answer_mjpeg" == "y" ]]; then
  cd ~
  url='https://github.com/jacksonliam/mjpg-streamer/archive/master.zip'
  if `validate_url $url >/dev/null`; then
      wget $url
      sudo apt-get -y install cmake libjpeg62-turbo-dev
      unzip master.zip
      rm master.zip
      cd mjpg-streamer-master/mjpg-streamer-experimental/
      make
      sudo make install
      cd ../..
      sudo rm -r mjpg-streamer-master
      sudo usermod -a -G video pyscada
      sudo wget https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/service/systemd/laborem_camera.service -O /etc/systemd/system/laborem_camera.service
      sudo systemctl enable laborem_camera
      sudo systemctl restart laborem_camera;
  else echo $url "does not exist"; exit 1; fi
fi

if [[ "$answer_picamera" == "y" ]]; then
  sudo pip3 install --upgrade picamera
  echo 'SUBSYSTEM=="vchiq",MODE="0666", GROUP="pyscada"' | sudo tee -a /etc/udev/rules.d/99-camera.rules
fi

if [[ "$answer_update" == "n" ]]; then

  #create DB
  sudo mysql -uroot -p -e "CREATE DATABASE PyScada_db CHARACTER SET utf8;GRANT ALL PRIVILEGES ON PyScada_db.* TO 'PyScada-user'@'localhost' IDENTIFIED BY 'PyScada-user-password';"

  cd /var/www/pyscada/
  sudo -u pyscada django-admin startproject PyScadaServer

  #Copy settings.py and urls.py
  cd /var/www/pyscada/PyScadaServer/PyScadaServer # linux
  var1=$(grep SECRET_KEY settings.py)
  echo $var1
  printf -v var2 '%q' "$var1"
  url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/settings.py'
  if `validate_url $url >/dev/null`; then
      sudo wget $url -O /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py
  else echo $url "does not exist"; exit 1; fi
  sudo sed -i "s/SECRET_KEY.*/$var2/g" settings.py

  url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/urls.py'
  if `validate_url $url >/dev/null`; then
      sudo wget $url -O /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py
  else echo $url "does not exist"; exit 1; fi
fi

#Migration and static files
cd /var/www/pyscada/PyScadaServer # linux
sudo -u pyscada python3 manage.py migrate
sudo -u pyscada python3 manage.py collectstatic --noinput

# load fixtures with default configuration for chart lin colors and units
sudo -u pyscada python3 manage.py loaddata color
sudo -u pyscada python3 manage.py loaddata units

# initialize the background service system of pyscada
sudo -u pyscada python3 manage.py pyscada_daemon init

if [[ "$answer_update" == "n" ]]; then

  cd /var/www/pyscada/PyScadaServer
  sudo -u pyscada python3 manage.py createsuperuser

  # Nginx
  url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/nginx_sample.conf'
  if `validate_url $url >/dev/null`; then
      sudo wget $url -O /etc/nginx/sites-available/pyscada.conf
      sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/
      sudo rm /etc/nginx/sites-enabled/default
      sudo mkdir /etc/nginx/ssl
      # the certificate will be valid for 5 Years,
      sudo openssl req -x509 -nodes -days 1780 -newkey rsa:2048 -keyout /etc/nginx/ssl/pyscada_server.key -out /etc/nginx/ssl/pyscada_server.crt
      sudo systemctl enable nginx.service # enable autostart on boot
      sudo systemctl restart nginx
  else echo $url "does not exist"; exit 1; fi

  # Gunicorn and PyScada
  url='https://raw.githubusercontent.com/trombastic/PyScada/master/extras/service/systemd/gunicorn.socket'
  if `validate_url $url >/dev/null`; then
      sudo wget $url -O /etc/systemd/system/gunicorn.socket
  else echo $url "does not exist"; exit 1; fi

  url='https://raw.githubusercontent.com/trombastic/PyScada/master/extras/service/systemd/gunicorn.service'
  if `validate_url $url >/dev/null`; then
      sudo wget $url -O /etc/systemd/system/gunicorn.service
  else echo $url "does not exist"; exit 1; fi

  url='https://raw.githubusercontent.com/clavay/PyScada/master/extras/service/systemd/pyscada_daemon.service'
  if `validate_url $url >/dev/null`; then
      sudo wget $url -O /etc/systemd/system/pyscada.service
  else echo $url "does not exist"; exit 1; fi
fi

# enable the services for autostart
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn
sudo systemctl enable pyscada
sudo systemctl restart pyscada

if [[ "$answer_update" == "n" ]]; then
  echo "PyScada installed"
else
  echo "PyScada updated"
fi
if [[ "$answer_picamera" == "y" ]]; then
  echo "Activate pi camera with sudo raspi-config"
fi
if [[ "$answer_laborem" == "y" ]]; then
  echo "Activate serial with sudo raspi-config"
fi
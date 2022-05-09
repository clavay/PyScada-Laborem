#!/bin/bash
download_version=$'Download the new version \n
wget https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/install.sh -O install.sh \n
or wget https://s.42l.fr/pyscada -O install.sh \n
sudo chmod a+x install.sh \n
sudo ./install.sh'

version=8

echo "Local version" $version

# todo : add inputs for mysql root pwd, db name, username, user pwd

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

read -p "Use proxy ? [http://proxy:port or n]: " answer_proxy

# Check if the actual version is lower than the remote
remote_version=$(wget_proxy -qO- https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/install.sh | sed -n 's/^version=\(.*\)/\1/p')
echo "Remote version" $remote_version

if ! [[ "$remote_version" =~ ^[0-9]+$ ]]
then
  echo "Very old remote version :" $remote_version
  exit
elif [ $version -ge $remote_version ] 2>/dev/null
then
 echo "Version check ok";
else
  echo "Old local version :" $remote_version
  echo "$download_version"
  exit
fi

echo 'date :'
echo $(date)
read -p "Is the date correct ? [y/n]: " answer_date
if [[ "$answer_date" == "n" ]]; then
  exit
fi

apt_proxy update
apt_proxy -y upgrade
apt_proxy install -y python3-pip
echo 'Some python3 packages installed:'
echo "$(pip3 list | grep -i -E 'pyscada|channels|asgiref')"

read -p "Update only (don't create db, user, copy services, settings and urls...) ? [y/n]: " answer_update
read -p "Install PyScada clavay fork ? [y/n]: " answer_pyscada
read -p "Install PyScada-Laborem ? [y/n]: " answer_laborem
read -p "Install PyScada-GPIO ? [y/n]: " answer_gpio
read -p "Install PyScada-Scripting ? [y/n]: " answer_scripting
read -p "Install PyScada-Serial ? [y/n]: " answer_serial
read -p "Install PyScada-WebService ? [y/n]: " answer_webservice
read -p "Install PyScada-BACnet ? [y/n]: " answer_bacnet
read -p "Install channels and redis ? [y/n]: " answer_channels

if [[ "$answer_update" == "n" ]]; then
  read -p "DB name ? [PyScada_db]: " answer_db_name
fi
if [[ "$answer_db_name" == "" ]]; then
  answer_db_name="PyScada_db"
fi
echo $answer_db_name

if [[ "$answer_laborem" == "y" ]]; then
  read -p "Install CAS ? [y/n]: " answer_cas
  read -p "Install mjpeg-streamer ? [y/n]: " answer_mjpeg
  read -p "Install PiCamera ? [y/n]: " answer_picamera
else
  answer_cas="n"
  answer_mjpeg="n"
  answer_picamera="n"
fi

echo "Stopping PyScada"
sudo systemctl stop pyscada gunicorn gunicorn.socket
echo "PyScada stopped"

apt_proxy -y install mariadb-server python3-mysqldb
apt_proxy install -y python3-pip libhdf5-103 libhdf5-dev python3-dev nginx libffi-dev zlib1g-dev libjpeg-dev
apt_proxy install -y libatlas-base-dev
apt_proxy install -y libopenjp2-7
pip3_proxy install gunicorn pyserial docutils cffi Cython numpy lxml pyvisa pyvisa-py

if [[ "$answer_pyscada" == "y" ]]; then
  pip3_proxy install --upgrade https://github.com/clavay/PyScada/tarball/master
else
  pip3_proxy install --upgrade https://github.com/pyscada/PyScada/tarball/master
fi

apt_proxy -y install owfs
pip3_proxy install pyownet
pip3_proxy install smbus-cffi
pip3_proxy install psutil
pip3_proxy install pyusb gpiozero

if [[ "$answer_laborem" == "y" ]]; then
  pip3_proxy install --upgrade https://github.com/clavay/PyScada-Laborem/tarball/master
fi
if [[ "$answer_gpio" == "y" ]]; then
  pip3_proxy install --upgrade https://github.com/clavay/PyScada-GPIO/tarball/master
fi
if [[ "$answer_scripting" == "y" ]]; then
  pip3_proxy install --upgrade https://github.com/clavay/PyScada-Scripting/tarball/master
fi
if [[ "$answer_serial" == "y" ]]; then
  pip3_proxy install --upgrade https://github.com/clavay/PyScada-Serial/tarball/master
fi
if [[ "$answer_webservice" == "y" ]]; then
  pip3_proxy install --upgrade https://github.com/clavay/PyScada-WebService/tarball/master
fi
if [[ "$answer_bacnet" == "y" ]]; then
  pip3_proxy install --upgrade https://github.com/clavay/PyScada-BACnet/tarball/master
fi
if [[ "$answer_channels" == "y" ]]; then
  apt_proxy -y install redis-server
  if grep -R "Raspberry Pi 3"  "/proc/device-tree/model" ; then
    echo "Don't install Rust for RPI3"
    pip3_proxy_not_rust install --upgrade channels channels-redis asgiref
  else
    #pip3_proxy install cryptography==3.4.6
    pip3_proxy install --upgrade cryptography==3.4.6 channels channels-redis asgiref
  fi
fi

apt_proxy install -y libmariadb-dev
pip3_proxy install --upgrade mysqlclient

#CAS
if [[ "$answer_cas" == "y" ]]; then
  apt_proxy -y install libxml2-dev libxslt-dev python-dev
  pip3_proxy install --upgrade https://github.com/clavay/django-cas-ng/tarball/clavay-proxy
  pip3_proxy install --upgrade https://github.com/clavay/python-cas/tarball/clavay-proxy
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
  #echo 'SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="pyscada"' | sudo tee -a /etc/udev/rules.d/10-usb.rules
  #echo 'KERNEL=="ttyS[0-9]", GROUP="dialout", MODE="0777"' | sudo tee -a /etc/udev/rules.d/10-usb.rules
  add_line_if_not_exist 'SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="pyscada"' /etc/udev/rules.d/10-usb.rules
  add_line_if_not_exist 'KERNEL=="ttyS[0-9]", GROUP="dialout", MODE="0777"' /etc/udev/rules.d/10-usb.rules
  sudo usermod -a -G pyscada www-data
  sudo usermod -a -G dialout pyscada
  sudo adduser pyscada i2c
  if [[ "$answer_gpio" == "y" ]]; then
    sudo adduser pyscada gpio
  fi
fi

#Mjpeg-streamer
if [[ "$answer_mjpeg" == "y" ]]; then
  cd ~
  url='https://github.com/jacksonliam/mjpg-streamer/archive/master.zip'
  if `validate_url $url >/dev/null`; then
      wget_proxy $url
      apt_proxy -y install cmake libjpeg62-turbo-dev
      unzip master.zip
      rm master.zip
      cd mjpg-streamer-master/mjpg-streamer-experimental/
      make
      sudo make install
      cd ../..
      sudo rm -r mjpg-streamer-master
      sudo usermod -a -G video pyscada
      wget_proxy https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/service/systemd/laborem_camera.service -O /etc/systemd/system/laborem_camera.service
      sudo systemctl enable laborem_camera
      sudo systemctl restart laborem_camera;
  else echo $url "does not exist"; exit 1; fi
fi

if [[ "$answer_picamera" == "y" ]]; then
  pip3_proxy install --upgrade picamera
  #echo 'SUBSYSTEM=="vchiq",MODE="0666", GROUP="pyscada"' | sudo tee -a /etc/udev/rules.d/99-camera.rules
  add_line_if_not_exist 'SUBSYSTEM=="vchiq",MODE="0666", GROUP="pyscada"' /etc/udev/rules.d/99-camera.rules
fi

if [[ "$answer_update" == "n" ]]; then

  #create DB
  sudo mysql -e "CREATE DATABASE ${answer_db_name} CHARACTER SET utf8;GRANT ALL PRIVILEGES ON ${answer_db_name}.* TO 'PyScada-user'@'localhost' IDENTIFIED BY 'PyScada-user-password';"

  cd /var/www/pyscada/
  sudo -u pyscada django-admin startproject PyScadaServer

  #Copy settings.py and urls.py
  cd /var/www/pyscada/PyScadaServer/PyScadaServer # linux
  var1=$(grep SECRET_KEY settings.py)
  echo $var1
  printf -v var2 '%q' "$var1"
  url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/settings.py'
  if `validate_url $url >/dev/null`; then
      wget_proxy $url -O /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py
  else echo $url "does not exist"; exit 1; fi
  sudo sed -i "s/SECRET_KEY.*/$var2/g" settings.py
  sudo sed -i "s/PyScada_db'/${answer_db_name}'/g" settings.py

  url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/urls.py'
  if `validate_url $url >/dev/null`; then
      wget_proxy $url -O /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py
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
  #sudo -u pyscada python3 manage.py createsuperuser
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('pyscada', 'admin@myproject.com', 'password')" | python3 manage.py shell

  # Nginx
  url='https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/nginx_sample.conf'
  if `validate_url $url >/dev/null`; then
      wget_proxy $url -O /etc/nginx/sites-available/pyscada.conf
      sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/
      sudo rm /etc/nginx/sites-enabled/default
      sudo mkdir /etc/nginx/ssl
      # the certificate will be valid for 5 Years,
      sudo openssl req -x509 -nodes -days 1780 -newkey rsa:2048 -keyout /etc/nginx/ssl/pyscada_server.key -out /etc/nginx/ssl/pyscada_server.crt
      sudo systemctl enable nginx.service # enable autostart on boot
      sudo systemctl restart nginx
  else echo $url "does not exist"; exit 1; fi

  # Gunicorn and PyScada
  url='https://raw.githubusercontent.com/pyscada/PyScada/master/extras/service/systemd/gunicorn.socket'
  if `validate_url $url >/dev/null`; then
      wget_proxy $url -O /etc/systemd/system/gunicorn.socket
  else echo $url "does not exist"; exit 1; fi

  url='https://raw.githubusercontent.com/pyscada/PyScada/master/extras/service/systemd/gunicorn.service'
  if `validate_url $url >/dev/null`; then
      wget_proxy $url -O /etc/systemd/system/gunicorn.service
  else echo $url "does not exist"; exit 1; fi

  url='https://raw.githubusercontent.com/clavay/PyScada/master/extras/service/systemd/pyscada_daemon.service'
  if `validate_url $url >/dev/null`; then
      wget_proxy $url -O /etc/systemd/system/pyscada.service
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
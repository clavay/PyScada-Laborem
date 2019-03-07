PyScada-Laborem
==================================

Laborem extension to PyScada

What is Working
---------------

 - nothing is test


What is not Working/Missing
---------------------------

 - Test with real hardware
 - Documentation

Installation
------------

 - sudo apt-get update
 - sudo apt-get -y upgrade
 - sudo apt-get install python3-pip
 - If behind a proxy pre-install dependencies : sudo pip3 install cffi Cython numpy lxml docutils
 - Install PyScada : https://pyscada.readthedocs.io/en/dev-0.7.x/installation.html
 - Change : sudo pip3 install https://github.com/trombastic/PyScada/archive/dev/0.7.x.zip
    to : sudo pip3 install https://github.com/clavay/PyScada/tarball/hmi
 - Install pyusb : sudo pip3 install pyusb
 - Install gpiozero : sudo pip3 install gpiozero
 - Install PyScada-Laborem : sudo pip3 install https://github.com/clavay/PyScada-Laborem/tarball/master
 - Install PyScada-GPIO : sudo pip3 install pyscada-gpio
 - Install PyScada-Scripting : sudo pip3 install pyscada-scripting
 - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py before url(r'^', include('pyscada.hmi.urls')), :
    - url(r'^', include('pyscada.laborem.urls')),

 - Add pyscada and gpio apps in /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py :
    INSTALLED_APPS = [
        ...
        'pyscada.laborem',
        'pyscada.gpio',

    ]
 - Add access to USB devices for pyscada user :
    Add in /etc/udev/rules.d/10-usb.rules : SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="pyscada"
    sudo usermod -a -G pyscada www-data
 - Add access to serial devices for pyscada user :
    Add : KERNEL=="ttyS[0-9]", GROUP="dialout", MODE="0777"
    sudo usermod -a -G dialout pyscada
 - Add access to I2C for pyscada user :
    sudo adduser pyscada i2c

To use CAS auth
---------------

 - sudo apt-get install libxml2-dev libxslt-dev python-dev

 Without proxy :
  - sudo pip3 install django_cas_ng
  - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py :

   INSTALLED_APPS = [
    - ...
    - 'django_cas_ng',

   ]

   AUTHENTICATION_BACKENDS = [
    - 'django.contrib.auth.backends.ModelBackend',
    - 'django_cas_ng.backends.CASBackend',

   ]

   CAS_SERVER_URL = 'https://account.example.com/cas/'

  - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py :

   - import django_cas_ng.views
   - url(r'^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
   - url(r'^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
   - url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),

 Behind a proxy for CAS V2 :
  - sudo pip3 install --upgrade https://github.com/clavay/django-cas-ng/tarball/clavay-proxy
  - sudo pip3 install --upgrade https://github.com/clavay/python-cas/tarball/clavay-proxy
  - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py :

   INSTALLED_APPS = [
    - ...
    - 'django_cas_ng',

   ]

   AUTHENTICATION_BACKENDS = [
    - 'django.contrib.auth.backends.ModelBackend',
    - 'django_cas_ng.backends.CASBackend',

   ]

   CAS_SERVER_URL = 'https://account.example.com/cas/'
   CAS_VERSION = '2'
   CAS_EXTRA_LOGIN_KWARGS = {'proxies': {'https': 'http://proxy.com:3128'}, 'timeout': 5}

  - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py :

   - import django_cas_ng.views
   - url(r'^accounts/CASlogin/$', django_cas_ng.views.login, name='cas_ng_login'),
   - url(r'^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
   - url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),

 - sudo /var/www/pyscada/PyScadaServer/manage.py migrate

To add a USB camera
-------------------


 Install mjpg-streamer :
     - Edit /etc/nginx/sites-available/pyscada.conf and add before "location /" :
         location /camera/ {
             proxy_pass http://127.0.0.1:8090/;

         }
     - Download : https://github.com/jacksonliam/mjpg-streamer
     - sudo apt-get install cmake libjpeg62-turbo-dev
     - unzip mjpg-streamer-master.zip
     - cd mjpg-streamer-experimental/
     - make
     - sudo make install
     - sudo usermod -a -G video pyscada
     - sudo wget https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/service/systemd/laborem_camera.service -O /etc/systemd/system/laborem_camera.service
     - sudo systemctl enable laborem_camera
     - sudo systemctl start laborem_camera
     - add to a custom html :
         <img id='camera-img' src="http://" + window.location.hostname + "/camera/?action=stream" onerror="this.src='{% static 'pyscada/laborem/img/webcam-offline.jpg' %}'" width="320px" height="240px" alt="Camera view">


To use less the SD card on a Raspberry Pi
-----------------------------------------

 - You will loose everything in /tmp, /var/tmp, /var/log after each reboot !
 - Move /tamp, /var/tmp and /var/log to memory :
     - sudo nano /etc/rc.local
         Add before "exit 0" :
            - chmod a+w /var/log
            - mkdir /var/log/nginx
            - chmod a+w /var/log/nginx
            - echo >> /var/log/pyscada_debug.log
            - chmod a+w /var/log/pyscada_debug.log
            - # If you want to copy the DB on RAM at start from your save
            - rsync -av /var/lib/mysql_to_restore/mysql /tmp
            - chown -R mysql:mysql /tmp/mysql
     - sudo nano /etc/fstab
         Add at the end :
            - tmpfs    /var/log    tmpfs    defaults,noatime,nosuid,mode=0755,size=50m    0 0
            - tmpfs   /tmp    tmpfs   defaults,noatime,mode=1777,size=350m
            - tmpfs   /var/tmp    tmpfs   defaults,noatime,mode=1777,size=30m
 - Remove swap (included in the "Read-only root filesystem"):
     - sudo swapoff --all
     - sudo apt-get remove dphys-swapfile
 - (In test !!!) Move mysql to RAM at boot and save it before shutdown or each day :
     - sudo systemctl stop nginx gunicorn gunicorn.socket pyscada mysql
     - wait for mysql to shutdown...
     - sudo rsync -av /var/lib/mysql /tmp
     - sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
          - change datadir=/var/lib/mysql
          - to datadir=/tmp/mysql
     - sudo systemctl start mysql nginx gunicorn pyscada
 - Read-only root filesystem for Raspbian Stretch (using overlay) :
     - https://github.com/JasperE84/root-ro

Contribute
----------

 - Issue Tracker: https://github.com/clavay/PyScada-Laborem/issues
 - Source Code: https://github.com/clavay/PyScada-Laborem


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.-

PyScada-LaboREM
==================================

LaboREM extension to PyScada

What is Working
---------------

 - nothing is test


What is not Working/Missing
---------------------------

 - Test with real hardware
 - Documentation

Installation
------------

 - Install PyScada : https://pyscada.readthedocs.io/en/dev-0.7.x/installation.html
 - Change : sudo pip install https://github.com/trombastic/PyScada/archive/dev/0.7.x.zip
    to : sudo pip install https://github.com/clavay/PyScada/tarball/hmi
 - Install pyusb : sudo pip install pyusb
 - Install gpiozero : sudo pip install gpiozero
 - Install PyScada-LaboREM : sudo pip install https://github.com/clavay/PyScada-LaboREM/tarball/master
 - Install PyScada-GPIO : sudo pip install pyscada-gpio
 - Install PyScada-Scripting : sudo pip install pyscada-scripting
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
  - sudo pip install django_cas_ng
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

   url(r'^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
   url(r'^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
   url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),

 Behind a proxy for CAS V2 :
  - sudo pip install --upgrade https://github.com/clavay/django-cas-ng/tarball/clavay-proxy
  - sudo pip install --upgrade https://github.com/clavay/python-cas/tarball/clavay-proxy
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
     - Download : https://github.com/jacksonliam/mjpg-streamer
     - sudo apt-get install cmake libjpeg62-turbo-dev
     - unzip mjpg-streamer-master.zip
     - cd mjpg-streamer-experimental/
     - make
     - sudo make install
     - sudo usermod -a -G video pyscada
     - sudo wget https://raw.githubusercontent.com/clavay/PyScada-LaboREM/master/extras/service/systemd/laborem_camera.service -O /etc/systemd/system/laborem_camera.service
     - sudo systemctl enable laborem_camera
     - sudo systemctl start laborem_camera
     - add to a custom html :
         <img id='camera-img' src="http://" + window.location.hostname + ":8090/?action=stream" onerror="this.src='{% static 'pyscada/laborem/img/webcam-offline.jpg' %}'" width="320px" height="240px" alt="Camera view">

Contribute
----------

 - Issue Tracker: https://github.com/clavay/PyScada-LaboREM/issues
 - Source Code: https://github.com/clavay/PyScada-laboREM


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.-

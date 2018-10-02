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
       to : sudo pip install https://github.com/clavay/PyScada/archive/dev/0.7.x.zip
 - Install dev version of pyvisa-py : pip install https://github.com/pyvisa/pyvisa-py/tarball/master
 - Install pyusb : sudo pip install pyusb
 - Install gpiozero : sudo pip install gpiozero
 - Install PyScada-LaboREM : sudo pip install https://github.com/clavay/PyScada-LaboREM/tarball/master
 - Install PyScada-GPIO : sudo pip install pyscada-gpio
 - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py : url(r'^', include('pyscada.laborem.urls')),
 - Add pyscada and gpio apps in /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py :
    INSTALLED_APPS = [
    ...
        'pyscada.laborem',
        'pyscada.gpio',
    ]

To use CAS auth
---------------

Without proxy :
 - sudo pip install django_cas_ng
 - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py :
    INSTALLED_APPS = [
    ...
        'django_cas_ng',
    ]

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
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
    ...
        'django_cas_ng',
    ]

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    ]

    CAS_SERVER_URL = 'https://account.example.com/cas/'
    CAS_VERSION = '2'
    CAS_EXTRA_LOGIN_KWARGS = {'proxies': {'https': 'http://proxy.com:3128'}, 'timeout': 5}
 - Add in /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py :
    url(r'^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
    url(r'^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),

sudo /var/www/pyscada/PyScadaServer/manage.py migrate

To add a USB camera
-------------------

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
 - add to a custom html : <img src="http://127.0.0.1:8090/?action=stream" width="320px" height="240px" />

Contribute
----------

 - Issue Tracker: https://github.com/clavay/PyScada-LaboREM/issues
 - Source Code: https://github.com/clavay/PyScada-laboREM


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.-

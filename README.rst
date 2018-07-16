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
 - Change : pip install https://github.com/trombastic/PyScada/archive/dev/0.7.x.zip
       to : pip install https://github.com/clavay/PyScada/archive/dev/0.7.x.zip
 - Install dev version of pyvisa-py : pip install https://github.com/pyvisa/pyvisa-py/tarball/master
 - Install pyusb : pip install pyusb
 - Install gpiozero : pip install gpiozero
 - Install PyScada-LaboREM : pip install https://github.com/clavay/PyScada-LaboREM/tarball/master
 - Install PyScada-GPIO : pip install pyscada-gpio
 - In /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py add : url(r'^', include('pyscada.laborem.urls')),
 - Add pyscada and gpio apps in /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py :
    INSTALLED_APPS = [
    ...
        'pyscada.laborem',
        'pyscada.gpio',
    ]

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

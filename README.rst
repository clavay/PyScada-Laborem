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
 - Install PyScada-LaboREM : pip install https://github.com/clavay/PyScada-LaboREM/tarball/master
 - Install PyScada-GPIO : pip install pyscada-gpio
 - In /var/www/pyscada/PyScadaServer/PyScadaServer/urls.py add : url(r'^', include('pyscada.laborem.urls')),
 - Add pyscada and gpio apps in /var/www/pyscada/PyScadaServer/PyScadaServer/settings.py :
    INSTALLED_APPS = [
    ...
        'pyscada.laborem',
        'pyscada.gpio',
    ]

Contribute
----------

 - Issue Tracker: https://github.com/clavay/PyScada-LaboREM/issues
 - Source Code: https://github.com/clavay/PyScada-laboREM


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.-

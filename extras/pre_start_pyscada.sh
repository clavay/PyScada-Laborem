#!/bin/bash

backuppath=/home/pyscada/nextcloud/export_laborem_iut_rpi3

#/bin/mount /home/pyscada/nextcloud
if /usr/bin/python3 /var/www/pyscada/PyScadaServer/manage.py loaddata ${backuppath}/core.json ; then
    echo "Loaddata core success"
else
    echo "Loaddata core failed"
fi
#/bin/umount /home/pyscada/nextcloud
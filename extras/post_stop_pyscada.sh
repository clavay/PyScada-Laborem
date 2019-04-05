#!/bin/bash

time_stamp=$(date +%Y_%m_%d_%H_%M_%S)
backuppath=/home/pyscada/nextcloud/export_laborem_iut_X

#/bin/mount /home/pyscada/nextcloud
/bin/mkdir -p ${backuppath}
/usr/bin/python3 /var/www/pyscada/PyScadaServer/manage.py dumpdata --exclude pyscada.recordeddata --exclude pyscada.devicewritetask --exclude auth.permission --exclude contenttypes > ${backuppath}/core.json
/usr/bin/python3 /var/www/pyscada/PyScadaServer/manage.py dumpdata --exclude pyscada.recordeddata --exclude pyscada.devicewritetask --exclude auth.permission --exclude contenttypes > ${backuppath}/core_${time_stamp}.json
/usr/bin/python3 /var/www/pyscada/PyScadaServer/manage.py dumpdata pyscada.recordeddata --exclude pyscada.devicewritetask --exclude auth.permission --exclude contenttypes > ${backuppath}/recorded_data_${time_stamp}.json
#/bin/umount /home/pyscada/nextcloud
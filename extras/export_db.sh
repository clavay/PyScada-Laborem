#!/bin/bash
currentDate=`date +"%Y-%m-%d@%H-%M-%S"`
#echo $currentDate
output='lite_db_'${currentDate}'.json'
echo $output
python3 /var/www/pyscada/PyScadaServer/manage.py dumpdata --exclude pyscada.mail --exclude auth.user --exclude sessions --exclude auth.permission --exclude contenttypes --exclude admin --exclude pyscada.RecordedData --exclude pyscada.RecordedDataOld --exclude pyscada.DeviceWriteTask --exclude pyscada.DeviceReadTask > ${output}

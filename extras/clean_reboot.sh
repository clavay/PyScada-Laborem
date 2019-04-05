#!/bin/bash

systemctl stop gunicorn gunicorn.socket
systemctl stop nginx
systemctl stop pyscada
umount /home/pyscada/nextcloud
systemctl stop mysql
/sbin/shutdown -r +1

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
get the json from elogs parse and save it to the db
"""

from pyscada.models import Variable

import requests
from django.conf import settings
import ipaddress
import logging

logger = logging.getLogger(__name__)


def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """
    pass


def shutdown(self):
    """
    write your code shutdown code here, don't change the name of this function
    :return:
    """
    pass


def script(self):
    """
    write your code loop code here, don't change the name of this function
    :return:
    """
    # Get the proxies from setting.py
    proxies = {}
    #if hasattr(settings, 'PROXIES'):
    #    if 'http' in settings.PROXIES:
    #        proxies['http'] = settings.PROXIES['http']
    #    if 'https' in settings.PROXIES:
    #        proxies['https'] = settings.PROXIES['https']

    # ip = '10.3.208.166'
    # device = '1380030161'
    # variable = '1864662904'

    for v in Variable.objects.all():
        ip = ""
        if len(v.description.split(";")) >= 2:
            variable = v.description.split(";")[1]
            device = v.description.split(";")[0]
            if len(v.description.split(";")) == 3:
                val_init = v.description.split(";")[2]
            else:
                val_init = 0.0
            ip = v.device.description
        else:
            # logger.debug('variable description length < 2 : %s' % v.description)
            continue
        try:
            ipaddress.ip_address(ip)
            url = 'http://' + ip + '/rest/devices/' + device + '/values/variables/' + variable + '/instant'
            resp = requests.get(url=url, proxies=proxies)

            if resp.status_code == 200:
                time = resp.json()['time']
                value = resp.json()['value']
                unit = resp.json()['unit']
                value = float(value) - float(val_init)
                logger.debug('%s - %s - %s - %s - %s - %s - %s - %s - %s' %
                             (v, ip, device, variable, value, time, value, unit, v.unit))
                self.write_values_to_db(data={v: [float(value)], 'timevalues': [float(time)]})
            else:
                logger.debug('request status_code wrong : %s - %s - %s - %s' % (resp.status_code, ip, device, variable))
        except ValueError:
            # logger.debug('IP address not valid : %s - %s - %s' % (ip, device, variable))
            pass

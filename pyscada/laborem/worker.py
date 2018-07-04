#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseDAQProcess
from pyscada.models import BackgroundProcess
from pyscada.laborem.models import LaboremMotherboardDevice
from pyscada.laborem import PROTOCOL_ID


import json
import logging

logger = logging.getLogger(__name__)


class Process(BaseDAQProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
        self.LABOREM_PROCESSES = []

    def init_process(self):

        # clean up
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).delete()

        grouped_ids = {}
        for item in LaboremMotherboardDevice.objects.filter(laboremmotherboard_device__active=True):
            if item.protocol == PROTOCOL_ID:  # LABOREM IP
                # every device gets its own process
                grouped_ids['%d-%s:%s-%d'
                            % (item.laboremmotherboard_device.pk, item.ip_address, item.port, item.unit_id)] = [item]
                continue

            # every port gets its own process
            if item.port not in grouped_ids:
                grouped_ids[item.port] = []
            grouped_ids[item.port].append(item)

        for key, values in grouped_ids.items():
            bp = BackgroundProcess(label='pyscada.laborem-%s' % key,
                                   message='waiting..',
                                   enabled=True,
                                   parent_process_id=self.process_id,
                                   process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                   process_class_kwargs=json.dumps(
                                       {'device_ids': [i.laboremmotherboard_device.pk for i in values]}))
            bp.save()
            self.LABOREM_PROCESSES.append({'id': bp.id,
                                           'key': key,
                                           'device_ids': [i.laboremmotherboard_device.pk for i in values],
                                           'failed': 0})

    def loop(self):
        """
        
        """
        # check if all laborem processes are running
        for laborem_process in self.LABOREM_PROCESSES:
            try:
                BackgroundProcess.objects.get(pk=laborem_process['id'])
            except BackgroundProcess.DoesNotExist or BackgroundProcess.MultipleObjectsReturned:
                # Process is dead, spawn new instance
                if laborem_process['failed'] < 3:
                    bp = BackgroundProcess(label='pyscada.laborem-%s' % laborem_process['key'],
                                           message='waiting..',
                                           enabled=True,
                                           parent_process_id=self.process_id,
                                           process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                           process_class_kwargs=json.dumps(
                                               {'device_ids': laborem_process['device_ids']}))
                    bp.save()
                    laborem_process['id'] = bp.id
                    laborem_process['failed'] += 1
                else:
                    logger.debug('process pyscada.laborem-%s failed more then 3 times' % laborem_process['key'])

        return 1, None

    def cleanup(self):
        # todo cleanup
        pass

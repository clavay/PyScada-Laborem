#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseDAQProcess
from pyscada.models import BackgroundProcess
from pyscada.laborem.models import LaboremMotherboardDevice, LaboremGroupInputPermission
from pyscada.models import Variable, VariableProperty
from django.contrib.auth.models import Group

import json
import traceback
import logging

logger = logging.getLogger(__name__)


class Process(BaseDAQProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
        self.LABOREM_PROCESSES = []

    def init_process(self):

        # clean up
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).delete()

        for item in LaboremMotherboardDevice.objects.filter(laboremmotherboard_device__active=True):
            # every device gets its own process
            bp = BackgroundProcess(label='pyscada.laborem-%s' % item.id,
                                   message='waiting..',
                                   enabled=True,
                                   parent_process_id=self.process_id,
                                   process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                   process_class_kwargs=json.dumps(
                                       {'device_id': item.laboremmotherboard_device.pk}))
            bp.save()
            self.LABOREM_PROCESSES.append({'id': bp.id,
                                           'key': item.id,
                                           'device_id': item.laboremmotherboard_device.pk,
                                           'failed': 0})

        # Create the 3 groups needed by Laborem and filling the permissions
        v = Group.objects.get_or_create(name="viewer")[0]
        w = Group.objects.get_or_create(name="worker")[0]
        t = Group.objects.get_or_create(name="teacher")[0]
        lv = LaboremGroupInputPermission.objects.get_or_create(hmi_group=v)[0]
        lw = LaboremGroupInputPermission.objects.get_or_create(hmi_group=w)[0]
        lt = LaboremGroupInputPermission.objects.get_or_create(hmi_group=t)[0]
        for var in Variable.objects.all():
            lw.variables.add(var)
            lt.variables.add(var)
        for vp in VariableProperty.objects.all():
            lw.variable_properties.add(vp)
            lt.variable_properties.add(vp)
        try:
            lw.laborem_motherboard_device.add(LaboremMotherboardDevice.objects.first())
            lt.laborem_motherboard_device.add(LaboremMotherboardDevice.objects.first())
        except Exception:
            logger.error("Laborem Starting : No LaboremMotherBoardDevice")
        lw.move_robot = True
        lt.move_robot = True
        lw.top10_answer = True
        lt.top10_answer = True
        lw.save()
        lt.save()

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
                                               {'device_id': laborem_process['device_id']}))
                    bp.save()
                    laborem_process['id'] = bp.id
                    laborem_process['failed'] += 1
                else:
                    logger.debug('process pyscada.laborem-%s failed more than 3 times' % laborem_process['key'])

        return 1, None

    def cleanup(self):
        # todo cleanup
        pass

    def restart(self):
        for laborem_process in self.LABOREM_PROCESSES:
            try:
                bp = BackgroundProcess.objects.get(pk=laborem_process['id'])
                bp.restart()
            except:
                logger.debug('%s, unhandled exception\n%s' % (self.label, traceback.format_exc()))

        return False

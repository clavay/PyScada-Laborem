#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import SingleDeviceDAQProcessWorker
from pyscada.laborem import PROTOCOL_ID

from pyscada.laborem.models import LaboremMotherboardDevice, LaboremGroupInputPermission
from pyscada.models import Variable, VariableProperty
from django.contrib.auth.models import Group

from time import sleep
import traceback
import logging

logger = logging.getLogger(__name__)


class Process(SingleDeviceDAQProcessWorker):
    device_filter = dict(laboremmotherboarddevice__isnull=False, protocol_id=PROTOCOL_ID)
    bp_label = 'pyscada.laborem-%s'

    def __init__(self, dt=5, **kwargs):
        super(SingleDeviceDAQProcessWorker, self).__init__(dt=dt, **kwargs)

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
            logger.error("Laborem cannot start : No LaboremMotherBoardDevice")
            # logger.debug('%s, unhandled exception\n%s' % (self.label, traceback.format_exc()))
        lw.move_robot = True
        lt.move_robot = True
        lw.top10_answer = True
        lt.top10_answer = True
        lw.save()
        lt.save()

    def init_process(self):
        super(SingleDeviceDAQProcessWorker, self).init_process()
        if LaboremMotherboardDevice.objects.count():
            LaboremMotherboardDevice.objects.first().relay(False)
            sleep(1)
            LaboremMotherboardDevice.objects.first().relay(True)

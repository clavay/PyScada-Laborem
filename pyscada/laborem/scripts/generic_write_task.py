#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
handles write tasks for variables attached to the generic devices
"""

from pyscada.models import DeviceWriteTask, VariableProperty, RecordedData
from time import time, sleep
import logging

logger = logging.getLogger(__name__)


def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """
    sleep(60)
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
    # add
    for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(), failed=False,
                                               variable_property__variable__device__protocol=1)\
            .order_by('variable_property__name'):
        logger.info('GenericDeviceWriteTask VP : %s' % task.__str__())
        if task.variable_property.variable.scaling is not None:
            task.value = task.variable_property.variable.scaling.scale_output_value(task.value)
        if task.variable_property:
            # write the freq property to VariableProperty use that for later read
            vp = VariableProperty.objects.update_property(variable_property=task.variable_property, value=task.value)
            if vp:
                task.done = True
                task.finished = time()
                task.save()
                continue

        logger.debug('nothing to do for device write task %d' % task.pk)
        task.failed = True
        task.finished = time()
        task.save()

    for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(), failed=False,
                                               variable__device__protocol=1).order_by('variable__name'):
        logger.info('GenericDeviceWriteTask Variable : %s' % task.__str__())
        # if task.variable.scaling is not None:
        #    task.value = task.variable.scaling.scale_output_value(task.value)
        if task.variable:
            # write value to Variable use that for later read
            tmp_data = task.variable.update_value(task.value, time())
            if tmp_data:
                task.done = True
                task.finished = time()
                task.save()
                RecordedData.objects.bulk_create([task.variable.create_recorded_data_element()])
            else:
                task.failed = True
                task.finished = time()
                task.save()

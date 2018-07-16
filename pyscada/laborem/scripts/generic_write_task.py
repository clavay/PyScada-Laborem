#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
handles write tasks for variables attached to the generic devices
"""

from pyscada.models import DeviceWriteTask, VariableProperty
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
                                               variable_property__variable__device__protocol=1):
        # logger.info('DeviceWriteTask VP : %s' % task.__str__())
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

    '''
    for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(), failed=False,
                                               variable__device__protocol=1).order_by('start'):
        data = []
        # logger.info('DeviceWriteTask V : %s' % task.__str__())
        if task.variable.scaling is not None:
            task.value = task.variable.scaling.scale_output_value(task.value)
        if task.variable:
            # write value to Variable use that for later read
            tmp_data = self.device.write_data(task.variable.id, task.value, task)
            if isinstance(tmp_data, list):
                if len(tmp_data) > 0:
                    task.done = True
                    task.finished = time()
                    task.save()
                    data.append(tmp_data)
                else:
                    task.failed = True
                    task.finished = time()
                    task.save()
            else:
                task.failed = True
                task.finished = time()
                task.save()
            if isinstance(data, list):
                if len(data) > 0:
                    return 1, data
    '''

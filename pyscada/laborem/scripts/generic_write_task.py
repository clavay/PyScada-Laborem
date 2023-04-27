#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
handles write tasks for variables attached to the generic devices
"""

from pyscada.models import DeviceWriteTask, VariableProperty, RecordedData
from pyscada.utils import set_bit
from time import time, sleep
import logging
from django.utils.timezone import now

logger = logging.getLogger(__name__)


def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """
    sleep(10)
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
    t_start = time()

    # add
    tasks = []
    items = []

    variable_as_decimal = {}
    # Iterate on VPs
    for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(), failed=False, variable_property__variable__device__protocol=1).order_by('start'):
        logger.error(task)
        if task.variable_property is not None and \
           len(task.variable_property.name.split("bit")) == 2 and \
           task.variable_property.name.split("bit")[0] == "" and \
           task.variable_property.name.split("bit")[1].isdigit() and \
           int(task.variable_property.name.split("bit")[1]) <= task.variable_property.variable.get_bits_by_class():
            if task.variable_property.variable not in variable_as_decimal:
                variable_as_decimal[task.variable_property.variable] = {}
            logger.error('ok')

            variable_as_decimal[task.variable_property.variable][task.variable_property.name.split("bit")[1]] = task.value
            # Set the VP task as done
            task.done = True
            task.finished = time()
            task.save(update_fields=['done', 'finished'])
            # Save the VP value
            VariableProperty.objects.update_property(variable_property=task.variable_property, value=task.value)
    # Get and change the variable value
    for var, item in variable_as_decimal.items():
        if var.query_prev_value(0):
            prev_value = var.prev_value
        else:
            prev_value = 0
        logger.error(prev_value)
        for bit, value in item.items():
            prev_value = set_bit(int(prev_value), int(bit), bool(value))
        logger.error(prev_value)
        # Create a new device write task for this varaible with the new value
        dwt = DeviceWriteTask(variable=var, value=prev_value)
        dwt.save()

    # other VP write task
    for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(), failed=False,
                                               variable_property__variable__device__protocol=1)\
            .order_by('variable_property__name'):
        #logger.debug('GenericDeviceWriteTask VP : %s' % task.__str__())
        if task.variable_property.variable.scaling is not None:
            task.value = task.variable_property.variable.scaling.scale_output_value(task.value)
        if task.variable_property:
            # write the value to VariableProperty
            vp = VariableProperty.objects.update_property(variable_property=task.variable_property, value=task.value)
            if vp:
                task.done = True
                task.finished = time()
                tasks.append(task)
                continue

        logger.debug('nothing to do for device write task %d' % task.pk)
        task.failed = True
        task.finished = time()
        tasks.append(task)

    for task in DeviceWriteTask.objects.filter(done=False, start__lte=time(), failed=False,
                                               variable__device__protocol=1).order_by('variable__name'):
        #logger.debug('GenericDeviceWriteTask Variable : %s' % task.__str__())
        # if task.variable.scaling is not None:
        #    task.value = task.variable.scaling.scale_output_value(task.value)
        if task.variable:
            # write value to Variable use that for later read
            tmp_data = task.variable.update_value(task.value, time())
            if tmp_data:
                task.done = True
                task.finished = time()
                # task.save()
                tasks.append(task)
                item = task.variable.create_recorded_data_element()
                item.date_saved = now()
                # RecordedData.objects.bulk_create([item])
                items.append(item)
            else:
                task.failed = True
                task.finished = time()
                # task.save()
                tasks.append(task)

    DeviceWriteTask.objects.bulk_update(tasks, ['done', 'finished', 'failed'])
    RecordedData.objects.bulk_create(items, batch_size=1000, ignore_conflicts=True)
    if time() - t_start > 1:
        logger.debug("generic in : " + str(int(time() - t_start)))


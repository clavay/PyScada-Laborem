# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.laborem.models import LaboremMotherboardDevice, ExtendedLaboremMotherboardDevice

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LaboremMotherboardDevice)
@receiver(post_save, sender=ExtendedLaboremMotherboardDevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is LaboremMotherboardDevice:
        post_save.send_robust(sender=Device, instance=instance.laboremmotherboard_device)
    elif type(instance) is ExtendedLaboremMotherboardDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))

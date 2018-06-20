# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

import logging

logger = logging.getLogger(__name__)

@python_2_unicode_compatible
class LaboremMotherboardDevice(models.Model):
    laboremmotherboard_device = models.OneToOneField(Device, null=True, blank=True)
    plug1 = models.ForeignKey('LaboremPlugDevice')
    plug2 = models.ForeignKey('LaboremPlugDevice')
    plug3 = models.ForeignKey('LaboremPlugDevice')
    plug4 = models.ForeignKey('LaboremPlugDevice')
    plug5 = models.ForeignKey('LaboremPlugDevice')
    plug6 = models.ForeignKey('LaboremPlugDevice')
    plug7 = models.ForeignKey('LaboremPlugDevice')
    plug8 = models.ForeignKey('LaboremPlugDevice')
    plug9 = models.ForeignKey('LaboremPlugDevice')
    plug10 = models.ForeignKey('LaboremPlugDevice')
    plug11 = models.ForeignKey('LaboremPlugDevice')
    plug12 = models.ForeignKey('LaboremPlugDevice')
    plug13 = models.ForeignKey('LaboremPlugDevice')
    plug14 = models.ForeignKey('LaboremPlugDevice')
    plug15 = models.ForeignKey('LaboremPlugDevice')
    plug16 = models.ForeignKey('LaboremPlugDevice')
    MotherboardIOConfig = models.ForeignKey('LaboremMotherboardIOConfig')
    # TODO : Make the motherboard Config to be restrictive on plug selection

@python_2_unicode_compatible
class LaboremMotherboardIOConfig(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    C0 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C0 connector')
    C1 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C1 connector')
    C2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C2 connector')
    C3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C3 connector')
    C4 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C4 connector')
    C5 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C5 connector')
    C6 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C6 connector')
    C7 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C7 connector')
    V0 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V0 connector')
    V1 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V1 connector')
    V2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V2 connector')
    V3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V3 connector')
    pinA = models.ForeignKey('GPIODevice', help_text='Relay')
    pinB = models.ForeignKey('GPIODevice', help_text='A0 connector')
    pinC = models.ForeignKey('GPIODevice', help_text='A1 connector')
    pinD = models.ForeignKey('GPIODevice', help_text='A2 connector')
    pinE = models.ForeignKey('GPIODevice', help_text='A3 connector')

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class LaboremMotherboardIOElement(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class LaboremPlugDevice(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    plug_image = models.ImageField(upload_to="img/laborem/plugs/", verbose_name="plug image", blank=True)
    motherboardIOConfig = models.ForeignKey('LaboremMotherboardIOConfig')
    level_choices = (('1', 'Easy'), ('2', 'Medium'), ('3', 'Hard'))
    level = models.CharField(max_length=254, choices=level_choices)

    def __str__(self):
        return self.laboremmotherboard_device.short_name

@python_2_unicode_compatible
class LaboremMotherboardVariable(models.Model):
    laboremmotherboard_variable = models.OneToOneField(Variable, null=True, blank=True)
    plug_choices = (('1', '1'),
                    ('2', '2'),
                    ('3', '3'),
                    ('4', '4'),
                    ('5', '5'),
                    ('6', '6'),
                    ('7', '7'),
                    ('8', '8'),
                    ('9', '9'),
                    ('10', '10'),
                    ('11', '11'),
                    ('12', '12'),
                    ('13', '13'),
                    ('14', '14'),
                    ('15', '15'),
                    ('16', '16'))
    plug = models.CharField(max_length=254, choices=plug_choices)

@receiver(post_save, sender=LaboremMotherboardDevice)
@receiver(post_save, sender=LaboremMotherboardVariable)
@receiver(post_save, sender=LaboremPlugDevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is LaboremMotherboardDevice:
        post_save.send_robust(sender=Device, instance=instance.laboremmotherboard_device)
    elif type(instance) is LaboremMotherboardVariable:
        post_save.send_robust(sender=Variable, instance=instance.laboremmotherboard_variable)

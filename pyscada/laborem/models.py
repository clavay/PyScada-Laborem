# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable, Unit
from pyscada.gpio.models import GPIOVariable
from pyscada.visa.models import VISADevice

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class LaboremMotherboardDevice(models.Model):
    laboremmotherboard_device = models.OneToOneField(Device, null=True, blank=True)
    plug1 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug1')
    plug2 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug2')
    plug3 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug3')
    plug4 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug4')
    plug5 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug5')
    plug6 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug6')
    plug7 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug7')
    plug8 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug8')
    plug9 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug9')
    plug10 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug10')
    plug11 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug11')
    plug12 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug12')
    plug13 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug13')
    plug14 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug14')
    plug15 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug15')
    plug16 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug16')
    MotherboardIOConfig = models.ForeignKey('LaboremMotherboardIOConfig')
    # TODO : Make the motherboard Config to be restrictive on plug selection
    plug_choices = (('0', '0'),
                    ('1', '1'),
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
    plug = models.CharField(max_length=254, choices=plug_choices, default=0)

    def __str__(self):
        return self.laboremmotherboard_device.short_name


@python_2_unicode_compatible
class LaboremMotherboardIOConfig(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    C0 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C0 connector', related_name='mobo_C0')
    C1 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C1 connector', related_name='mobo_C1')
    C2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C2 connector', related_name='mobo_C2')
    C3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C3 connector', related_name='mobo_C3')
    C4 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C4 connector', related_name='mobo_C4')
    C5 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C5 connector', related_name='mobo_C5')
    C6 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C6 connector', related_name='mobo_C6')
    C7 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C7 connector', related_name='mobo_C7')
    V0 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V0 connector', related_name='mobo_V0')
    V1 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V1 connector', related_name='mobo_V1')
    V2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V2 connector', related_name='mobo_V2')
    V3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V3 connector', related_name='mobo_V3')
    pinA = models.OneToOneField(GPIOVariable, help_text='Relay', null=True, blank=True, related_name='mobo_pinA')
    pinB = models.OneToOneField(GPIOVariable, help_text='A0 connector', null=True, blank=True, related_name='mobo_pinB')
    pinC = models.OneToOneField(GPIOVariable, help_text='A1 connector', null=True, blank=True, related_name='mobo_pinC')
    pinD = models.OneToOneField(GPIOVariable, help_text='A2 connector', null=True, blank=True, related_name='mobo_pinD')
    pinE = models.OneToOneField(GPIOVariable, help_text='A3 connector', null=True, blank=True, related_name='mobo_pinE')

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
        return self.name


@python_2_unicode_compatible
class LaboremRobotElement(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    robot = models.ForeignKey(VISADevice)
    value = models.FloatField(default=0)
    unit = models.ForeignKey(Unit, on_delete=models.SET(1))
    active = models.PositiveSmallIntegerField(default=0)
    R = models.FloatField(default=0)
    theta = models.FloatField(default=0)
    z = models.FloatField(default=0)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class LaboremRobotBase(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    element = models.ForeignKey(LaboremRobotElement)
    # TODO : 2 bases cannot select the same element

    def __str__(self):
        return self.name


@receiver(post_save, sender=LaboremMotherboardDevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is LaboremMotherboardDevice:
        post_save.send_robust(sender=Device, instance=instance.laboremmotherboard_device)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Unit
from pyscada.gpio.models import GPIOVariable
from pyscada.visa.models import VISADevice
from pyscada.hmi.models import WidgetContentModel

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.template.loader import get_template

import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class LaboremMotherboardDevice(WidgetContentModel):
    laboremmotherboard_device = models.OneToOneField(Device, blank=True, null=True)
    plug1 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug1', blank=True, null=True)
    plug2 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug2', blank=True, null=True)
    plug3 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug3', blank=True, null=True)
    plug4 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug4', blank=True, null=True)
    plug5 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug5', blank=True, null=True)
    plug6 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug6', blank=True, null=True)
    plug7 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug7', blank=True, null=True)
    plug8 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug8', blank=True, null=True)
    plug9 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug9', blank=True, null=True)
    plug10 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug10', blank=True, null=True)
    plug11 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug11', blank=True, null=True)
    plug12 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug12', blank=True, null=True)
    plug13 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug13', blank=True, null=True)
    plug14 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug14', blank=True, null=True)
    plug15 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug15', blank=True, null=True)
    plug16 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug16', blank=True, null=True)
    MotherboardIOConfig = models.ForeignKey('LaboremMotherboardIOConfig', blank=True, null=True)
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

    def change_selected_plug(self, plug):
        self.plug = self.plug_choices[plug][0]
        self.save()
        return True

    def visible(self):
        return True

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        main_template = get_template('DUT_selector.html')
        main_content = main_template.render(dict(dut_selector=self))
        sidebar_content = None
        return main_content, sidebar_content


@python_2_unicode_compatible
class LaboremMotherboardIOConfig(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    V1 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V1 connector', null=True, blank=True,
                           related_name='mobo_V1')
    V2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V2 connector', null=True, blank=True,
                           related_name='mobo_V2')
    V3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V3 connector', null=True, blank=True,
                           related_name='mobo_V3')
    V4 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V4 connector', null=True, blank=True,
                           related_name='mobo_V4')
    C1 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C1 connector', null=True, blank=True,
                           related_name='mobo_C1')
    C2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C2 connector', null=True, blank=True,
                           related_name='mobo_C2')
    C3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C3 connector', null=True, blank=True,
                           related_name='mobo_C3')
    C4 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C4 connector', null=True, blank=True,
                           related_name='mobo_C4')
    C5 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C5 connector', null=True, blank=True,
                           related_name='mobo_C5')
    C6 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C6 connector', null=True, blank=True,
                           related_name='mobo_C6')
    C7 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C7 connector', null=True, blank=True,
                           related_name='mobo_C7')
    C8 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C8 connector', null=True, blank=True,
                           related_name='mobo_C8')
    pin1 = models.OneToOneField(GPIOVariable, help_text='A0 connector', null=True, blank=True, related_name='mobo_pin1')
    pin2 = models.OneToOneField(GPIOVariable, help_text='A1 connector', null=True, blank=True, related_name='mobo_pin2')
    pin3 = models.OneToOneField(GPIOVariable, help_text='A2 connector', null=True, blank=True, related_name='mobo_pin3')
    pin4 = models.OneToOneField(GPIOVariable, help_text='A3 connector', null=True, blank=True, related_name='mobo_pin4')
    pin5 = models.OneToOneField(GPIOVariable, help_text='Relay', null=True, blank=True, related_name='mobo_pin5')
    pin6 = models.OneToOneField(GPIOVariable, help_text='Ground', null=True, blank=True, related_name='mobo_pin6')

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
class LaboremRobotBase(WidgetContentModel):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    element = models.ForeignKey(LaboremRobotElement, blank=True, null=True)
    R = models.FloatField(default=0)
    theta = models.FloatField(default=0)
    z = models.FloatField(default=0)
    # TODO : 2 bases cannot select the same element

    def __str__(self):
        return self.name

    def change_selected_element(self, element_id):
        self.element.pk = element_id
        self.save()
        return True

    def visible(self):
        return True

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        visible_robot_element_list = LaboremRobotElement.objects.all()
        main_template = get_template('robot_selector.html')
        main_content = main_template.render(dict(base=self, visible_robot_element_list=visible_robot_element_list))
        sidebar_content = None
        return main_content, sidebar_content

@receiver(post_save, sender=LaboremMotherboardDevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is LaboremMotherboardDevice:
        post_save.send_robust(sender=Device, instance=instance.laboremmotherboard_device)

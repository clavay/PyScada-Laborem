# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Unit, Variable, VariableProperty
from pyscada.gpio.models import GPIOVariable
from pyscada.visa.models import VISADevice
from pyscada.hmi.models import WidgetContentModel, Page

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.template.loader import get_template
from django.contrib.auth.models import User, Group

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class LaboremMotherboardDevice(WidgetContentModel):
    laboremmotherboard_device = models.OneToOneField(Device, blank=True, null=True, on_delete=models.CASCADE)
    plug1 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug1', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug2 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug2', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug3 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug3', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug4 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug4', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug5 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug5', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug6 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug6', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug7 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug7', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug8 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug8', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug9 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug9', blank=True, null=True,
                              on_delete=models.CASCADE)
    plug10 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug10', blank=True, null=True,
                               on_delete=models.CASCADE)
    plug11 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug11', blank=True, null=True,
                               on_delete=models.CASCADE)
    plug12 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug12', blank=True, null=True,
                               on_delete=models.CASCADE)
    plug13 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug13', blank=True, null=True,
                               on_delete=models.CASCADE)
    plug14 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug14', blank=True, null=True,
                               on_delete=models.CASCADE)
    plug15 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug15', blank=True, null=True,
                               on_delete=models.CASCADE)
    plug16 = models.ForeignKey('LaboremPlugDevice', related_name='mobo_plug16', blank=True, null=True,
                               on_delete=models.CASCADE)
    MotherboardIOConfig = models.ForeignKey('LaboremMotherboardIOConfig', blank=True, null=True,
                                            on_delete=models.CASCADE)
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

    def get_selected_plug(self):
        if self.plug == '1':
            return self.plug1
        elif self.plug == '2':
            return self.plug2
        elif self.plug == '3':
            return self.plug3
        elif self.plug == '4':
            return self.plug4
        elif self.plug == '5':
            return self.plug5
        elif self.plug == '6':
            return self.plug6
        elif self.plug == '7':
            return self.plug7
        elif self.plug == '8':
            return self.plug8
        elif self.plug == '9':
            return self.plug9
        elif self.plug == '10':
            return self.plug10
        elif self.plug == '11':
            return self.plug11
        elif self.plug == '12':
            return self.plug12
        elif self.plug == '13':
            return self.plug13
        elif self.plug == '14':
            return self.plug14
        elif self.plug == '15':
            return self.plug15
        elif self.plug == '16':
            return self.plug16
        elif self.plug == '0':
            return None

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
                           related_name='mobo_V1', on_delete=models.CASCADE)
    V2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V2 connector', null=True, blank=True,
                           related_name='mobo_V2', on_delete=models.CASCADE)
    V3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V3 connector', null=True, blank=True,
                           related_name='mobo_V3', on_delete=models.CASCADE)
    V4 = models.ForeignKey('LaboremMotherboardIOElement', help_text='V4 connector', null=True, blank=True,
                           related_name='mobo_V4', on_delete=models.CASCADE)
    C1 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C1 connector', null=True, blank=True,
                           related_name='mobo_C1', on_delete=models.CASCADE)
    C2 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C2 connector', null=True, blank=True,
                           related_name='mobo_C2', on_delete=models.CASCADE)
    C3 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C3 connector', null=True, blank=True,
                           related_name='mobo_C3', on_delete=models.CASCADE)
    C4 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C4 connector', null=True, blank=True,
                           related_name='mobo_C4', on_delete=models.CASCADE)
    C5 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C5 connector', null=True, blank=True,
                           related_name='mobo_C5', on_delete=models.CASCADE)
    C6 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C6 connector', null=True, blank=True,
                           related_name='mobo_C6', on_delete=models.CASCADE)
    C7 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C7 connector', null=True, blank=True,
                           related_name='mobo_C7', on_delete=models.CASCADE)
    C8 = models.ForeignKey('LaboremMotherboardIOElement', help_text='C8 connector', null=True, blank=True,
                           related_name='mobo_C8', on_delete=models.CASCADE)
    pin1 = models.OneToOneField(GPIOVariable, help_text='A0 connector', null=True, blank=True, related_name='mobo_pin1',
                                on_delete=models.SET_NULL)
    pin2 = models.OneToOneField(GPIOVariable, help_text='A1 connector', null=True, blank=True, related_name='mobo_pin2',
                                on_delete=models.SET_NULL)
    pin3 = models.OneToOneField(GPIOVariable, help_text='A2 connector', null=True, blank=True, related_name='mobo_pin3',
                                on_delete=models.SET_NULL)
    pin4 = models.OneToOneField(GPIOVariable, help_text='A3 connector', null=True, blank=True, related_name='mobo_pin4',
                                on_delete=models.SET_NULL)
    pin5 = models.OneToOneField(GPIOVariable, help_text='Relay', null=True, blank=True, related_name='mobo_pin5',
                                on_delete=models.SET_NULL)
    pin6 = models.OneToOneField(GPIOVariable, help_text='Ground', null=True, blank=True, related_name='mobo_pin6',
                                on_delete=models.SET_NULL)
    mdo1 = models.ForeignKey(Device, help_text='Oscilloscope', null=True, blank=True, related_name='osc1',
                             on_delete=models.SET_NULL)
    mdo2 = models.ForeignKey(Device, help_text='Oscilloscope', null=True, blank=True, related_name='osc2',
                             on_delete=models.SET_NULL)
    dmm1 = models.ForeignKey(Device, help_text='Multimeter', null=True, blank=True, related_name='mm1',
                             on_delete=models.SET_NULL)
    afg1 = models.ForeignKey(Device, help_text='Function Generator', null=True, blank=True, related_name='afg1',
                             on_delete=models.SET_NULL)
    dcps1 = models.ForeignKey(Device, help_text='DC Power Supply', null=True, blank=True, related_name='dcps1',
                              on_delete=models.SET_NULL)
    robot1 = models.ForeignKey(Device, help_text='Robot Arm', null=True, blank=True, related_name='robot1',
                               on_delete=models.SET_NULL)

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
    motherboardIOConfig = models.ForeignKey(LaboremMotherboardIOConfig, null=True, on_delete=models.SET_NULL)
    level_choices = (('1', 'beginner'), ('2', 'intermediate'), ('3', 'advanced'))
    level = models.CharField(max_length=254, choices=level_choices)
    robot = models.ForeignKey(VISADevice, blank=True, null=True, on_delete=models.SET_NULL,
                              help_text='If the PCB Plug is modifiable with the robot choose the Robot device. '
                                        'If not let it blank')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class LaboremRobotElement(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    robot = models.ForeignKey(VISADevice, null=True, on_delete=models.SET_NULL)
    value = models.FloatField(default=0)
    unit = models.ForeignKey(Unit, on_delete=models.SET(1))
    active = models.PositiveSmallIntegerField(default=0)
    R = models.FloatField(default=0)
    theta = models.FloatField(default=0)
    z = models.FloatField(default=0)

    def __str__(self):
        return self.name

    def change_active_to_base_id(self, base_id):
        self.active = base_id
        self.save()
        return True


@python_2_unicode_compatible
class LaboremRobotBase(WidgetContentModel):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    element = models.ForeignKey(LaboremRobotElement, blank=True, null=True, on_delete=models.SET_NULL)
    R = models.FloatField(default=0)
    theta = models.FloatField(default=0)
    z = models.FloatField(default=0)
    # TODO : 2 bases cannot select the same element

    def __str__(self):
        return self.name

    def change_selected_element(self, element_id):
        if element_id is None:
            self.element = None
        else:
            self.element = LaboremRobotElement.objects.get(pk=element_id)
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


@python_2_unicode_compatible
class LaboremTOP10(models.Model):
    name = models.CharField(default='', max_length=255)
    description = models.TextField(default='', verbose_name="Description", null=True)
    page = models.ForeignKey(Page, default=1, null=True, on_delete=models.SET_NULL)
    plug = models.ForeignKey(LaboremPlugDevice, null=True, on_delete=models.SET_NULL)
    robot_base1 = models.ForeignKey(LaboremRobotElement, blank=True, null=True, related_name='robot_base1',
                                    on_delete=models.SET_NULL)
    robot_base2 = models.ForeignKey(LaboremRobotElement, blank=True, null=True, related_name='robot_base2',
                                    on_delete=models.SET_NULL)
    question1 = models.CharField(default='', max_length=255, blank=True, null=True)
    answer1 = models.CharField(default='', max_length=255, blank=True, null=True)
    question2 = models.CharField(default='', max_length=255, blank=True, null=True)
    answer2 = models.CharField(default='', max_length=255, blank=True, null=True)
    question3 = models.CharField(default='', max_length=255, blank=True, null=True)
    answer3 = models.CharField(default='', max_length=255, blank=True, null=True)
    question4 = models.CharField(default='', max_length=255, blank=True, null=True)
    answer4 = models.CharField(default='', max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Laborem TOP10 Questions/Answers'
        verbose_name_plural = 'Laborem TOP10 Questions/Answers'


@python_2_unicode_compatible
class LaboremTOP10Score(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    TOP10QA = models.ForeignKey(LaboremTOP10, null=True, on_delete=models.SET_NULL)
    answer1 = models.CharField(default='', max_length=255, blank=True, null=True)
    answer2 = models.CharField(default='', max_length=255, blank=True, null=True)
    answer3 = models.CharField(default='', max_length=255, blank=True, null=True)
    answer4 = models.CharField(default='', max_length=255, blank=True, null=True)
    note = models.FloatField(default=0)
    active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Laborem TOP10 Score'
        verbose_name_plural = 'Laborem TOP10 Scores'


@python_2_unicode_compatible
class LaboremTOP10Ranking(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    score = models.FloatField(default=0)
    active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Laborem TOP10 Ranking'
        verbose_name_plural = 'Laborem TOP10 Ranking'
        ordering = ['-score']


@python_2_unicode_compatible
class LaboremExperience(models.Model):
    page = models.OneToOneField(Page, null=True, on_delete=models.SET_NULL)
    description = models.TextField(default='', verbose_name="Description", null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.page.link_title) if self.page is not None else str(self.pk)


@python_2_unicode_compatible
class LaboremGroupInputPermission(models.Model):
    hmi_group = models.OneToOneField(Group, null=True, on_delete=models.SET_NULL)
    variables = models.ManyToManyField(Variable, blank=True)
    variable_properties = models.ManyToManyField(VariableProperty, blank=True)
    laborem_motherboard_device = models.ManyToManyField(LaboremMotherboardDevice, blank=True)
    move_robot = models.BooleanField(default=False, blank=True)
    top10_answer = models.BooleanField(default=False, blank=True)
    laborem_experiences = models.ManyToManyField(LaboremExperience, blank=True)

    def __str__(self):
        return self.hmi_group.name


@python_2_unicode_compatible
class LaboremUser(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    laborem_group_input = models.ForeignKey(LaboremGroupInputPermission, null=True, blank=True,
                                            on_delete=models.SET_NULL)
    connection_time = models.DateTimeField(default=datetime.now, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    last_check = models.DateTimeField(null=True, blank=True)
    connection_id = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return self.user.username


class ExtendedLaboremMotherboardDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'Laborem Motherboard Device'
        verbose_name_plural = 'Laborem Motherboard Devices'

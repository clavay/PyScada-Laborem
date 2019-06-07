# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-06-07 09:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0054_auto_20190411_0749'),
        ('laborem', '0027_auto_20190111_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='laboremmotherboardioconfig',
            name='afg1',
            field=models.ForeignKey(blank=True, help_text='Function Generator', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='afg1', to='pyscada.Device'),
        ),
        migrations.AddField(
            model_name='laboremmotherboardioconfig',
            name='dcps1',
            field=models.ForeignKey(blank=True, help_text='DC Power Supply', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcps1', to='pyscada.Device'),
        ),
        migrations.AddField(
            model_name='laboremmotherboardioconfig',
            name='dmm1',
            field=models.ForeignKey(blank=True, help_text='Multimeter', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mm1', to='pyscada.Device'),
        ),
        migrations.AddField(
            model_name='laboremmotherboardioconfig',
            name='mdo1',
            field=models.ForeignKey(blank=True, help_text='Oscilloscope', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='osc1', to='pyscada.Device'),
        ),
        migrations.AddField(
            model_name='laboremmotherboardioconfig',
            name='robot1',
            field=models.ForeignKey(blank=True, help_text='Robot Arm', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='robot1', to='pyscada.Device'),
        ),
    ]

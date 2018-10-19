# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-10-17 11:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('laborem', '0012_auto_20181009_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaboremTOP10',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('description', models.TextField(default='', null=True, verbose_name='Description')),
                ('question1', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('answer1', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('question2', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('answer2', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('question3', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('answer3', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('question4', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('answer4', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('active', models.PositiveSmallIntegerField(default=0)),
                ('plug', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laborem.LaboremPlugDevice')),
                ('robot_base1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='robot_base1', to='laborem.LaboremRobotElement')),
                ('robot_base2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='robot_base2', to='laborem.LaboremRobotElement')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

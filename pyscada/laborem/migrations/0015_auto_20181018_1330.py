# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-10-18 13:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('laborem', '0014_auto_20181018_1322'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='laboremtop10',
            options={'verbose_name': 'Laborem TOP10 Questions/Answers', 'verbose_name_plural': 'Laborem TOP10 Questions/Answers'},
        ),
        migrations.AlterModelOptions(
            name='laboremtop10score',
            options={'verbose_name': 'Laborem TOP10 Score', 'verbose_name_plural': 'Laborem TOP10 Scores'},
        ),
    ]
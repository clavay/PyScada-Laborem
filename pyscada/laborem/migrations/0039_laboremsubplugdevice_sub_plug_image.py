# Generated by Django 2.2.8 on 2020-11-23 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laborem', '0038_auto_20201119_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='laboremsubplugdevice',
            name='sub_plug_image',
            field=models.ImageField(blank=True, upload_to='img/laborem/plugs/', verbose_name='plug image'),
        ),
    ]

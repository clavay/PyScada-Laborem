# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site

from django.contrib import admin
from django import forms

from pyscada.laborem import PROTOCOL_ID
from pyscada.laborem.models import LaboremMotherboardDevice
from pyscada.admin import DeviceAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol


class ExtendedLaboremMotherboardDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'LaboREM Motherboard Device'
        verbose_name_plural = 'LaboREM Motherboard Devices'


class LaboremMotherboardDeviceAdminInline(admin.StackedInline):
    model = LaboremMotherboardDevice


class LaboremMotherboardDeviceAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(LaboremMotherboardDeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(LaboremMotherboardDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        LaboremMotherboardDeviceAdminInline
    ]

admin_site.register(ExtendedLaboremMotherboardDevice, LaboremMotherboardDeviceAdmin)
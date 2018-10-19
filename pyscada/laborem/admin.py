# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.laborem import PROTOCOL_ID
from pyscada.laborem.models import LaboremMotherboardDevice, LaboremMotherboardIOConfig, LaboremMotherboardIOElement
from pyscada.laborem.models import LaboremPlugDevice, LaboremRobotElement, LaboremRobotBase
from pyscada.laborem.models import LaboremTOP10 , LaboremTOP10Score, LaboremTOP10Ranking
from pyscada.admin import DeviceAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol
from django.contrib import admin

import logging

logger = logging.getLogger(__name__)


class ExtendedLaboremMotherboardDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'Laborem Motherboard Device'
        verbose_name_plural = 'Laborem Motherboard Devices'


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


class LaboremTOP10ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'plug', 'TOP10QA', 'note', 'active')
    list_display_links = ('user', 'plug')


class LaboremTOP10RankingAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'active')


admin_site.register(ExtendedLaboremMotherboardDevice, LaboremMotherboardDeviceAdmin)
admin_site.register(LaboremMotherboardIOConfig)
admin_site.register(LaboremMotherboardIOElement)
admin_site.register(LaboremPlugDevice)
admin_site.register(LaboremRobotElement)
admin_site.register(LaboremRobotBase)
admin_site.register(LaboremTOP10)
admin_site.register(LaboremTOP10Score, LaboremTOP10ScoreAdmin)
admin_site.register(LaboremTOP10Ranking, LaboremTOP10RankingAdmin)

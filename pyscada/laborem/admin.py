# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.laborem import PROTOCOL_ID
from pyscada.laborem.models import LaboremMotherboardDevice, LaboremMotherboardIOConfig, LaboremMotherboardIOElement
from pyscada.laborem.models import LaboremPlugDevice, LaboremRobotElement, LaboremRobotBase, LaboremUser
from pyscada.laborem.models import LaboremTOP10 , LaboremTOP10Score, LaboremTOP10Ranking, LaboremGroupInputPermission
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
    list_display = ('user', 'TOP10QA', 'note', 'active')
    list_display_links = ('user', 'TOP10QA')


class LaboremTOP10RankingAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'active')


class LaboremTOP10Admin(admin.ModelAdmin):
    list_display = ('name', 'plug', 'robot_base1', 'robot_base2')


class LaboremPlugDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'motherboardIOConfig', 'level')


class LaboremRobotBaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'element', 'R', 'theta', 'z')


class LaboremRobotElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'unit', 'R', 'theta', 'z')


class GroupDisplayPermissionAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables', 'variable_properties', 'laborem_motherboard_device')


class LaboremUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'laborem_group_input', 'connection_time', 'start_time', 'last_check')


admin_site.register(ExtendedLaboremMotherboardDevice, LaboremMotherboardDeviceAdmin)
admin_site.register(LaboremMotherboardIOConfig)
admin_site.register(LaboremMotherboardIOElement)
admin_site.register(LaboremPlugDevice, LaboremPlugDeviceAdmin)
admin_site.register(LaboremRobotElement, LaboremRobotElementAdmin)
admin_site.register(LaboremRobotBase, LaboremRobotBaseAdmin)
admin_site.register(LaboremTOP10, LaboremTOP10Admin)
admin_site.register(LaboremTOP10Score, LaboremTOP10ScoreAdmin)
admin_site.register(LaboremTOP10Ranking, LaboremTOP10RankingAdmin)
admin_site.register(LaboremGroupInputPermission, GroupDisplayPermissionAdmin)
admin_site.register(LaboremUser, LaboremUserAdmin)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaLaboremConfig(AppConfig):
    name = 'pyscada.laborem'
    verbose_name = _("PyScada Laborem")
    path = os.path.dirname(os.path.realpath(__file__))
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        import pyscada.laborem.signals
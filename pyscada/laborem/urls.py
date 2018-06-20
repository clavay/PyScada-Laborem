# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views
from pyscada.admin import admin_site
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Public pages
    url(r'^view_laborem/(?P<link_title>[\w,-]+)/$', views.view_laborem, name="laborem-view"),
]

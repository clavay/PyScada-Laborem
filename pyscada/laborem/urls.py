# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views


urlpatterns = [
    # Public pages
    url(r'^view_laborem/(?P<link_title>[\w,-]+)/$', views.view_laborem, name="laborem-view"),
    url(r'^form/write_plug/$', views.form_write_plug),
    url(r'^form/write_robot_base/$', views.form_write_robot_base),
]

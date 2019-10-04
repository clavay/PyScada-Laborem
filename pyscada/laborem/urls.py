# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Public pages
    url(r'^$', views.index, name="view-overview"),
    url(r'^view_laborem/(?P<link_title>[\w,-]+)/$', views.view_laborem, name="main-laborem-view"),
    url(r'^form/write_plug/$', views.form_write_plug),
    url(r'^form/write_robot_base/$', views.form_write_robot_base),
    url(r'^form/write_property/$', views.form_write_property),
    url(r'^accounts/choose_login/$', auth_views.LoginView, {'template_name': 'choose_login.html'},
        name='choose_login_view'),
    url(r'^json/query_top10_question/$', views.query_top10_question),
    url(r'^form/validate_top10_answers/$', views.validate_top10_answers),
    url(r'^form/rank_top10/$', views.rank_top10),
    url(r'^form/reset_robot_bases/$', views.reset_robot_bases),
    url(r'^form/reset_selected_plug/$', views.reset_selected_plug),
    url(r'^form/move_robot/$', views.move_robot),
    url(r'^form/check_users/$', views.check_users),
    url(r'^form/check_time/$', views.check_time),
    url(r'^form/remove_id/$', views.remove_id),
    url(r'^form/get_experience_list/$', views.get_experience_list),
]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.core import version as core_version
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Form
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View

from .models import LaboremRobotElement
from .models import LaboremMotherboardDevice

from django.http import HttpResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import requires_csrf_token
import logging

logger = logging.getLogger(__name__)


@requires_csrf_token
def view_laborem(request, link_title):
        if not request.user.is_authenticated():
            return redirect('/accounts/choose_login/?next=%s' % request.path)

        page_template = get_template('content_page.html')
        widget_row_template = get_template('widget_row.html')

        try:
            v = View.objects.get(link_title=link_title)
        except View.DoesNotExist or View.MultipleObjectsReturned:
            return HttpResponse(status=404)

        if GroupDisplayPermission.objects.count() == 0:
            # no groups
            page_list = v.pages.all()
            sliding_panel_list = v.sliding_panel_menus.all()

            visible_widget_list = Widget.objects.filter(page__in=page_list.iterator()).values_list('pk', flat=True)
            # visible_custom_html_panel_list = CustomHTMLPanel.objects.all().values_list('pk', flat=True)
            # visible_chart_list = Chart.objects.all().values_list('pk', flat=True)
            # visible_xy_chart_list = XYChart.objects.all().values_list('pk', flat=True)
            visible_control_element_list = ControlItem.objects.all().values_list('pk', flat=True)
            visible_form_list = Form.objects.all().values_list('pk', flat=True)
            visible_robot_element_list = LaboremRobotElement.objects.all().values_list('name', flat=True)
        else:
            page_list = v.pages.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator()).distinct()

            sliding_panel_list = v.sliding_panel_menus.filter(
                groupdisplaypermission__hmi_group__in=request.user.groups.iterator()).distinct()

            visible_widget_list = Widget.objects.filter(
                groupdisplaypermission__hmi_group__in=request.user.groups.iterator(),
                page__in=page_list.iterator()).values_list('pk', flat=True)
            """
            # todo update permission model to reflect new widget structure
            visible_custom_html_panel_list = CustomHTMLPanel.objects.filter(
                groupdisplaypermission__hmi_group__in=request.user.groups.iterator()).values_list('pk', flat=True)
            visible_chart_list = Chart.objects.filter(
                groupdisplaypermission__hmi_group__in=request.user.groups.iterator()).values_list('pk', flat=True)
            visible_xy_chart_list = XYChart.objects.filter(
                groupdisplaypermission__hmi_group__in=request.user.groups.iterator()).values_list('pk', flat=True)
            """
            visible_control_element_list = GroupDisplayPermission.objects.filter(
                hmi_group__in=request.user.groups.iterator()).values_list('control_items', flat=True)
            visible_form_list = GroupDisplayPermission.objects.filter(
                hmi_group__in=request.user.groups.iterator()).values_list('forms', flat=True)

        visible_robot_element_list = LaboremRobotElement.objects.all().values_list('name', flat=True)
        panel_list = sliding_panel_list.filter(position__in=(1, 2,))
        control_list = sliding_panel_list.filter(position=0)

        pages_html = ""
        for page in page_list:
            # process content row by row
            current_row = 0
            widget_rows_html = ""
            main_content = list()
            sidebar_content = list()
            has_chart = False
            for widget in page.widget_set.all():
                # check if row has changed
                if current_row != widget.row:
                    # render new widget row and reset all loop variables
                    widget_rows_html += widget_row_template.render(
                        {'row': current_row, 'main_content': main_content, 'sidebar_content': sidebar_content,
                         'sidebar_visible': len(sidebar_content) > 0}, request)
                    current_row = widget.row
                    main_content = list()
                    sidebar_content = list()
                if widget.pk not in visible_widget_list:
                    continue
                if not widget.visible:
                    continue
                mc, sbc = widget.content.create_panel_html(widget_pk=widget.pk, user=request.user)
                if mc is not None:
                    main_content.append(dict(html=mc, widget=widget))
                if sbc is not None:
                    sidebar_content.append(dict(html=sbc, widget=widget))
                if widget.content.content_model == "pyscada.hmi.models.Chart":
                    has_chart = True

            widget_rows_html += widget_row_template.render(
                {'row': current_row, 'main_content': main_content, 'sidebar_content': sidebar_content,
                 'sidebar_visible': len(sidebar_content) > 0}, request)

            pages_html += page_template.render(
                {'page': page, 'widget_rows_html': widget_rows_html, 'has_chart': has_chart},
                request)

        c = {
            'page_list': page_list,
            'pages_html': pages_html,
            'panel_list': panel_list,
            'control_list': control_list,
            'user': request.user,
            'visible_control_element_list': visible_control_element_list,
            'visible_form_list': visible_form_list,
            'visible_robot_element_list': visible_robot_element_list,
            'view_title': v.title,
            'view_show_timeline': v.show_timeline,
            'version_string': core_version
        }

        return TemplateResponse(request, 'view.html', c)


def form_write_plug(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if 'mb_id' in request.POST and 'plug_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
        plug_id = int(request.POST['plug_id'])
        for mb in LaboremMotherboardDevice.objects.filter(pk=mb_id):
            mb.change_selected_plug(plug_id)
        return HttpResponse(status=200)
    return HttpResponse(status=404)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.core import version as core_version
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Form
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View
from pyscada.hmi.models import Page


from pyscada.models import Variable, VariableProperty, DeviceWriteTask
from .models import LaboremRobotElement
from .models import LaboremRobotBase
from .models import LaboremMotherboardDevice
from .models import LaboremTOP10
from .models import LaboremTOP10Score
from .models import LaboremTOP10Ranking, LaboremGroupInputPermission, LaboremUser

from django.http import HttpResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.models import User
from django.utils.timezone import now

import time
import json
import numpy as np

import logging

logger = logging.getLogger(__name__)


def user_check(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    else:
        if LaboremUser.objects.filter(user=request.user).count() == 0:
            lu = LaboremUser(user=request.user)
            lu.save()


@requires_csrf_token
def view_laborem(request, link_title):
    #if not request.user.is_authenticated():
    #    return redirect('/accounts/choose_login/?next=%s' % request.path)
    user_check(request)

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

    try:
        form_top10qa = Form.objects.get(title="TOP10QA")
    except Form.DoesNotExist or Form.MultipleObjectsReturned:
        return HttpResponse(status=404)

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
        'version_string': core_version,
        'form_top10qa': form_top10qa
    }

    return TemplateResponse(request, 'view_laborem.html', c)


def form_write_plug(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if 'mb_id' in request.POST and 'plug_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
        plug_id = int(request.POST['plug_id'])
        if LaboremGroupInputPermission.objects.count() == 0:
            mb = LaboremMotherboardDevice.objects.get(pk=mb_id)
        else:
            try:
                mb = LaboremMotherboardDevice.objects.get(pk=mb_id,
                                                          laboremgroupinputpermission__hmi_group__in=request.user.groups.iterator())
            except LaboremMotherboardDevice.DoesNotExist:
                return HttpResponse(status=200)
        if mb is not None:
            mb.change_selected_plug(plug_id)
            return HttpResponse(status=200)
    return HttpResponse(status=404)


def form_write_robot_base(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).move_robot:
                continue
        return HttpResponse(status=200)
    if 'base_id' in request.POST and 'element_id' in request.POST:
        base_id = int(request.POST['base_id'])
        element_id = int(request.POST['element_id'])
        for base in LaboremRobotBase.objects.filter(pk=base_id):
            base.change_selected_element(element_id)
        return HttpResponse(status=200)
    return HttpResponse(status=404)


def form_write_property(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if 'variable_property_id' in request.POST and 'value' in request.POST:
        variable_property_id = int(request.POST['variable_property_id'])
        value = request.POST['value']
        if LaboremGroupInputPermission.objects.count() == 0:
            for vp in VariableProperty.objects.filter(pk=variable_property_id):
                VariableProperty.objects.update_property(variable_property=VariableProperty.objects.get(name=vp.name),
                                                         value=value)
        else:
            try:
                for vp in VariableProperty.objects.filter(pk=variable_property_id):
                    vpgetbyname = VariableProperty.objects.get(name=vp.name,
                                                               laboremgroupinputpermission__hmi_group__in=request.user.groups.iterator())
                    VariableProperty.objects.update_property(variable_property=vpgetbyname, value=value)
            except VariableProperty.DoesNotExist:
                return HttpResponse(status=200)
        return HttpResponse(status=200)
    return HttpResponse(status=404)


def query_top10_question(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if not 'mb_id' in request.POST:
        return HttpResponse(status=404)
    mb_id = int(request.POST['mb_id'])
    if LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "1":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug1
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "2":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug2
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "3":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug3
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "4":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug4
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "5":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug5
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "6":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug6
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "7":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug7
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "8":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug8
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "9":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug9
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "10":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug10
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "11":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug11
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "12":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug12
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "13":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug13
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "14":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug14
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "15":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug15
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "16":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug16
    else:
        logger.error("Cannot select plug un query_top10_question")
        return HttpResponse(status=404)
    data = {}
    if LaboremRobotBase.objects.get(name="base1").element is not None \
            and LaboremRobotBase.objects.get(name="base2").element is not None:
        top10qa = LaboremTOP10.objects.filter(plug=plug,
                                              robot_base1__value=LaboremRobotBase.objects.get(name="base1").
                                              element.value,
                                              robot_base1__unit=LaboremRobotBase.objects.get(name="base1").
                                              element.unit,
                                              robot_base2__value=LaboremRobotBase.objects.get(name="base2").
                                              element.value,
                                              robot_base2__unit=LaboremRobotBase.objects.get(name="base2").
                                              element.unit).order_by('id').first()
    elif LaboremRobotBase.objects.get(name="base1").element is None \
            and LaboremRobotBase.objects.get(name="base2").element is None:
        top10qa = LaboremTOP10.objects.filter(plug=plug,robot_base1__value=None, robot_base1__unit=None,
                                              robot_base2__value=None, robot_base2__unit=None).order_by('id').first()
    else:
        return HttpResponse(status=404)
    if top10qa is None:
        return HttpResponse(status=404)
    data['question1'] = top10qa.question1
    data['question2'] = top10qa.question2
    data['question3'] = top10qa.question3
    data['question4'] = top10qa.question4
    return HttpResponse(json.dumps(data), content_type='application/json')


def validate_top10_answers(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).top10_answer:
                continue
        return HttpResponse(status=200)
    if 'mb_id' not in request.POST:
        return HttpResponse(status=404)
    mb_id = int(request.POST['mb_id'])
    if LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "1":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug1
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "2":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug2
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "3":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug3
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "4":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug4
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "5":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug5
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "6":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug6
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "7":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug7
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "8":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug8
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "9":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug9
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "10":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug10
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "11":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug11
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "12":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug12
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "13":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug13
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "14":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug14
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "15":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug15
    elif LaboremMotherboardDevice.objects.get(pk=mb_id).plug == "16":
        plug = LaboremMotherboardDevice.objects.get(pk=mb_id).plug16
    else:
        logger.error("Cannot select plug un validate_top10_answers")
        return HttpResponse(status=404)
    level_plug = 0
    if plug.level == "1":
        level_plug = 1
    elif plug.level == "2":
        level_plug = 3
    elif plug.level == "3":
        level_plug = 5
    else:
        logger.error("Level plug error : %s" % plug.level)
    note = 0
    if LaboremRobotBase.objects.get(name="base1").element is not None \
            and LaboremRobotBase.objects.get(name="base2").element is not None:
        top10qa = LaboremTOP10.objects.filter(plug=plug,
                                              robot_base1__value=LaboremRobotBase.objects.get(name="base1").element.
                                              value,
                                              robot_base1__unit=LaboremRobotBase.objects.get(name="base1").element.
                                              unit,
                                              robot_base2__value=LaboremRobotBase.objects.get(name="base2").element.
                                              value,
                                              robot_base2__unit=LaboremRobotBase.objects.get(name="base2").element.
                                              unit).order_by('id').first()
    elif LaboremRobotBase.objects.get(name="base1").element is None \
            and LaboremRobotBase.objects.get(name="base2").element is None:
        top10qa = LaboremTOP10.objects.filter(plug=plug,robot_base1__value=None, robot_base1__unit=None,
                                              robot_base2__value=None, robot_base2__unit=None).order_by('id').first()
    else:
        return HttpResponse(status=404)
    if top10qa is None:
        return HttpResponse(status=404)
    if top10qa.question1:
        note += calculate_note(level_plug, top10qa.answer1, request.POST['value1'])
    if top10qa.question2:
        note += calculate_note(level_plug, top10qa.answer2, request.POST['value2'])
    if top10qa.question3:
        note += calculate_note(level_plug, top10qa.answer3, request.POST['value3'])
    if top10qa.question4:
        note += calculate_note(level_plug, top10qa.answer4, request.POST['value4'])
    score = LaboremTOP10Score(user=request.user, plug=plug, TOP10QA=top10qa, note=note)
    score.save()
    return HttpResponse(status=200)


def calculate_note(level, answer, student_answer):
    return level * np.exp(-abs(1-float(student_answer)/float(answer))*5)


def rank_top10(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    LaboremTOP10Ranking.objects.all().delete()
    for user in LaboremTOP10Score.objects.values_list('user').distinct():
        score_total = 0
        for item in LaboremTOP10Score.objects.filter(user=user).values_list('TOP10QA').distinct():
            score_total += LaboremTOP10Score.objects.filter(user=user, TOP10QA=item).order_by('id').first().note
        rank = LaboremTOP10Ranking(user=User.objects.get(pk=user[0]), score=score_total)
        rank.save()
    top10ranking_list = LaboremTOP10Ranking.objects.all().order_by('-score')
    data = ""
    for item in top10ranking_list:
        data += '<tr class="top10-item"><td>' + str(item.user.username) + \
                   '</td><td style="text-align: center">' + str(round(item.score, 2)) + '</td></tr>'
    return HttpResponse(json.dumps(data), content_type='application/json')


def query_previous_and_next_btn(request, **kwargs):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if 'actual_hash' in request.POST and 'direction' in request.POST \
            and 'robot' in request.POST and 'expe' in request.POST:
        actual_hash = request.POST['actual_hash']
        direction = request.POST['direction']
        kwargs['robot'] = request.POST['robot']
        kwargs['expe'] = request.POST['expe']
        position = Page.objects.get(link_title=actual_hash).position
        next_page = ""
        previous_page = ""
        if direction == 'start':
            next_page = query_page(position + 1, **kwargs)
            previous_page = ""
        elif direction == 'btn-next':
            next_page = query_page(position + 2, **kwargs)
            previous_page = actual_hash
        elif direction == 'btn-previous':
            next_page = actual_hash
            previous_page = query_page(position - 2, **kwargs)
        elif direction == 'idle':
            next_page = query_page(position + 1, **kwargs)
            previous_page = "="
        data = {}
        data['next_page'] = next_page
        data['previous_page'] = previous_page
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse(status=404)


def query_page(position, **kwargs):
    robot = kwargs.get('robot', None)
    expe = kwargs.get('expe', None)
    try:
        page = Page.objects.get(position=position).link_title
    except Page.DoesNotExist:
        page = ""
    except Page.MultipleObjectsReturned:
        if expe is not None and expe != "":
            try:
                page = Page.objects.get(position=position, link_title=expe).link_title
            except Page.DoesNotExist:
                try:
                    page = Page.objects.get(position=position,
                                            link_title="robot" if robot == '1' else "preconf").link_title
                except Page.DoesNotExist:
                    page = ""
        elif robot is not None and robot != "":
            try:
                page = Page.objects.get(position=position, link_title="robot" if robot == '1' else "preconf").link_title
            except Page.DoesNotExist:
                page = ""
        else:
            page = ""
    return page


def reset_robot_bases(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).move_robot:
                for base in LaboremRobotBase.objects.all():
                    base.change_selected_element(None)
                return HttpResponse(status=200)
    return HttpResponse(status=200)


def move_robot(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/choose_login/?next=%s' % request.path)
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).move_robot:
                if 'move' in request.POST:
                    move = request.POST['move']
                    try:
                        variable = Variable.objects.get(name="Bode_run")
                    except Variable.DoesNotExist:
                        return HttpResponse(status=200)
                    if move == 'put':
                        vp = VariableProperty.objects.get_property(variable=variable, name="Bode_put_on")
                        if vp is None:
                            return HttpResponse(status=200)
                        key = vp.id
                        cwt = DeviceWriteTask(variable_property_id=key, value=1, start=time.time(), user=request.user)
                        cwt.save()
                        return HttpResponse(status=200)
                    if move == 'drop':
                        vp = VariableProperty.objects.get_property(variable=variable, name="Bode_take_off")
                        if vp is None:
                            return HttpResponse(status=200)
                        key = vp.id
                        cwt = DeviceWriteTask(variable_property_id=key, value=1, start=time.time(), user=request.user)
                        cwt.save()
                        return HttpResponse(status=200)
    return HttpResponse(status=200)


def check_users(request):
    LaboremUser.objects.update_or_create(user=request.user, defaults={'last_check': now})
    return HttpResponse(status=200)

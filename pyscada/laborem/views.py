# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.core import version as core_version
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Form
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View
from pyscada.hmi.models import Page

from pyscada.laborem import version as laborem_version
from pyscada.models import Variable, VariableProperty, DeviceWriteTask, VariablePropertyManager
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
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from django.utils.dateformat import format

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
        return False


def index(request):
    u = user_check(request)
    if u:
        return u

    if LaboremUser.objects.get(user=request.user).laborem_group_input is None:
        LaboremUser.objects.filter(user=request.user).exclude(laborem_group_input__hmi_group__name="teacher").update(
            laborem_group_input=LaboremGroupInputPermission.objects.get(hmi_group__name="viewer"),
            last_check=now(), connection_time=now())
        time.sleep(3)
        return redirect('/')
    if GroupDisplayPermission.objects.count() == 0:
        view_list = View.objects.all()
    else:
        view_list = View.objects.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator()).distinct()
    c = {
        'user': request.user,
        'view_list': view_list,
        'version_string': core_version,
        'laborem_version_string': laborem_version
    }
    return TemplateResponse(request, 'view_laborem_overview.html', c)  # HttpResponse(t.render(c))


@requires_csrf_token
def view_laborem(request, link_title):
    # if not request.user.is_authenticated():
    #    return redirect('/accounts/choose_login/?next=%s' % request.path)
    u = user_check(request)
    if u:
        return u

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
        'laborem_version_string': laborem_version,
        'form_top10qa': form_top10qa
    }

    return TemplateResponse(request, 'view_laborem.html', c)


def form_write_plug(request):
    u = user_check(request)
    if u:
        return u

    if 'mb_id' in request.POST and 'plug_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
        plug_id = int(request.POST['plug_id'])
        if LaboremGroupInputPermission.objects.count() == 0:
            mb = LaboremMotherboardDevice.objects.get(pk=mb_id)
        else:
            try:
                mb = LaboremMotherboardDevice.objects.get(pk=mb_id,
                                                          laboremgroupinputpermission__hmi_group__in=request.user.
                                                          groups.iterator())
            except LaboremMotherboardDevice.DoesNotExist:
                return HttpResponse(status=200)
        if mb is not None:
            mb.change_selected_plug(plug_id)
            logger.debug("Change selected plug_id %s - user %s - mb_id %s" % (plug_id, request.user, mb_id))
            return HttpResponse(status=200)
    return HttpResponse(status=404)


def form_write_robot_base(request):
    u = user_check(request)
    if u:
        return u

    if LaboremGroupInputPermission.objects.count() > 0:
        try:
            LaboremGroupInputPermission.objects.get(move_robot=True, hmi_group__in=request.user.groups.all())
        except LaboremGroupInputPermission.DoesNotExist:
            logger.error("write robot base LaboremGroupInputPermission.DoesNotExist for %s" % request.user)
            return HttpResponse(status=404)
    if 'base_id' in request.POST and 'element_id' in request.POST:
        # try:
        #    vpgetbyname = VariableProperty.objects.get(name="message_laborem",
        #                                               laboremgroupinputpermission__hmi_group__in=request.user.
        #                                               groups.iterator())
        #    VariableProperty.objects.update_property(variable_property=vpgetbyname,
        #                                             value="Le robot place les éléments...", value_class='string')
        # except VariableProperty.DoesNotExist:
        #    logger.debug("form_write_property - vp as int or float - "
        #                 "VariableProperty.DoesNotExist or group permission error")
        #    return HttpResponse(status=200)
        base_id = int(request.POST['base_id'])
        element_id = int(request.POST['element_id'])
        for base in LaboremRobotBase.objects.filter(pk=base_id):
            base.change_selected_element(element_id)
        return HttpResponse(status=200)
    logger.error("base_id or element_id not in POST : %s" % request.POST)
    return HttpResponse(status=404)


def form_write_property(request):
    u = user_check(request)
    if u:
        return u

    if 'variable_property' in request.POST and 'value' in request.POST:
        value = request.POST['value']
        try:
            variable_property = int(request.POST['variable_property'])
            if LaboremGroupInputPermission.objects.count() == 0:
                VariableProperty.objects.update_property(variable_property=variable_property, value=value)
            else:
                try:
                    vpgetbyname = VariableProperty.objects.get(pk=variable_property,
                                                               laboremgroupinputpermission__hmi_group__in=request.user.
                                                               groups.iterator())
                    VariableProperty.objects.update_property(variable_property=vpgetbyname, value=value)
                except VariableProperty.DoesNotExist:
                    logger.debug("form_write_property - vp as int or float - "
                                 "VariableProperty.DoesNotExist or group permission error")
                    return HttpResponse(status=200)
        except ValueError:
            variable_property = str(request.POST['variable_property'])
            # if VariableProperty.objects.get(name=variable_property).value_class.upper() in ['STRING']:
            if LaboremGroupInputPermission.objects.count() == 0:
                VariableProperty.objects.update_property(variable_property=VariableProperty.objects.get(
                    name=variable_property), value=value)
            else:
                try:
                    vpgetbyname = VariableProperty.objects.get(name=variable_property,
                                                               laboremgroupinputpermission__hmi_group__in=request.
                                                               user.groups.iterator())
                    VariableProperty.objects.update_property(variable_property=vpgetbyname, value=value)
                except VariableProperty.DoesNotExist:
                    logger.debug("form_write_property - vp as str - "
                                 "VariableProperty.DoesNotExist or group permission error : %s" % variable_property)
                    return HttpResponse(status=200)
            # else:
            #    return HttpResponse(status=404)
        return HttpResponse(status=200)
    return HttpResponse(status=404)


def query_top10_question(request):
    u = user_check(request)
    if u:
        return u

    group_ok = False
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).top10_answer:
                group_ok = True
    if not group_ok:
        return HttpResponse(status=404)
    if 'mb_id' not in request.POST or 'page' not in request.POST:
        logger.debug("query top10 questions : mb_id or page is missing")
        return HttpResponse(status=404)
    mb_id = int(request.POST['mb_id'])
    page = request.POST['page']
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
        logger.error("Cannot select plug in query_top10_question")
        return HttpResponse(status=404)
    data = {}
    if LaboremRobotBase.objects.get(name="base1").element is not None \
            and LaboremRobotBase.objects.get(name="base2").element is not None:
        top10qa = LaboremTOP10.objects.filter(page__link_title=page, plug=plug,
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
        top10qa = LaboremTOP10.objects.filter(page__link_title=page, plug=plug, robot_base1__value=None,
                                              robot_base1__unit=None,
                                              robot_base2__value=None, robot_base2__unit=None).order_by('id').first()
    else:
        logger.debug("top10qa bases error")
        return HttpResponse(status=404)
    if top10qa is None:
        logger.debug("top10qa is None")
        return HttpResponse(json.dumps(data), content_type='application/json')
    data['disable'] = 0
    data['question1'] = top10qa.question1
    data['question2'] = top10qa.question2
    data['question3'] = top10qa.question3
    data['question4'] = top10qa.question4
    if LaboremTOP10Score.objects.filter(user=request.user, TOP10QA=top10qa).count() > 0:
        data['answer1'] = LaboremTOP10Score.objects.filter(user=request.user, TOP10QA=top10qa).first().answer1
        data['answer2'] = LaboremTOP10Score.objects.filter(user=request.user, TOP10QA=top10qa).first().answer2
        data['answer3'] = LaboremTOP10Score.objects.filter(user=request.user, TOP10QA=top10qa).first().answer3
        data['answer4'] = LaboremTOP10Score.objects.filter(user=request.user, TOP10QA=top10qa).first().answer4
        data['disable'] = 1
    return HttpResponse(json.dumps(data), content_type='application/json')


def validate_top10_answers(request):
    u = user_check(request)
    if u:
        return u

    group_ok = False
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).top10_answer:
                group_ok = True
    if not group_ok:
        return HttpResponse(status=404)
    if 'mb_id' not in request.POST or 'page' not in request.POST:
        return HttpResponse(status=404)
    mb_id = int(request.POST['mb_id'])
    page = request.POST['page']
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
        logger.error("Cannot select plug in validate_top10_answers")
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
    note_max = 0
    if LaboremRobotBase.objects.get(name="base1").element is not None \
            and LaboremRobotBase.objects.get(name="base2").element is not None:
        top10qa = LaboremTOP10.objects.filter(page__link_title=page, plug=plug,
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
        top10qa = LaboremTOP10.objects.filter(page__link_title=page, plug=plug, robot_base1__value=None,
                                              robot_base1__unit=None,
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
    score = LaboremTOP10Score(user=request.user, TOP10QA=top10qa, note=note,
                              answer1=request.POST['value1'], answer2=request.POST['value2'],
                              answer3=request.POST['value3'], answer4=request.POST['value4'])
    score.save()
    if top10qa.question1:
        note_max += calculate_note(level_plug, top10qa.answer1, top10qa.answer1)
    if top10qa.question2:
        note_max += calculate_note(level_plug, top10qa.answer2, top10qa.answer2)
    if top10qa.question3:
        note_max += calculate_note(level_plug, top10qa.answer3, top10qa.answer3)
    if top10qa.question4:
        note_max += calculate_note(level_plug, top10qa.answer4, top10qa.answer4)
    VariableProperty.objects.update_or_create_property(Variable.objects.get(name="LABOREM"), "message_laborem",
                                                       "Vous avez eu " + str(round(note, 2)) + "/" + str(note_max),
                                                       value_class='string')
    time.sleep(3)
    VariableProperty.objects.update_or_create_property(Variable.objects.get(name="LABOREM"), "message_laborem",
                                                       "", value_class='string')
    return HttpResponse(status=200)


def calculate_note(level, answer, student_answer):
    return level * np.exp(-abs(1-float(student_answer)/float(answer))*5)


def rank_top10(request):
    u = user_check(request)
    if u:
        return u
    time.sleep(2)
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
    u = user_check(request)
    if u:
        return u

    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).move_robot:
                for base in LaboremRobotBase.objects.all():
                    base.change_selected_element(None)
                return HttpResponse(status=200)
    return HttpResponse(status=200)


def reset_selected_plug(request):
    u = user_check(request)
    if u:
        return u

    if 'mb_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
    else:
        logger.debug("mb_id not in request.POST for reset_selected_plug fonction. Request : %s" % request)
        return HttpResponse(status=404)
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).move_robot:
                try:
                    LaboremMotherboardDevice.change_selected_plug(LaboremMotherboardDevice.objects.get(pk=mb_id), 0)
                    logger.debug("Reset selected plug - user %s - mb_id %s" % (request.user, mb_id))
                except LaboremMotherboardDevice.DoesNotExist:
                    logger.error("request : %s - group : %s" % (request, group))
                return HttpResponse(status=200)
    return HttpResponse(status=200)


def move_robot(request):
    u = user_check(request)
    if u:
        return u

    data = dict()
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
                        for base in LaboremRobotBase.objects.all():
                            if base.element is not None and str(base.element.active) == '0':
                                VariableProperty.objects.update_or_create_property(Variable.objects.get(name="LABOREM"),
                                                                                   "message_laborem",
                                                                                   "Le robot place les éléments...",
                                                                                   value_class='string')
                                data['message_laborem'] = "Le robot place les éléments..."
                        cwt = DeviceWriteTask(variable_property_id=key, value=1, start=time.time(), user=request.user)
                        cwt.save()
                        return HttpResponse(json.dumps(data), content_type='application/json')
                    if move == 'drop':
                        vp = VariableProperty.objects.get_property(variable=variable, name="Bode_take_off")
                        if vp is None:
                            return HttpResponse(status=200)
                        key = vp.id
                        for base in LaboremRobotBase.objects.all():
                            if base.element is not None and str(base.element.active) != '0':
                                VariableProperty.objects.update_or_create_property(Variable.objects.get(name="LABOREM"),
                                                                                   "message_laborem",
                                                                                   "Le robot retire les éléments...",
                                                                                   value_class='string')
                                data['message_laborem'] = "Le robot retire les éléments..."
                        cwt = DeviceWriteTask(variable_property_id=key, value=1, start=time.time(), user=request.user)
                        cwt.save()
                        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse(status=200)


def check_users(request):
    u = user_check(request)
    if u:
        return u
    if 'mb_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
    else:
        logger.debug("mb_id not in request.POST for check_user fonction. Request : %s" % request)
        return HttpResponse(status=404)
    data = dict()

    data['setTimeout'] = 10000

    data['user_type'] = 0
    if request.user.groups.all().first() == Group.objects.get(name="viewer") \
            or request.user.groups.all().first() is None:
        data['user_type'] = 1
        data['setTimeout'] = 10000
    elif request.user.groups.all().first() == Group.objects.get(name="worker"):
        data['user_type'] = 2
        data['setTimeout'] = 1000
    try:
        data['timeline_start'] = (int(format(VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "viewer_start_timeline").timestamp, 'U')) - 1)*1000
    except (Variable.DoesNotExist, AttributeError):
        data['timeline_start'] = ''
    try:
        data['timeline_stop'] = (int(format(VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "viewer_stop_timeline").timestamp, 'U')) + 1)*1000
    except (Variable.DoesNotExist, AttributeError):
        data['timeline_stop'] = ''
    try:
        data['message_laborem'] = VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "message_laborem").value_string
    except (Variable.DoesNotExist, AttributeError):
        data['message_laborem'] = ''
    try:
        progress_bar_now = VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "progress_bar_now").value_int16
        progress_bar_min = VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "progress_bar_min").value_int16
        progress_bar_max = VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "progress_bar_max").value_int16
        if progress_bar_max != progress_bar_min:
            data['progress_bar'] = int(100 * float(progress_bar_now - progress_bar_min) /
                                       float(progress_bar_max - progress_bar_min))
        else:
            data['progress_bar'] = ''
    except (Variable.DoesNotExist, AttributeError):
        data['progress_bar'] = ''

    LaboremUser.objects.update_or_create(user=request.user, defaults={'last_check': now})
    laborem_waiting_users_list = LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").\
        order_by('connection_time')
    laborem_working_user = LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker").first()
    if laborem_working_user is not None:
        current_user = LaboremUser.objects.filter(user=request.user).first()
        data['titletime'] = "unlimited"
        data['waitingusers'] = ""
        i = 0
        j = 0
        title_time = ""
        td = timedelta(minutes=5)
        for item in laborem_waiting_users_list:
            data['waitingusers'] += '<tr class="waitingusers-item"><td>' + str(item.user.username) + \
                                    '</td><td style="text-align: center">'
            if (td - (now() - laborem_working_user.start_time) + i * td).seconds // 60 > 0:
                data['waitingusers'] += str((td - (now() - laborem_working_user.start_time) + i * td).seconds // 60) \
                                        + ' min '
            data['waitingusers'] += str((td - (now() - laborem_working_user.start_time) + i * td).seconds
                                        % 60) + ' sec' + '</td></tr>'
            if current_user == item:
                j = i + 1
                data['titletime'] = ""
                if (td - (now() - laborem_working_user.start_time) + i * td).seconds // 60 > 0:
                    title_time += str((td - (now() - laborem_working_user.start_time) + i * td).seconds // 60) \
                                         + ' min '
                title_time += str((td - (now() - laborem_working_user.start_time) + i * td).seconds % 60) + ' sec'
                data['titletime'] += title_time
            i += 1
        time_left = ' unlimited '
        if i > 0:
            if (td - (now() - laborem_working_user.start_time)).seconds // 60 > 0:
                time_left = str((td - (now() - laborem_working_user.start_time)).seconds // 60) + ' min ' \
                            + str((td - (now() - laborem_working_user.start_time)).seconds % 60) + ' sec'
                if current_user == laborem_working_user:
                    data['titletime'] = ""
                    data['titletime'] += str((td - (now() - laborem_working_user.start_time)).seconds
                                             // 60) + ' min ' + \
                        str((td - (now() - laborem_working_user.start_time)).seconds % 60) + ' sec'
            else:
                time_left = str((td - (now() - laborem_working_user.start_time)).seconds % 60) + ' sec'
                if current_user == laborem_working_user:
                    data['titletime'] = ""
                    data['titletime'] += str((td - (now() - laborem_working_user.start_time)).seconds % 60) + ' sec'
        data['activeuser'] = '<tr class="waitingusers-item"><td>' + str(laborem_working_user.user.username) + \
                             '</td><td style="text-align: center">' + time_left + '</td></tr>'

        data['summary'] = ''
        data['summary'] += '<h3>Résumé</h3>'
        data['summary'] += '<li>En train de manipuler : ' + str(laborem_working_user) + '</li>'
        if j > 0:
            data['summary'] += "<li>File d'attente :<ul><li>Rang : " + str(j) + "</li>"
            data['summary'] += "<li>Temps d'attente : " + str(title_time) + '</li></ul></li>'
            data['viewer_rank'] = str(j)
        try:
            data['summary'] += "<li>Montage en cours : <ul><li>" \
                               + LaboremMotherboardDevice.get_selected_plug(
                LaboremMotherboardDevice.objects.get(pk=mb_id)).name \
                               + "</li>"
            data['plug_name'] = LaboremMotherboardDevice.get_selected_plug(
                LaboremMotherboardDevice.objects.get(pk=mb_id)).name
            data['plug_description'] = LaboremMotherboardDevice.get_selected_plug(
                LaboremMotherboardDevice.objects.get(pk=mb_id)).description
            if LaboremMotherboardDevice.get_selected_plug(LaboremMotherboardDevice.objects.get(pk=mb_id)).robot:
                data['summary'] += "<li>Modifiable via le robot</li>"
                for base in LaboremRobotBase.objects.all():
                    if base.element is not None:
                        data['summary'] += "<li>" + str(base) + " : " + str(base.element) + "</li>"
                data['summary'] += "</ul>"
            else:
                data['summary'] += "<li>Précablé</li></ul>"
            try:
                vp = VariableProperty.objects.get_property(Variable.objects.get(name="LABOREM"),
                                                           "EXPERIENCE").value_string.capitalize()
                if vp != "":
                    data['summary'] += "<li>Expérience en cours : " + vp + "</li>"
            except (Variable.DoesNotExist, AttributeError):
                pass
        except (LaboremMotherboardDevice.DoesNotExist, AttributeError):
            pass
    return HttpResponse(json.dumps(data), content_type='application/json')

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
from pyscada.models import Variable, VariableProperty, DeviceWriteTask
from .models import LaboremRobotElement, LaboremRobotBase, LaboremMotherboardDevice, LaboremExperience
from .models import LaboremTOP10Ranking, LaboremGroupInputPermission, LaboremUser, LaboremTOP10, LaboremTOP10Score

from django.http import HttpResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from django.utils.dateformat import format
from django.conf import settings
from django.contrib.auth import authenticate, login

from uuid import uuid4
import time
import json
import numpy as np

import logging

logger = logging.getLogger(__name__)

UNAUTHENTICATED_REDIRECT = settings.UNAUTHENTICATED_REDIRECT if hasattr(
    settings, 'UNAUTHENTICATED_REDIRECT') else '/accounts/login/'


def unauthenticated_redirect(func):
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated:
            return redirect('%s?next=%s' % (UNAUTHENTICATED_REDIRECT, args[0].path))
        else:
            if LaboremUser.objects.filter(user=args[0].user).count() == 0:
                lu = LaboremUser(user=args[0].user)
                lu.save()
        return func(*args, **kwargs)
    return wrapper


@unauthenticated_redirect
def index(request):
    try:
        if LaboremUser.objects.get(user=request.user).laborem_group_input is None:
            LaboremUser.objects.filter(user=request.user).exclude(laborem_group_input__hmi_group__name="teacher").\
                update(laborem_group_input=LaboremGroupInputPermission.objects.get(hmi_group__name="viewer"),
                       last_check=now(), connection_time=now())
            time.sleep(3)
            return redirect('/')
    except LaboremGroupInputPermission.DoesNotExist:
        pass

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


@unauthenticated_redirect
@requires_csrf_token
def view_laborem(request, link_title):
    page_template = get_template('content_page.html')
    widget_row_template = get_template('widget_row.html')

    try:
        v = View.objects.get(link_title=link_title)
    except (View.DoesNotExist, View.MultipleObjectsReturned):
        return HttpResponse(status=404)

    if GroupDisplayPermission.objects.count() == 0:
        # no groups
        page_list = v.pages.all()
        sliding_panel_list = v.sliding_panel_menus.all()

        visible_widget_list = Widget.objects.filter(page__in=page_list.iterator()).values_list('pk', flat=True)
        # visible_custom_html_panel_list = CustomHTMLPanel.objects.all().values_list('pk', flat=True)
        # visible_chart_list = Chart.objects.all().values_list('pk', flat=True)
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
        """
        visible_control_element_list = GroupDisplayPermission.objects.filter(
            hmi_group__in=request.user.groups.iterator()).values_list('control_items', flat=True)
        visible_form_list = GroupDisplayPermission.objects.filter(
            hmi_group__in=request.user.groups.iterator()).values_list('forms', flat=True)

    visible_robot_element_list = LaboremRobotElement.objects.all()
    visible_robot_base_list = LaboremRobotBase.objects.all()
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
            if widget.content is None:
                continue
            mc, sbc = widget.content.create_panel_html(widget_pk=widget.pk, user=request.user)
            if mc is not None and mc is not "":
                main_content.append(dict(html=mc, widget=widget))
            else:
                logger.info("main_content of widget : %s is %s !" % (widget, mc))
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
    except (Form.DoesNotExist, Form.MultipleObjectsReturned):
        form_top10qa = ""

    if LaboremGroupInputPermission.objects.count() == 0:
        visible_experience_list = LaboremExperience.objects.all()
    else:
        #visible_experience_list = LaboremExperience.objects.filter(laboremgroupinputpermission__hmi_group__in=request.
        #                                                           user.groups.exclude(name='teacher').
        #                                                           iterator())
        visible_experience_list = LaboremExperience.objects.filter(laboremgroupinputpermission__hmi_group__name="worker")

    c = {
        'page_list': page_list,
        'pages_html': pages_html,
        'panel_list': panel_list,
        'control_list': control_list,
        'user': request.user,
        'visible_control_element_list': visible_control_element_list,
        'visible_form_list': visible_form_list,
        'visible_robot_element_list': visible_robot_element_list,
        'visible_robot_base_list': visible_robot_base_list,
        'view_title': v.title,
        'view_show_timeline': v.show_timeline,
        'version_string': core_version,
        'laborem_version_string': laborem_version,
        'form_top10qa': form_top10qa,
        'visible_experience_list': visible_experience_list,
    }

    return TemplateResponse(request, 'view_laborem.html', c)


@unauthenticated_redirect
def form_write_plug(request):
    if 'mb_id' in request.POST and 'plug_id' in request.POST and 'sub_plug_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
        plug_id = int(request.POST['plug_id'])
        sub_plug_id = int(request.POST['sub_plug_id'])
        if sub_plug_id == 0:
            sub_plug_id = None
        if LaboremGroupInputPermission.objects.count() == 0:
            mb = LaboremMotherboardDevice.objects.get(pk=mb_id)
        else:
            try:
                mb = LaboremMotherboardDevice.objects.get(pk=mb_id,
                                                          laboremgroupinputpermission__hmi_group__in=request.user.
                                                          groups.exclude(name='teacher').iterator())
            except LaboremMotherboardDevice.DoesNotExist:
                logger.warning("In form_write_plug  : LaboremMotherboardDevice.DoesNotExist - mb_id : %s - group : %s" %
                               (mb_id, request.user.groups.exclude(name='teacher')))
                return HttpResponse(status=200)
        if mb is not None:
            mb.change_selected_plug(plug_id, sub_plug_id, request.user)
            logger.debug("Change selected plug_id %s sub_plug_id %s - user %s - mb_id %s" % (plug_id, sub_plug_id, request.user, mb_id))
            return HttpResponse(status=200)
    return HttpResponse(status=404)


@unauthenticated_redirect
def form_write_robot_base(request):
    if LaboremGroupInputPermission.objects.count() > 0:
        try:
            LaboremGroupInputPermission.objects.get(
                move_robot=True, hmi_group__in=request.user.groups.exclude(name='teacher').iterator())
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
            base.change_requested_element(element_id)
        return HttpResponse(status=200)
    logger.error("base_id or element_id not in POST : %s" % request.POST)
    return HttpResponse(status=404)


@unauthenticated_redirect
def form_write_property(request):
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
                                                               groups.exclude(name='teacher').iterator())
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
                                                               user.groups.exclude(name='teacher').iterator())
                    VariableProperty.objects.update_property(variable_property=vpgetbyname, value=value)
                except VariableProperty.DoesNotExist:
                    logger.debug("form_write_property - vp as str - "
                                 "VariableProperty.DoesNotExist or group permission error : %s - group : %s" %
                                 (variable_property, request.user.groups.exclude(name='teacher')))
                    return HttpResponse(status=200)
            # else:
            #    return HttpResponse(status=404)
        return HttpResponse(status=200)
    return HttpResponse(status=404)


@unauthenticated_redirect
def query_top10_question(request):
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

    plug, sub_plug = LaboremMotherboardDevice.objects.get(pk=mb_id).get_selected_plug()
    if plug is None:
        logger.error("Cannot select plug in query_top10_question")
        return HttpResponse(status=404)

    data = {}
    if plug.robot is None:
        r_v_1 = None
        r_u_1 = None
        r_v_2 = None
        r_u_2 = None
    elif LaboremRobotBase.objects.get(name="baseVert").element is not None \
            and LaboremRobotBase.objects.get(name="baseRouge").element is not None:
        r_v_1 = LaboremRobotBase.objects.get(name="baseVert").element.value
        r_u_1 = LaboremRobotBase.objects.get(name="baseVert").element.unit
        r_v_2 = LaboremRobotBase.objects.get(name="baseRouge").element.value
        r_u_2 = LaboremRobotBase.objects.get(name="baseRouge").element.unit
    else:
        r_v_1 = None
        r_u_1 = None
        r_v_2 = None
        r_u_2 = None
    top10qa = LaboremTOP10.objects.filter(page__link_title=page, plug=plug, sub_plug=sub_plug, active=True,
                                          robot_base1__value=r_v_1,
                                          robot_base1__unit=r_u_1,
                                          robot_base2__value=r_v_2,
                                          robot_base2__unit=r_u_2).order_by('id').first()

    if top10qa is None:
        logger.debug("top10qa is None")
        return HttpResponse(json.dumps(data), content_type='application/json')
    data['disable'] = 0
    data['question1'] = top10qa.question1
    data['question2'] = top10qa.question2
    data['question3'] = top10qa.question3
    data['question4'] = top10qa.question4
    top10qaScore = LaboremTOP10Score.objects.filter(user=request.user, TOP10QA=top10qa, active=True)
    if len(top10qaScore) > 0:
        top10qaScoreFirst = top10qaScore.first()
        data['answer1'] = top10qaScoreFirst.answer1
        data['answer2'] = top10qaScoreFirst.answer2
        data['answer3'] = top10qaScoreFirst.answer3
        data['answer4'] = top10qaScoreFirst.answer4
        data['disable'] = 1
        logger.debug("top10qa %s already done by %s" % (top10qa, request.user))
    return HttpResponse(json.dumps(data), content_type='application/json')


@unauthenticated_redirect
def validate_top10_answers(request):
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

    plug, sub_plug = LaboremMotherboardDevice.objects.get(pk=mb_id).get_selected_plug()
    if plug is None:
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

    if plug.robot is None:
        r_v_1 = None
        r_u_1 = None
        r_v_2 = None
        r_u_2 = None
    elif LaboremRobotBase.objects.get(name="baseVert").element is not None \
            and LaboremRobotBase.objects.get(name="baseRouge").element is not None:
        r_v_1 = LaboremRobotBase.objects.get(name="baseVert").element.value
        r_u_1 = LaboremRobotBase.objects.get(name="baseVert").element.unit
        r_v_2 = LaboremRobotBase.objects.get(name="baseRouge").element.value
        r_u_2 = LaboremRobotBase.objects.get(name="baseRouge").element.unit
    else:
        r_v_1 = None
        r_u_1 = None
        r_v_2 = None
        r_u_2 = None
    top10qa = LaboremTOP10.objects.filter(page__link_title=page, plug=plug, sub_plug=sub_plug,
                                          robot_base1__value=r_v_1,
                                          robot_base1__unit=r_u_1,
                                          robot_base2__value=r_v_2,
                                          robot_base2__unit=r_u_2).order_by('id').first()

    if top10qa is None:
        return HttpResponse(status=404)
    if top10qa.question1:
        note += calculate_note(level_plug, top10qa.score1, top10qa.answer1, request.POST['value1'])
    if top10qa.question2:
        note += calculate_note(level_plug, top10qa.score2, top10qa.answer2, request.POST['value2'])
    if top10qa.question3:
        note += calculate_note(level_plug, top10qa.score3, top10qa.answer3, request.POST['value3'])
    if top10qa.question4:
        note += calculate_note(level_plug, top10qa.score4, top10qa.answer4, request.POST['value4'])
    score = LaboremTOP10Score(user=request.user, TOP10QA=top10qa, note=note,
                              answer1=request.POST['value1'] if 'value1' in request.POST else None,
                              answer2=request.POST['value2'] if 'value2' in request.POST else None,
                              answer3=request.POST['value3'] if 'value3' in request.POST else None,
                              answer4=request.POST['value4'] if 'value4' in request.POST else None)
    score.save()
    if top10qa.question1:
        note_max += calculate_note(level_plug, top10qa.score1, top10qa.answer1, top10qa.answer1)
    if top10qa.question2:
        note_max += calculate_note(level_plug, top10qa.score2, top10qa.answer2, top10qa.answer2)
    if top10qa.question3:
        note_max += calculate_note(level_plug, top10qa.score3, top10qa.answer3, top10qa.answer3)
    if top10qa.question4:
        note_max += calculate_note(level_plug, top10qa.score4, top10qa.answer4, top10qa.answer4)
    VariableProperty.objects.update_or_create_property(Variable.objects.get(name="LABOREM"), "message_laborem",
                                                       "Vous avez eu " + str(round(note, 2)) + "/" + str(note_max),
                                                       value_class='string', timestamp=now())
    time.sleep(3)
    VariableProperty.objects.update_or_create_property(Variable.objects.get(name="LABOREM"), "message_laborem",
                                                       "", value_class='string', timestamp=now())
    return HttpResponse(status=200)


def calculate_note(level, score, answer, student_answer):
    try:
        answer = float(str(answer).replace(',', '.'))
        student_answer = float(str(student_answer).replace(',', '.'))
    except ValueError:
        logger.error("TOP10 answer is not a float : %s - %s" % (answer, student_answer))
    # return level * np.exp(-abs(1-float(student_answer.replace(',', '.'))/float(answer.replace(',', '.')))*2)
    note = 0
    high_limit = 0.1
    low_limit = 0.25
    if answer == 0.0:
        if student_answer == 0.0:
            note = level * score
            return note
        else:
            temp_answer = answer
            answer = student_answer
            student_answer = temp_answer
    if abs(1-student_answer/answer) <= high_limit:
        note = level * score
    elif abs(student_answer - answer) <= 0.1:
        note = level * score
    elif abs(1-student_answer/answer) <= low_limit or abs(student_answer - answer) <= 1:
        note = level * score * max((abs(1-student_answer/answer) - low_limit) / (high_limit - low_limit),
                                   (1 - abs(student_answer - answer)))
    return note
    # return min(level * np.exp(-abs(1-float(student_answer.replace(',', '.'))/float(answer.replace(',', '.')))+0.2),
    #           level) * score


@unauthenticated_redirect
def rank_top10(request):
    time.sleep(2)
    LaboremTOP10Ranking.objects.all().delete()
    for user in LaboremTOP10Score.objects.values_list('user').distinct():
        score_total = 0
        found = False
        for item in LaboremTOP10Score.objects.filter(user=user, active=True).values_list('TOP10QA').distinct():
            score_total += LaboremTOP10Score.objects.filter(user=user, TOP10QA=item, active=True).order_by('id').first().note
            found = True
        if found:
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


@unauthenticated_redirect
def reset_robot_bases(request):
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).move_robot:
                for base in LaboremRobotBase.objects.all():
                    base.change_requested_element(None)
                return HttpResponse(status=200)
    return HttpResponse(status=200)


@unauthenticated_redirect
def reset_selected_plug(request):
    if 'mb_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
    else:
        logger.debug("mb_id not in request.POST for reset_selected_plug fonction. Request : %s" % request)
        return HttpResponse(status=404)
    if LaboremGroupInputPermission.objects.count() > 0:
        plug_selected = Variable.objects.get(name="plug_selected")
        if LaboremGroupInputPermission.objects.filter(
                hmi_group__in=request.user.groups.exclude(name='teacher').iterator(),
                variables__pk=plug_selected.pk):
            try:
                LaboremMotherboardDevice.objects.get(pk=mb_id).change_selected_plug(0)
                logger.debug("Reset selected plug - user %s - mb_id %s" % (request.user, mb_id))
            except LaboremMotherboardDevice.DoesNotExist:
                logger.error("request : %s - mb_id : %s" % (request, mb_id))
            return HttpResponse(status=200)
    return HttpResponse(status=200)


@unauthenticated_redirect
def move_robot(request):
    data = dict()
    if LaboremGroupInputPermission.objects.count() > 0:
        for group in request.user.groups.iterator():
            if LaboremGroupInputPermission.objects.get(hmi_group=group).move_robot:
                try:
                    variable = Variable.objects.get(name="LABOREM")
                except Variable.DoesNotExist:
                    return HttpResponse(status=200)
                vp = VariableProperty.objects.get_property(variable=variable, name="ROBOT_PUT_ON")
                if vp is None:
                    return HttpResponse(status=200)
                key = vp.id
                for base in LaboremRobotBase.objects.all():
                    if base.element is not None and str(base.element.active) == '0':
                        VariableProperty.objects.update_or_create_property(Variable.objects.get(name="LABOREM"),
                                                                           "message_laborem",
                                                                           "Le robot place les éléments...",
                                                                           value_class='string',
                                                                           timestamp=now())
                        data['message_laborem'] = {}
                        data['message_laborem']['message'] = "Le robot place les éléments..."
                        data['message_laborem']['timestamp'] = int(format(now(), 'U')) * 1000
                cwt = DeviceWriteTask(variable_property_id=key, value=1, start=time.time(), user=request.user)
                cwt.create_and_notificate(cwt)
                return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse(status=200)


@unauthenticated_redirect
def remove_id(request):
    if 'connection_id' in request.POST:
        LaboremUser.objects.update_or_create(user=request.user,
                                             defaults={'connection_id': request.POST['connection_id']})
    else:
        LaboremUser.objects.update_or_create(user=request.user, defaults={'connection_id': None})
    return HttpResponse(status=200)


@unauthenticated_redirect
def check_time(request):
    time_before_remove_id = 5
    data = dict()
    data['setTimeout'] = 1000
    u = LaboremUser.objects.get(user=request.user)
    uid = uuid4().hex
    if 'connection_id' in request.POST and request.POST['connection_id'] != "":
        if u.connection_id == request.POST['connection_id']:
            LaboremUser.objects.update_or_create(user=request.user, defaults={'last_check': now})
            data['connection_accepted'] = "1"
        elif str(u.connection_id) == "" or u.connection_id is None:
            LaboremUser.objects.update_or_create(user=request.user,
                                                 defaults={'last_check': now,
                                                           'connection_id': request.POST['connection_id']})
            data['connection_accepted'] = "1"
            # data['connection_id'] = request.POST['connection_id']
        else:
            LaboremUser.objects.filter(user=request.user,
                                       last_check__lte=now() - timedelta(seconds=time_before_remove_id)). \
                exclude(laborem_group_input__hmi_group__name="teacher"). \
                update(last_check=now(), connection_id=str(request.POST['connection_id']))
            # LaboremUser.objects.update_or_create(user=request.user, defaults={'last_check': now})
            data['connection_accepted'] = "0"
    else:
        if str(u.connection_id) == "" or u.connection_id is None:
            LaboremUser.objects.update_or_create(user=request.user, defaults={'last_check': now,
                                                                              'connection_id': uid})
            data['connection_accepted'] = "1"
            data['connection_id'] = uid
        else:
            LaboremUser.objects.filter(user=request.user,
                                       last_check__lte=now() - timedelta(seconds=time_before_remove_id)). \
                exclude(laborem_group_input__hmi_group__name="teacher"). \
                update(last_check=now(), connection_id=uid)
            # LaboremUser.objects.update_or_create(user=request.user, defaults={'last_check': now})
            data['connection_accepted'] = "0"
            data['connection_id'] = uid
    return HttpResponse(json.dumps(data), content_type='application/json')


@unauthenticated_redirect
def check_users(request):
    if 'mb_id' in request.POST:
        mb_id = int(request.POST['mb_id'])
    else:
        logger.debug("mb_id not in request.POST for check_user fonction. Request : %s" % request)
        return HttpResponse(status=404)
    data = dict()

    # Laborem group
    data['user_type'] = \
        str(request.user.groups.exclude(name='teacher').first()) \
        if request.user.groups.exclude(name='teacher').first() is not None else "none"

    '''
    if request.user.groups.all().first() == Group.objects.get(name="viewer"):
        data['user_type'] = "viewer"
    elif request.user.groups.all().first() == Group.objects.get(name="worker"):
        data['user_type'] = "worker"
    elif request.user.groups.all().first() == Group.objects.get(name="teacher"):
        data['user_type'] = "teacher"
    elif request.user.groups.all().first() is None:
        data['user_type'] = "none"
    '''

    # Define timeline on user click or user connect
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

    # Send message for robot, experience or laborem state
    try:
        vp = VariableProperty.objects.get_property(Variable.objects.get(name="LABOREM"), "message_laborem")
        data['message_laborem'] = {}
        data['message_laborem']['message'] = vp.value_string
        data['message_laborem']['timestamp'] = int(format(vp.timestamp, 'U')) * 1000
    except (Variable.DoesNotExist, AttributeError):
        data['message_laborem'] = {}
        data['message_laborem']['message'] = ''
        data['message_laborem']['timestamp'] = ''

    # Change the % of the progress bar for the MessageModal
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

    # Send viewer list
    # LaboremUser.objects.update_or_create(user=request.user, defaults={'last_check': now})
    data['request_user'] = str(request.user)
    if Variable.objects.filter(name="LABOREM").count() and VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "working_time") is not None:
        td = timedelta(minutes=int(VariableProperty.objects.get_property(Variable.objects.get(
            name="LABOREM"), "working_time").value_int16))
    else:
        td = 0
    waiting_users_list = LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").\
        order_by('connection_time')
    working_user = LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker").first()
    if working_user is not None:
        data['active_user'] = {}
        data['active_user']['name'] = str(working_user.user.username)
        data['active_user']['min'] = str((td - (now() - working_user.start_time)).seconds // 60)
        data['active_user']['sec'] = str((td - (now() - working_user.start_time)).seconds % 60)
        wu = 1
        data['waiting_users'] = {}
        # data['waiting_users'][0] = waiting_users_list.count()
        for waiting_user in waiting_users_list:
            data['waiting_users'][wu] = {}
            data['waiting_users'][wu]['username'] = str(waiting_user.user.username)
            data['waiting_users'][wu]['min'] = \
                str((td - (now() - working_user.start_time) + (wu - 1) * td).seconds // 60)
            data['waiting_users'][wu]['sec'] = \
                str((td - (now() - working_user.start_time) + (wu - 1) * td).seconds % 60)
            wu += 1
    try:
        selected_plug, selected_sub_plug = LaboremMotherboardDevice.objects.get(pk=mb_id).get_selected_plug()
        data['plug'] = {}
        data['plug']['name'] = ""
        data['plug']['description'] = ""
        if selected_plug is not None:
            data['plug']['name'] = selected_plug.name
            if selected_sub_plug is not None:
                data['plug']['name'] += " " + selected_sub_plug.sub_name
            data['plug']['description'] = selected_plug.description

            if selected_plug.robot:
                data['plug']['robot'] = "true"
                data['plug']['base'] = {}
                for base in LaboremRobotBase.objects.all():
                    if base.element is not None:
                        data['plug']['base'][base.description] = base.element.__str__()
            else:
                data['plug']['robot'] = "false"
    except (LaboremMotherboardDevice.DoesNotExist, AttributeError, TypeError):
        pass
    try:
        experience = VariableProperty.objects.get_property(Variable.objects.get(name="LABOREM"),
                                                           "EXPERIENCE").value_string.lower()
        if experience != "":
            data['experience'] = experience
    except (Variable.DoesNotExist, AttributeError):
        pass

    try:
        viewer_quantity = VariableProperty.objects.get_property(Variable.objects.get(name="LABOREM"),
                                                                "VIEWER_QUANTITY").value()
        if viewer_quantity is not None:
            data['viewer_quantity'] = viewer_quantity
        else:
            data['viewer_quantity'] = 1
    except (Variable.DoesNotExist, AttributeError):
        data['viewer_quantity'] = 1

    return HttpResponse(json.dumps(data), content_type='application/json')


@unauthenticated_redirect
def get_experience_list(request):
    if LaboremGroupInputPermission.objects.count() == 0:
        visible_experience_list = LaboremExperience.objects.all().values_list('pk', flat=True)
    else:
        visible_experience_list = LaboremExperience.objects.filter(laboremgroupinputpermission__hmi_group__in=request.
                                                                   user.groups.exclude(name='teacher').
                                                                   iterator()).values_list('pk', flat=True)
    data = dict()
    for e in visible_experience_list:
        if e is not None:
            data[LaboremExperience.objects.get(pk=e).page.link_title] = LaboremExperience.objects.get(pk=e).page.title
    return HttpResponse(json.dumps(data), content_type='application/json')

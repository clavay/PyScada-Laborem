#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
handles write tasks for variables attached to the generic devices
"""

from pyscada.laborem.models import LaboremUser, LaboremGroupInputPermission
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User, Group
import logging

logger = logging.getLogger(__name__)


def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """
    pass


def shutdown(self):
    """
    write your code shutdown code here, don't change the name of this function
    :return:
    """
    pass


def script(self):
    """
    write your code loop code here, don't change the name of this function
    :return:
    """
    # check if the 3 groups exist
    if LaboremGroupInputPermission.objects.filter(hmi_group__name="viewer").count() and \
            LaboremGroupInputPermission.objects.filter(hmi_group__name="worker").count() and \
            LaboremGroupInputPermission.objects.filter(hmi_group__name="teacher").count():
        # do not touch the teachers
        # remove group from users with check > 12 sec
        LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=12)).\
            exclude(laborem_group_input__hmi_group__name="teacher").update(laborem_group_input=None, start_time=None)
        # move worker to viewer if start > 5 min and viewer list count > 0
        # if no viewer, actualize the start time each time
        if LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").count() > 0:
            LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker",
                                       start_time__lte=now() - timedelta(minutes=5)).\
                update(laborem_group_input=None, start_time=None, connection_time=now())
        else:
            LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker").update(start_time=now())
        # if no worker take the first viewer by waiting time
        if LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker").count() == 0:
            if LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").count() > 0:
                lu = LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").\
                    order_by("connection_time").first()
                lu.laborem_group_input = LaboremGroupInputPermission.objects.filter(hmi_group__name="worker").first()
                lu.start_time = now()
                lu.save()
        # move the without group in viewer if check < 12 sec
        LaboremUser.objects.filter(laborem_group_input=None, last_check__gte=now() - timedelta(seconds=12)).\
            exclude(laborem_group_input__hmi_group__name="teacher").\
            update(laborem_group_input=LaboremGroupInputPermission.objects.get(hmi_group__name="viewer"))

        # update the user group to the group selected in LaboremUser
        for U in User.objects.all():
            try:
                if U.groups.all().first() != LaboremUser.objects.get(user=U).laborem_group_input.hmi_group:
                    U.groups.clear()
                    U.groups.add(LaboremUser.objects.get(user=U).laborem_group_input.hmi_group)
                    U.save()
            except LaboremUser.DoesNotExist:
                pass
            except AttributeError:
                pass
    else:
        logger.info("Please create the 3 groups for the user list")

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
handles write tasks for variables attached to the generic devices
"""

from pyscada.laborem.models import LaboremUser, LaboremGroupInputPermission, LaboremRobotBase
from pyscada.models import Variable, VariableProperty
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User, Group
import logging
from datetime import datetime

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
    time_before_remove_group = 12
    # check if the 3 groups exist
    if LaboremGroupInputPermission.objects.filter(hmi_group__name="viewer").count() and \
            LaboremGroupInputPermission.objects.filter(hmi_group__name="worker").count() and \
            LaboremGroupInputPermission.objects.filter(hmi_group__name="teacher").count():
        # do not touch the teachers
        # move the without group in viewer if check < time_before_remove_group sec
        LaboremUser.objects.filter(laborem_group_input=None,
                                   last_check__gte=now() - timedelta(seconds=time_before_remove_group)).\
            exclude(laborem_group_input__hmi_group__name="teacher").\
            update(laborem_group_input=LaboremGroupInputPermission.objects.get(hmi_group__name="viewer"),
                   connection_time=now())
        # remove group from users with check > time_before_remove_group sec
        if LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group)).exclude(
                laborem_group_input__hmi_group__name="teacher").exclude(laborem_group_input=None):
            logger.debug("users with check > %s sec : %s" % (time_before_remove_group,
                         LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group)).
                         exclude(laborem_group_input__hmi_group__name="teacher").exclude(laborem_group_input=None)))
            for u in LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group)).exclude(
                    laborem_group_input__hmi_group__name="teacher").exclude(laborem_group_input=None):
                logger.debug("user %s - timedelta %s" % (u.user, now() - u.last_check))
        LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group)).\
            exclude(laborem_group_input__hmi_group__name="teacher").\
            update(laborem_group_input=None, start_time=None, connection_id=None)
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
                for base in LaboremRobotBase.objects.all():
                    if base.element is not None and str(base.element.active) != '0':
                        lu.start_time += timedelta(seconds=20)
                lu.save()
                logger.debug("New worker : %s" % lu.user)
                self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                             timestamp=datetime.utcnow())
                self.write_variable_property("LABOREM", "USER_STOP", 1, value_class="BOOLEAN")
                self.write_variable_property("LABOREM", "ROBOT_TAKE_OFF", 1, value_class="BOOLEAN")
                reset_all_vp_of_a_var(self, "BODE_RUN")
                reset_all_vp_of_a_var(self, "SPECTRE_RUN")

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
        logger.error("Please create the 3 groups for the user list")


def reset_all_vp_of_a_var(self, variable_name):
    if variable_name in self.variables:
        variable = self.variables[variable_name]
    else:
        variable = Variable.objects.filter(name=variable_name).first()
    for vp in VariableProperty.objects.filter(variable=variable):
        VariableProperty.objects.update_property(variable_property=vp, variable=variable)

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
handles write tasks for variables attached to the generic devices
"""

from pyscada.laborem.models import LaboremUser, LaboremGroupInputPermission, LaboremRobotBase, LaboremMotherboardDevice
from pyscada.models import Variable, VariableProperty
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User, Group
from django.db.models import F, Q
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
    LaboremMotherboardDevice.objects.first().relay(0)
    pass


def script(self):
    """
    write your code loop code here, don't change the name of this function
    :return:
    """
    time_before_remove_group = 30
    working_time = VariableProperty.objects.get_property(Variable.objects.get(
        name="LABOREM"), "working_time").value_int16
    # check if the 3 groups exist
    if LaboremGroupInputPermission.objects.filter(Q(hmi_group__name="viewer") | Q(hmi_group__name="worker") |
                                                  Q(hmi_group__name="teacher")).count() == 3:
        # do not touch the teachers
        # move the without group in viewer if check < time_before_remove_group sec
        LaboremUser.objects.filter(laborem_group_input=None,
                                   last_check__gte=now() - timedelta(seconds=time_before_remove_group)).\
            update(laborem_group_input=LaboremGroupInputPermission.objects.get(hmi_group__name="viewer"),
                   connection_time=now())
        # remove group from users with check > time_before_remove_group sec
        '''
        if LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group)).exclude(
                laborem_group_input__hmi_group__name="teacher").exclude(laborem_group_input=None):
            logger.debug("users with check > %s sec : %s" % (time_before_remove_group,
                         LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group))
                                                             .exclude(laborem_group_input__hmi_group__name="teacher").
                                                             exclude(laborem_group_input=None)))
            for u in LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group)).\
                    exclude(laborem_group_input__hmi_group__name="teacher").exclude(laborem_group_input=None):
                logger.debug("user %s - timedelta %s" % (u.user, now() - u.last_check))
        '''
        LaboremUser.objects.filter(last_check__lte=now() - timedelta(seconds=time_before_remove_group)).\
            exclude(laborem_group_input__hmi_group__name="teacher").\
            update(laborem_group_input=None, start_time=None, connection_id=None)
        # move worker to viewer if start > working_time min and viewer list count > 0
        # if no viewer, actualize the start time each time
        if LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").count() > 0:
            # Someone connected, switch on relay
            LaboremMotherboardDevice.objects.first().relay(1)
            LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker",
                                       start_time__lte=now() - timedelta(minutes=working_time)).\
                update(laborem_group_input=None, start_time=None, connection_time=now())
        else:
            LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker").update(start_time=now())
        # if no worker take the first viewer by waiting time
        if LaboremUser.objects.filter(laborem_group_input__hmi_group__name="worker").count() == 0:
            if LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").count() > 0:
                reset_laborem_on_user_or_session_change(self)
                lu = LaboremUser.objects.filter(laborem_group_input__hmi_group__name="viewer").\
                        order_by("connection_time").first()
                lu.laborem_group_input = LaboremGroupInputPermission.objects.filter(hmi_group__name="worker").first()
                lu.start_time = now()
                for base in LaboremRobotBase.objects.all():
                    if base.element is not None and str(base.element.active) != '0':
                        lu.start_time += timedelta(seconds=20)
                lu.save()
            else:
                # Nobody connected, switch off relay
                LaboremMotherboardDevice.objects.first().relay(0)
        else:
            # Someone connected, switch on relay
            LaboremMotherboardDevice.objects.first().relay(1)

        # set viewer group for empty user.group
        try:
            User.objects.filter(groups__isnull=True).first().groups.add(Group.objects.get(name="viewer"))
        except User.DoesNotExist:
            pass
        except AttributeError:
            pass
        try:
            User.objects.filter(groups__name__startswith="teacher").exclude(groups__name__startswith="worker")\
                .exclude(groups__name__startswith="viewer").first().groups.add(Group.objects.get(name="viewer"))
        except User.DoesNotExist:
            pass
        except AttributeError:
            pass

        # remove worker user group if not in LaboremUser
        for U in User.objects.exclude(laboremuser__laborem_group_input__hmi_group__name="worker")\
                .filter(groups__name__startswith="worker"):
            try:
                U.groups.remove(Group.objects.get(name='worker'))
                # logger.debug("User with different laborem group : %s" % U)
            except LaboremUser.DoesNotExist:
                pass
            except AttributeError:
                pass
        for U in User.objects.filter(laboremuser__laborem_group_input__hmi_group__name="worker") \
                .exclude(groups__name__startswith="worker"):
            U.groups.add(U.laboremuser.laborem_group_input.hmi_group)
    else:
        logger.error("Please create the 3 groups for the user list")
    # logger.debug("Total time : %s - start : %s - without group to viewer : %s - remove group : %s -
    #             move to worker or actualize time : %s - take first viewer to worker : %s - "
    #             "update user group to the laborem group : %s"
    #             % (t7-t1, round((t2-t1)*100/(t7-t1)), round((t3-t2)*100/(t7-t1)), round((t4-t3)*100/(t7-t1)),
    #                round((t5-t4)*100/(t7-t1)), round((t6-t5)*100/(t7-t1)), round((t7-t6)*100/(t7-t1))))


def reset_laborem_on_user_or_session_change(self):
    self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                 timestamp=now())
    self.write_variable_property("LABOREM", "USER_STOP", 1, value_class="BOOLEAN")
    #self.write_variable_property("LABOREM", "ROBOT_TAKE_OFF", 1, value_class="BOOLEAN")
    reset_all_vp_of_a_var(self, "BODE_RUN")
    reset_all_vp_of_a_var(self, "SPECTRE_RUN")


def reset_all_vp_of_a_var(self, variable_name):
    if variable_name in self.variables:
        variable = self.variables[variable_name]
    else:
        variable = Variable.objects.filter(name=variable_name).first()
    for vp in VariableProperty.objects.filter(variable=variable):
        VariableProperty.objects.update_property(variable_property=vp, variable=variable)

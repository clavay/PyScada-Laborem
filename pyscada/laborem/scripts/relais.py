#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import time
# from pyscada.models import Device
from pyscada.laborem.models import LaboremMotherboardDevice

logger = logging.getLogger(__name__)


def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """
    #os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"
    #os.environ["PIGPIO_ADDR"] = "10.3.205.173"
    try:
        from gpiozero import LED
        # TODO: Keep the GPIO config in DB. Add gpiozero to the GPIO model
        self.d = {0: LED(5),
                  1: LED(6),
                  2: LED(13),
                  3: LED(19),
                  4: LED(26)}  # in my opinion this is more reliable
        self.d[4].on()
    except Exception as e:
        logger.error("Error importing gpiozero in script - Exception : %s" % e)


def shutdown(self):
    """
    write your code shutdown code here, don't change the name of this function
    :return:
    """
    # Wait for the robot to go to a safe position
    time.sleep(5)


def script(self):
    """
    write your code loop code here, don't change the name of this function
    :return:
    """

    try:
        from gpiozero import LED
#        device_laborem = Device.objects.get(pk=8)
#        plug_selected = int(device_laborem.laboremmotherboarddevice.plug)
        device_laborem = LaboremMotherboardDevice.objects.first()
        plug_selected = int(device_laborem.plug)

        if plug_selected:
            plug_selected = plug_selected - 1
            for i in range(0, 4):
                if int(bin(plug_selected)[2:].zfill(4)[4 - i - 1:4 - i]):
                    self.d[i].on()
                else:
                    self.d[i].off()
    except:
        pass

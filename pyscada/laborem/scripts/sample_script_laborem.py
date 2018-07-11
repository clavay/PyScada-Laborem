#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pyscada.models import Device
from pyscada.laborem.models import LaboremMotherboardDevice, LaboremRobotBase
import logging
import visa
import time
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)


def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """
    os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"
    os.environ["PIGPIO_ADDR"] = "10.3.205.173"
    try:
        from gpiozero import LED
    except:
        logger.error("Error importing gpiozero in script")
    device_laborem = Device.objects.get(pk=10)
    plug_selected = device_laborem.laboremmotherboarddevice.plug
    #plug_selected = int(self.read_variable_property(variable_name='BODE_RUN', property_name='BODE_PLUG'))

    # TODO: Keep the GPIO config in DB. Add gpiozero to the GPIO model
    d = []
    d.append(LED(5))
    d.append(LED(6))
    d.append(LED(13))
    d.append(LED(19))
    d.append(LED(26))
    relay = d[4]
    #relay.on()
    logger.info("Plug selected : %s" % (plug_selected))
    '''for i in range(0, 4):
        if bin(plug_selected)[2:].zfill(4)[i:i+1]:
            d[i].on()
        else:
            d[i].off()
'''
    visa_backend = '@py'  # use PyVISA-py as backend
    if hasattr(settings, 'VISA_BACKEND'):
        visa_backend = settings.VISA_BACKEND
    device_mdo = Device.objects.get(pk=3)
    device_afg = Device.objects.get(pk=2)
    device_dmm = Device.objects.get(pk=1)
    # device_robot = Device.objects.get(pk=7)

    try:
        self.rm = visa.ResourceManager(visa_backend)
    except:
        logger.error("Visa ResourceManager cannot load resources : %s" % self)
        return False
    try:
        resource_prefix = device_mdo.visadevice.resource_name.split('::')[0]
        extras = {}
        if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
            if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
        logger.debug('VISA_DEVICE_SETTINGS for %s: %r' % (resource_prefix, extras))
        self.inst_mdo = self.rm.open_resource(device_mdo.visadevice.resource_name, **extras)
        if self.inst_mdo is not None:
            logger.debug('Connected visa device : %s' % device_mdo.__str__())
        else:
            logger.debug('NOT connected visa device : %s' % device_mdo.__str__())
    except:
        logger.error("Visa ResourceManager cannot open resource : %s" % device_mdo.__str__())
        pass
    try:
        resource_prefix = device_afg.visadevice.resource_name.split('::')[0]
        extras = {}
        if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
            if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
        logger.debug('VISA_DEVICE_SETTINGS for %s: %r' % (resource_prefix, extras))
        self.inst_afg = self.rm.open_resource(device_afg.visadevice.resource_name, **extras)
        if self.inst_afg is not None:
            logger.debug('Connected visa device : %s' % device_afg.__str__())
        else:
            logger.debug('NOT connected visa device : %s' % device_afg.__str__())
    except:
        logger.error("Visa ResourceManager cannot open resource : %s" % device_afg.__str__())
        pass
    try:
        resource_prefix = device_dmm.visadevice.resource_name.split('::')[0]
        extras = {}
        if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
            if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
        logger.debug('VISA_DEVICE_SETTINGS for %s: %r' % (resource_prefix, extras))
        self.inst_dmm = self.rm.open_resource(device_dmm.visadevice.resource_name, **extras)
        if self.inst_dmm is not None:
            logger.debug('Connected visa device : %s' % device_dmm.__str__())
        else:
            logger.debug('NOT connected visa device : %s' % device_dmm.__str__())
    except:
        logger.error("Visa ResourceManager cannot open resource : %s" % device_dmm.__str__())
        pass
    '''try:
        resource_prefix = device_robot.visadevice.resource_name.split('::')[0]
        extras = {}
        if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
            if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
        logger.debug('VISA_DEVICE_SETTINGS for %s: %r' % (resource_prefix, extras))
        self.inst_robot = self.rm.open_resource(device_afg.visadevice.resource_name, **extras)
        if self.inst_robot is not None:
            logger.debug('Connected visa device : %s' % device_robot.__str__())
        else:
            logger.debug('NOT connected visa device : %s' % device_robot.__str__())
    except:
        logger.error("Visa ResourceManager cannot open resource : %s" % device_robot.__str__())
        pass
    '''
    return True


def shutdown(self):
    """
    write your code shutdown code here, don't change the name of this function
    :return:
    """
    try:
        if self.inst_mdo is not None:
            self.inst_mdo.close()
            self.inst_mdo = None
    except AttributeError:
        pass
    try:
        if self.inst_afg is not None:
            self.inst_afg.close()
            self.inst_afg = None
    except AttributeError:
        pass
    try:
        if self.inst_dmm is not None:
            self.inst_dmm.close()
            self.inst_dmm = None
    except AttributeError:
        pass
    try:
        if self.inst_robot is not None:
            self.inst_robot.close()
            self.inst_robot = None
    except AttributeError:
        pass
    return True


def script(self):
    """
    write your code loop code here, don't change the name of this function

    :return:
    """
    # logger.info("Script Bode running...")
    init_bode = bool(self.read_variable_property(variable_name='Bode_run', property_name='Bode_init'))
    if init_bode:
        logger.info("Init Bode running...")
        self.write_variable_property(variable_name='Bode_run', property_name='Bode_init', value=0,
                                     value_class='BOOLEAN')
        vepp = self.read_variable_property(variable_name='Bode_run', property_name='Bode_Vepp')
        self.inst_afg.write('*RST;OUTPut1:STATe ON;OUTP1:IMP MAX;SOUR1:AM:STAT OFF;SOUR1:FUNC:SHAP SIN;SOUR1:'
                            'VOLT:LEV:IMM:AMPL ' + str(vepp) + 'Vpp')
        self.inst_dmm.write('*RST;:FUNC "VOLTage:AC";:VOLTage:AC:RANGe:AUTO 1;:VOLTage:AC:RESolution MIN;:TRIG:DEL MIN')
        self.inst_mdo.write('*RST;:SEL:CH1 1;:SEL:CH2 1;:HORIZONTAL:POSITION 0;:CH1:YUN "V";:CH1:SCALE ' +
                            str(1.2 * float(vepp) / (2 * 4)) + ';:CH2:YUN "V";:CH2:BANdwidth 10000000;:'
                            'CH1:BANdwidth 10000000;:TRIG:A:TYP EDGE;:TRIG:A:EDGE:COUPLING DC;:TRIG:A:EDGE:SOU CH1;'
                            ':TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM')
        # Move the robot
        for base in LaboremRobotBase.objects.all():
            R = base.element.R
            theta = base.element.theta
            z = base.element.z
            l_epaule = 11.5
            l_coude = 14.8
            l_poignet = 8.8
            offset_base = 11.3
            z2 = z + l_poignet + offset_base
            angle_coude = min(
                max(np.arccos((R ** 2 + z2 ** 2 - (l_epaule ** 2 + l_coude ** 2)) /
                              (2 * l_epaule * l_coude * (R**2 + z2**2)**0.5))*180/np.pi, -125), 25)
            angle_epaule = min(max(np.arctan2((z2 * (l_epaule + l_coude * np.cos(angle_coude)) -
                                               R * l_coude * np.sin(angle_coude)),
                                              (z2 * (l_epaule + l_coude * np.cos(angle_coude)) +
                                               R * l_coude * np.sin(angle_coude)))*180/np.pi, -43), 43)
            angle_poignet = min(max(180 - angle_coude - angle_epaule, -90), 90)
            angle_base = min(max(theta, -180), 180)
            rot_e = angle_epaule*511/180
            rot_c = angle_coude*511/180
            rot_p = angle_poignet*511/180
            rot_b = angle_base*511/180
            logger.info("%s %s %s %s %s %s %s %s %s %s %s %s" % (R, theta, z, z2, l_epaule, l_coude, l_poignet,
                                                                 offset_base, angle_epaule, angle_coude,
                                                                 angle_poignet, angle_base))
            logger.info("%s %s %s %s" % (rot_e, rot_c, rot_p, rot_b))

    loop = bool(self.read_variable_property(variable_name='Bode_run', property_name='Bode_loop'))
    if loop:
        logger.info("Loop Bode running...")
        self.write_variable_property(variable_name='Bode_run', property_name='Bode_loop', value=0,
                                     value_class='BOOLEAN')
        fmin = self.read_variable_property(variable_name='Bode_run', property_name='Bode_Fmin')
        fmax = self.read_variable_property(variable_name='Bode_run', property_name='Bode_Fmax')
        nb_points = self.read_variable_property(variable_name='Bode_run', property_name='Bode_nb_points')

        for f in np.geomspace(fmin, fmax, nb_points):
            # Set the generator to freq f
            self.inst_afg.write('SOUR1:FREQ:FIX ' + str(f))

            # Read from the multimeter the RMS value of the output
            i = 0
            i_max = 3  # Try X time max to read 3  vseff
            vseff = 0
            while i < i_max:
                try:
                    i += 1
                    time.sleep(0.3)
                    vseff = self.inst_dmm.query(':READ?')
                    break
                except Exception as e:
                    logger.error("Error reading multimeter : %s" % e)
            vsmax = float(vseff)*float(np.sqrt(2))
            mdo_horiz_scale = str(round(float(4.0 / (10.0 * float(f))), 6))
            mdo_ch2_scale = str(1.4 * float(vsmax) / 4.0)
            mdo_ch1_trig_level = str(0.8 * float(vsmax))
            logger.info("Freq = %s - horiz scale = %s - ch2 scale = %s - vsmax = %s - vseff = %s"
                        % (int(f), mdo_horiz_scale, mdo_ch2_scale, vsmax, vseff))

            # Set the oscilloscope horizontal scale and vertical scale for the output
            self.inst_mdo.write(':HORIZONTAL:SCALE ' + mdo_horiz_scale + ';:CH2:SCALE ' + mdo_ch2_scale +
                                ';:TRIG:A:LEV:CH1 ' + mdo_ch1_trig_level + ';:MEASUrement:IMMed:SOUrce1 CH1;'
                                ':MEASUrement:IMMed:SOUrce2 CH2;:MEASUREMENT:IMMed:TYPE PHASE')

            # Wait for the oscilloscope to show the signals
            time.sleep(20 / f)

            # Start reading the phase
            cmd_phase = str(':MEASUREMENT:IMMED:VALUE?')
            i = 0
            i_max = 3  # Try X time max to read 3 phases
            mean_phase = 999
            while i < i_max:
                i += 1
                phase = []
                for k in range(1, 4):
                    j = 0
                    j_max = 3  # Try X time max to read 1 phase
                    while j < j_max:
                        j += 1
                        phase_tmp = float(self.inst_mdo.query(cmd_phase))
                        if type(phase_tmp) == float:
                            phase.append(phase_tmp)
                            j = j_max
                        else:
                            logger.error('Phase is not float : %s' % phase_tmp)
                            time.sleep(0.1)
                    time.sleep(0.1)
                mean_phase = np.mean(phase)
                st_dev_phase = np.std(phase)
                # logger.info("Phase : %s - Mean : %s - StDev : %s" % (phase, mean_phase, st_dev_phase))
                if float(mean_phase < 200) and st_dev_phase < 3:
                    break

            # Start reading the gain
            cmd_p2p1 = str(':MEASUrement:IMMed:SOUrce1 CH1;:MEASUREMENT:IMMED:TYPE PK2PK;:MEASUREMENT:IMMED:VALUE?')
            cmd_p2p2 = str(':MEASUrement:IMMed:SOUrce1 CH2;:MEASUREMENT:IMMED:TYPE PK2PK;:MEASUREMENT:IMMED:VALUE?')
            i = 0
            i_max = 3  # Try X time max to read 2 pic to pic values
            gain = 999
            while i < i_max:
                p2p1_ok = False
                p2p2_ok = False
                p2p1 = float(self.inst_mdo.query(cmd_p2p1))
                if isinstance(p2p1, float):
                    p2p1_ok = True
                else:
                    logger.error('p2p1 is not float : %s' % p2p1)
                p2p2 = float(self.inst_mdo.query(cmd_p2p2))
                if isinstance(p2p2, float):
                    p2p2_ok = True
                else:
                    logger.error('p2p2 is not float : %s' % p2p2)
                i += 1
                if p2p1_ok and p2p2_ok:
                    gain = 20 * np.log10(p2p2/p2p1)
                    break
                else:
                    time.sleep(0.1)

            self.write_values_to_db(data={'Bode_Freq': [f], 'Bode_Gain': [gain], 'Bode_Phase': [mean_phase]})
        logger.info("Bode loop end")

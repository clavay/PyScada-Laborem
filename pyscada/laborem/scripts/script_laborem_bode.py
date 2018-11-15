#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyscada.models import Device
from pyscada.laborem.models import LaboremRobotBase
import logging
import visa
import time
from datetime import datetime
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)


###################################################
# This part is for the robot used in GIM IUT Anglet
###################################################

def take_and_drop(self, robot, r1, theta1, z1, r2, theta2, z2):
    # init
    pince(robot, 1)
    # prepare_epaule_coude_poignet(robot, 20, 5, 3)
    # rotation_base(self, robot, 0)
    # on place le bras pour prendre
    prepare_epaule_coude_poignet(robot, r1, z1, 1)
    # on tourne le bras pour prendre
    rotation_base(self, robot, theta1)
    # on ferme la pince
    pince(robot, 0)
    # on leve le bras
    prepare_epaule_coude_poignet(robot, r1, 4, 2)
    prepare_epaule_coude_poignet(robot, r2, 4, 1)
    # on tourne le bras pour déposer
    rotation_base(self, robot, theta2)
    # on place le bras pour deposer
    prepare_epaule_coude_poignet(robot, r2, sum([z2], 0.8), 3)
    # on ouvre la pince
    pince(robot, 1)
    # on se releve
    prepare_epaule_coude_poignet(robot, r2, 4, 2)
    # prepare_epaule_coude_poignet(robot, 20, 4, 3)
    rotation_base(self, robot, 0)


def format_ascii(rot_ascii, axe):
    if rot_ascii < 0:
        ret = axe + '-' + str(int(rot_ascii))[1:].zfill(3)
        print(ret)
        return ret
    else:
        ret = axe + '+' + str(int(rot_ascii)).zfill(3)
        print(ret)
        return ret


def deg_to_ascii(angle_deg, angle_max_deg):
    return int(min(max(angle_deg, -angle_max_deg), angle_max_deg) * 511 / angle_max_deg)


def prepare_epaule_coude_poignet(robot, r, z, mouvement):
    l_epaule = 11.5
    l_coude = 14.8
    l_poignet = 8.8
    l_base = 11

    angle_max_epaule = 43
    angle_max_coude = 125
    angle_max_poignet = 90

    correction_angle_poignet = 28.5

    temps_entre_cmd = 0.1

    xp = r
    yp = z - l_base + l_poignet

    r_alpha = (xp**2 + yp**2 - l_epaule**2 - l_coude**2)/(-2*l_epaule*l_coude)
    alpha = np.arccos(r_alpha)
    theta_coude = -np.pi + alpha

    theta_5 = np.arctan2(yp, xp) + np.arcsin(l_coude*np.sin(alpha)/(xp**2 + yp**2)**0.5)
    theta_epaule = -np.pi/4 + theta_5

    theta_poignet = -np.pi/2 - np.pi/4 - theta_epaule - theta_coude

    if mouvement == 1:
        robot.write(format_ascii(deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                              angle_max_poignet), 'F'))
        time.sleep(temps_entre_cmd)
        robot.write(format_ascii(deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
        time.sleep(temps_entre_cmd)
        robot.write(format_ascii(deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
        time.sleep(1)
    elif mouvement == 2:
        robot.write(format_ascii(deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
        time.sleep(temps_entre_cmd)
        robot.write(format_ascii(deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
        time.sleep(temps_entre_cmd)
        robot.write(format_ascii(deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                              angle_max_poignet), 'F'))
        time.sleep(1)
    elif mouvement == 3:
        robot.write(format_ascii(deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
        time.sleep(temps_entre_cmd)
        robot.write(format_ascii(deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
        time.sleep(temps_entre_cmd)
        robot.write(format_ascii(deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                              angle_max_poignet), 'F'))
        time.sleep(1)
    return True


def rotation_base(self, robot, theta):
    angle_max_base = 130
    theta_base = theta*np.pi/180
    robot.write(format_ascii(deg_to_ascii(theta_base*180/np.pi, angle_max_base), 'B'))
    try:
        old_theta = 0.0 - self.read_variable_property(variable_name='LABOREM', property_name='OLD_THETA')
        tempo = abs(sum([deg_to_ascii(theta_base*180/np.pi, angle_max_base), old_theta])) * 5000 / 1024
        time.sleep(tempo / 1000)
        self.write_variable_property(variable_name='LABOREM', property_name='OLD_THETA',
                                     value=deg_to_ascii(theta_base*180/np.pi, angle_max_base),
                                     value_class='INT32')
    except Exception as e:
        logger.warning("No old theta : %s" % e)
        time.sleep(3)
    return True


def pince(robot, openclose):
    if openclose == 0:
        robot.write('P+511')
        time.sleep(1.7)
    else:
        robot.write('P-511')
        time.sleep(1.7)
    return True


#######################
# End of the robot part
#######################

def startup(self):
    """
    write your code startup code here, don't change the name of this function
    :return:
    """

    # Wait for the instruments to wake up
    time.sleep(60)

    visa_backend = '@py'  # use PyVISA-py as backend
    if hasattr(settings, 'VISA_BACKEND'):
        visa_backend = settings.VISA_BACKEND
    device_mdo = Device.objects.get(pk=6)
    device_afg = Device.objects.get(pk=5)
    device_dmm = Device.objects.get(pk=4)
    device_robot = Device.objects.get(pk=1)

    try:
        self.rm = visa.ResourceManager(visa_backend)
    except Exception as e:
        logger.error("Visa ResourceManager cannot load resources : %s - Exception : %s" % (self, e))
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
    except Exception as e:
        logger.error("Visa ResourceManager cannot open resource : %s - Exception : %s" % (device_mdo.__str__(), e))
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
    except Exception as e:
        logger.error("Visa ResourceManager cannot open resource : %s - Exception : %s" % (device_afg.__str__(), e))
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
    except Exception as e:
        logger.error("Visa ResourceManager cannot open resource : %s - Exception : %s" % (device_dmm.__str__(), e))
        pass
    try:
        resource_prefix = device_robot.visadevice.resource_name.split('::')[0]
        extras = {}
        if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
            if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
        logger.debug('VISA_DEVICE_SETTINGS for %s: %r' % (resource_prefix, extras))
        self.inst_robot = self.rm.open_resource(device_robot.visadevice.resource_name, **extras)
        if self.inst_robot is not None:
            logger.debug('Connected visa device : %s' % device_robot.__str__())
        else:
            logger.debug('NOT connected visa device : %s' % device_robot.__str__())
    except Exception as e:
        logger.error("Visa ResourceManager cannot open resource : %s - Exception : %s" % (device_robot.__str__(), e))
        pass

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
        robot = self.inst_robot
        # on tourne le bras
        rotation_base(self, robot, 0)
        # on baisse le bras
        prepare_epaule_coude_poignet(robot, 17, 1, 2)
        if self.inst_robot is not None:
            self.inst_robot.close()
            self.inst_robot = None
    except AttributeError:
        pass
    except visa.VisaIOError:
        pass

    return True


def script(self):
    """
    write your code loop code here, don't change the name of this function

    :return:
    """
    # logger.debug("Script Bode running...")
    put_on_bode = bool(self.read_variable_property(variable_name='Bode_run', property_name='Bode_put_on'))
    if put_on_bode:
        logger.debug("Putting on Elements...")
        # Move the robot
        for base in LaboremRobotBase.objects.all():
            if base.element is None:
                r_element = base.element.R
                theta_element = base.element.theta
                z_element = base.element.z
                r_base = base.R
                theta_base = base.theta
                z_base = base.z
                take_and_drop(self, self.inst_robot, r_element, theta_element, z_element, r_base, theta_base, z_base)
            else:
                logger.debug("Base %s NOT empty" % base)
        self.write_variable_property(variable_name='Bode_run', property_name='Bode_put_on', value=0,
                                     value_class='BOOLEAN')

    take_off_bode = bool(self.read_variable_property(variable_name='Bode_run', property_name='Bode_take_off'))
    if take_off_bode:
        logger.debug("Taking off Elements...")
        for base in LaboremRobotBase.objects.all():
            if base.element is not None:
                r_element = base.element.R
                theta_element = base.element.theta
                z_element = base.element.z
                r_base = base.R
                theta_base = base.theta
                z_base = base.z
                take_and_drop(self, self.inst_robot, r_base, theta_base, z_base, r_element, theta_element, z_element)
                base.element = None
                base.save()
            else:
                logger.debug("Base %s empty" % base)
        self.write_variable_property(variable_name='Bode_run', property_name='Bode_take_off', value=0,
                                     value_class='BOOLEAN')

    bode = bool(self.read_variable_property(variable_name='Bode_run', property_name='BODE_5_LOOP'))
    if bode:
        logger.debug("Bode running...")
        self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                     timestamp=datetime.utcnow())
        vepp = min(max(self.read_variable_property(variable_name='Bode_run', property_name='BODE_1_VEPP'), 0), 19)
        self.inst_afg.write('*RST;OUTPut1:STATe ON;OUTP1:IMP MAX;SOUR1:AM:STAT OFF;SOUR1:FUNC:SHAP SIN;SOUR1:'
                            'VOLT:LEV:IMM:AMPL ' + str(vepp) + 'Vpp')
        self.inst_dmm.write('*RST;:FUNC "VOLTage:AC";:VOLTage:AC:RANGe:AUTO 1;:VOLTage:AC:RESolution MIN;:TRIG:DEL MIN')
        self.inst_mdo.write('*RST;:SEL:CH1 1;:SEL:CH2 1;:HORIZONTAL:POSITION 0;:CH1:YUN "V";:CH1:SCALE ' +
                            str(1.2 * float(vepp) / (2 * 4)) + ';:CH2:YUN "V";:CH2:BANdwidth 10000000;:'
                            ':CH1:BANdwidth 10000000;:TRIG:A:TYP EDGE;:TRIG:A:EDGE:COUPLING DC;:TRIG:A:EDGE:SOU CH1;'
                            ':TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM')
        fmin = min(max(self.read_variable_property(variable_name='Bode_run', property_name='BODE_2_FMIN'), 1), 200000)
        fmax = min(max(self.read_variable_property(variable_name='Bode_run', property_name='BODE_3_FMAX'), 1), 200000)
        nb_points = min(max(self.read_variable_property(variable_name='Bode_run', property_name='BODE_4_NB_POINTS'),
                            2), 20)

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
                    time.sleep(1)
                    vseff = self.inst_dmm.query(':READ?')
                    break
                except Exception as e:
                    logger.error("Error reading multimeter : %s" % e)
            vsmax = float(vseff)*float(np.sqrt(2))
            mdo_horiz_scale = str(round(float(4.0 / (10.0 * float(f))), 6))
            mdo_ch2_scale = str(1.4 * float(vsmax) / 4.0)
            logger.debug("Freq = %s - horiz scale = %s - ch2 scale = %s - vsmax = %s - vseff = %s"
                         % (int(f), mdo_horiz_scale, mdo_ch2_scale, vsmax, vseff))

            # Set the oscilloscope horizontal scale and vertical scale for the output
            self.inst_mdo.write(':HORIZONTAL:SCALE ' + mdo_horiz_scale + ';:CH2:SCALE ' + mdo_ch2_scale +
                                ';:TRIG:A:LEV:CH1 0;:MEASUrement:IMMed:SOUrce1 CH1;'
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
                # logger.debug("Phase : %s - Mean : %s - StDev : %s" % (phase, mean_phase, st_dev_phase))
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
                    if np.isinf(gain):
                        gain = 0
                    break
                else:
                    time.sleep(0.1)

            logger.debug("Freq : %s - Gain : %s - Phase : %s" % (f, gain, mean_phase))
            self.write_values_to_db(data={'Bode_Freq': [f], 'Bode_Gain': [gain], 'Bode_Phase': [mean_phase]})
        logger.debug("Bode end")
        self.write_variable_property(variable_name='Bode_run', property_name='BODE_5_LOOP', value=0,
                                     value_class='BOOLEAN')

    waveform = bool(self.read_variable_property(variable_name='Spectre_run', property_name='Spectre_9_Waveform'))
    if waveform:
        logger.debug("Waveform running...")

        self.inst_mdo.timeout = 10000
        self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                     timestamp=datetime.utcnow())

        vepp = min(max(self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_2_VEPP'), 0), 19)
        funcshape1 = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_3_FUNCTION_SHAPE')

        # Set the generator to freq f
        f = min(max(self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_1_F'), 1), 200000)
        mdo_horiz_scale = str(round(float(4.0 / (10.0 * float(f))), 6))

        self.inst_afg.write('*RST;OUTPut1:STATe ON;OUTP1:IMP MAX;SOUR1:AM:STAT OFF;SOUR1:FUNC:SHAP ' + funcshape1
                            + ';SOUR1:VOLT:LEV:IMM:AMPL ' + str(vepp) + 'Vpp')
        self.inst_afg.write('SOUR1:FREQ:FIX ' + str(f))
        self.inst_dmm.write('*RST;:FUNC "VOLTage:AC";:VOLTage:AC:RANGe:AUTO 1;:VOLTage:AC:RESolution MIN;:TRIG:DEL MIN')
        self.inst_mdo.write('*RST;:SEL:CH1 1;:HORIZONTAL:POSITION 0;:CH1:YUN "V";'
                            ':CH1:BANdwidth 10000000;:TRIG:A:TYP EDGE;'
                            ':TRIG:A:EDGE:COUPLING DC;:TRIG:A:EDGE:SOU CH1;:TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM')
        self.inst_mdo.write(':HORIZONTAL:SCALE ' + mdo_horiz_scale + ';:CH1:SCALE ' + str(1.2 * float(vepp) / (2 * 4)))
        self.inst_mdo.write(':SEL:CH2 1;:CH2:YUN "V";:CH2:BANdwidth 10000000;')

        # io config
        self.inst_mdo.write('header 0')
        self.inst_mdo.write('data:encdg SRIBINARY')
        self.inst_mdo.write('data:source CH1')  # channel
        self.inst_mdo.write('data:start 1')  # first sample
        record = int(self.inst_mdo.query('horizontal:recordlength?'))
        self.inst_mdo.write('data:stop {}'.format(record))  # last sample
        self.inst_mdo.write('wfmoutpre:byt_n 1')  # 1 byte per sample

        # acq config
        self.inst_mdo.write('acquire:state 0')  # stop
        self.inst_mdo.write('acquire:stopafter SEQUENCE')  # single
        self.inst_mdo.write('acquire:state 1')  # run

        # data query
        time.sleep(20 / f)
        self.inst_mdo.query_binary_values('curve?', datatype='b', container=np.array, delay=20/f)
        time.sleep(20 / f)
        bin_wave_ch1 = self.inst_mdo.query_binary_values('curve?', datatype='b', container=np.array, delay=20/f)

        # retrieve scaling factors
        tscale = float(self.inst_mdo.query('wfmoutpre:xincr?'))
        # tstart = float(self.inst_mdo.query('wfmoutpre:xzero?'))
        vscale_ch1 = float(self.inst_mdo.query('wfmoutpre:ymult?'))  # volts / level
        voff_ch1 = float(self.inst_mdo.query('wfmoutpre:yzero?'))  # reference voltage
        vpos_ch1 = float(self.inst_mdo.query('wfmoutpre:yoff?'))  # reference position (level)

        # create scaled vectors
        # horizontal (time)
        # total_time = tscale * record
        # tstop = tstart + total_time
        # scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
        # vertical (voltage)
        unscaled_wave_ch1 = np.array(bin_wave_ch1, dtype='double')  # data type conversion
        scaled_wave_ch1 = (unscaled_wave_ch1 - vpos_ch1) * vscale_ch1 + voff_ch1
        scaled_wave_ch1 = scaled_wave_ch1.tolist()

        # Read from the multimeter the RMS value of the output
        i = 0
        i_max = 3  # Try X time max to read 3  vseff
        vseff = 0
        while i < i_max:
            try:
                i += 1
                time.sleep(1)
                vseff = self.inst_dmm.query(':READ?')
                break
            except Exception as e:
                logger.error("Error reading multimeter : %s" % e)
        vsmax = float(vseff) * float(np.sqrt(2))
        mdo_ch2_scale = str(1.4 * float(vsmax) / 4.0)

        # Set the oscilloscope horizontal scale and vertical scale for the output
        self.inst_mdo.write(':CH2:SCALE ' + mdo_ch2_scale + ';:TRIG:A:LEV:CH2 0;')

        # io config
        self.inst_mdo.write('header 0')
        self.inst_mdo.write('data:encdg SRIBINARY')
        self.inst_mdo.write('data:source CH2')  # channel
        self.inst_mdo.write('data:start 1')  # first sample
        record = int(self.inst_mdo.query('horizontal:recordlength?'))
        self.inst_mdo.write('data:stop {}'.format(record))  # last sample
        self.inst_mdo.write('wfmoutpre:byt_n 1')  # 1 byte per sample

        # acq config
        self.inst_mdo.write('acquire:state 0')  # stop
        self.inst_mdo.write('acquire:stopafter SEQUENCE')  # single
        self.inst_mdo.write('acquire:state 1')  # run

        # data query
        time.sleep(20 / f)
        self.inst_mdo.query_binary_values('curve?', datatype='b', container=np.array, delay=20/f)
        time.sleep(20 / f)
        bin_wave_ch2 = self.inst_mdo.query_binary_values('curve?', datatype='b', container=np.array, delay=20/f)

        # retrieve scaling factors
        vscale_ch2 = float(self.inst_mdo.query('wfmoutpre:ymult?'))  # volts / level
        voff_ch2 = float(self.inst_mdo.query('wfmoutpre:yzero?'))  # reference voltage
        vpos_ch2 = float(self.inst_mdo.query('wfmoutpre:yoff?'))  # reference position (level)

        # create scaled vectors
        # vertical (voltage)
        unscaled_wave_ch2 = np.array(bin_wave_ch2, dtype='double')  # data type conversion
        scaled_wave_ch2 = (unscaled_wave_ch2 - vpos_ch2) * vscale_ch2 + voff_ch2
        scaled_wave_ch2 = scaled_wave_ch2.tolist()

        timevalues = list()
        time_now = time.time()
        scaled_wave_ch1_mini = list()
        scaled_wave_ch2_mini = list()
        save_duration = 1000  # in ms
        for i in range(0, save_duration):
            timevalues.append(time_now + 0.001 * i)
            scaled_wave_ch1_mini.append(scaled_wave_ch1[i*len(scaled_wave_ch1)/save_duration])
            scaled_wave_ch2_mini.append(scaled_wave_ch2[i*len(scaled_wave_ch2)/save_duration])

        # FFT CH1
        eta1 = scaled_wave_ch1
        nfft1 = len(eta1)
        hanning_1 = np.hanning(nfft1) * eta1
        spectrum_hanning_1 = abs(np.fft.fft(hanning_1))
        spectrum_hanning_1 = spectrum_hanning_1 * 2 * 2 / nfft1  # also correct for Hann filter
        frequencies1 = np.linspace(0, 1/tscale, nfft1, endpoint=False).tolist()

        logger.debug("tscale %s - f %s - Ech/s %s - Vepp %s" % (tscale, f, f/tscale, vepp))
        logger.debug("length eta1 %s - hanning %s - hanning_1 %s - spectrum_hanning_1 %s - frequencies1 %s"
                     % (nfft1, len(np.hanning(nfft1)), len(hanning_1), len(spectrum_hanning_1), len(frequencies1)))

        # FFT CH2
        eta2 = scaled_wave_ch2
        nfft2 = len(eta2)
        hanning_2 = np.hanning(nfft2) * eta2
        spectrum_hanning_2 = abs(np.fft.fft(hanning_2))
        spectrum_hanning_2 = spectrum_hanning_2 * 2 * 2 / nfft2  # also correct for Hann filter
        # frequencies2 = np.linspace(0, 1/tscale, nfft2, endpoint=False).tolist()

        self.write_values_to_db(data={'Wave_CH1': scaled_wave_ch1_mini, 'timevalues': timevalues})
        self.write_values_to_db(data={'Wave_CH2': scaled_wave_ch2_mini, 'timevalues': timevalues})
        self.write_values_to_db(data={'Wave_time': timevalues, 'timevalues': timevalues})
        self.write_values_to_db(data={'FFT_CH1': spectrum_hanning_1[:100], 'timevalues': timevalues})
        self.write_values_to_db(data={'FFT_CH2': spectrum_hanning_2[:100], 'timevalues': timevalues})
        self.write_values_to_db(data={'Bode_Freq': frequencies1[:100], 'timevalues': timevalues})
        self.write_variable_property(variable_name='Spectre_run', property_name='Spectre_9_Waveform', value=0,
                                     value_class='BOOLEAN')

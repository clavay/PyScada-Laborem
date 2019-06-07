#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyscada.models import Device, Variable, DeviceProtocol, Unit
from pyscada.laborem.models import LaboremRobotBase
import logging
import visa
import time
from django.utils.timezone import now
import numpy as np
from django.conf import settings
from struct import unpack

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
    # on tourne le bras pour deposer
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
        return ret
    else:
        ret = axe + '+' + str(int(rot_ascii)).zfill(3)
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

    r_alpha = (xp ** 2 + yp ** 2 - l_epaule ** 2 - l_coude ** 2) / (-2 * l_epaule * l_coude)
    alpha = np.arccos(r_alpha)
    theta_coude = -np.pi + alpha

    theta_5 = np.arctan2(yp, xp) + np.arcsin(l_coude * np.sin(alpha) / (xp ** 2 + yp ** 2) ** 0.5)
    theta_epaule = -np.pi / 4 + theta_5

    theta_poignet = -np.pi / 2 - np.pi / 4 - theta_epaule - theta_coude

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
    theta_base = theta * np.pi / 180
    robot.write(format_ascii(deg_to_ascii(theta_base * 180 / np.pi, angle_max_base), 'B'))
    try:
        old_theta = 0.0 - self.read_variable_property(variable_name='LABOREM', property_name='OLD_THETA')
        tempo = abs(sum([deg_to_ascii(theta_base * 180 / np.pi, angle_max_base), old_theta])) * 5000 / 1024
        time.sleep(tempo / 1000)
        self.write_variable_property(variable_name='LABOREM', property_name='OLD_THETA',
                                     value=deg_to_ascii(theta_base * 180 / np.pi, angle_max_base),
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
    if not Device.objects.filter(short_name="generic_device"):
        Device.objects.create(short_name="generic_device", protocol=DeviceProtocol.objects.get(protocol="generic"),
                              description="Laborem generic device to store generic variables")
    if not Variable.objects.filter(name="LABOREM"):
        Variable.objects.create(name="LABOREM", description="Var to store Varaible Properties used by Laborem",
                                device=Device.objects.get(short_name="generic_device"), unit=Unit.objects.get(unit=""))
    # User stop button
    self.write_variable_property("LABOREM", "USER_STOP", 0, value_class='BOOLEAN')

    # Progress bar
    self.write_variable_property("LABOREM", "progress_bar_now", 0, value_class='int16')
    self.write_variable_property("LABOREM", "progress_bar_min", 0, value_class='int16')
    self.write_variable_property("LABOREM", "progress_bar_max", 0, value_class='int16')

    # Timeline
    self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                 timestamp=now())
    self.write_variable_property("LABOREM", "viewer_stop_timeline", 1, value_class="BOOLEAN",
                                 timestamp=now())

    # Worker experience
    self.write_variable_property("LABOREM", "EXPERIENCE", '', value_class='string')

    self.write_variable_property("LABOREM", "message_laborem", "Laborem is starting. Please Wait...",
                                 value_class='string')
    time.sleep(10)
    self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')

    visa_backend = '@py'  # use PyVISA-py as backend
    if hasattr(settings, 'VISA_BACKEND'):
        visa_backend = settings.VISA_BACKEND
    try:
        device_mdo = Device.objects.get(pk=6)
        device_afg = Device.objects.get(pk=5)
        device_robot = Device.objects.get(pk=1)
    except Device.DoesNotExist:
        logger.error("Script Laborem - Device(s) does not exist, please create all the devices first.")
        return False

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
    self.write_variable_property("LABOREM", "message_laborem", "Laborem is down.", value_class='string')
    self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                 timestamp=now())
    self.write_variable_property("LABOREM", "viewer_stop_timeline", 1, value_class="BOOLEAN",
                                 timestamp=now())
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
    put_on_robot = bool(self.read_variable_property(variable_name='LABOREM', property_name='ROBOT_PUT_ON'))
    if put_on_robot:
        logger.debug("Putting on Elements...")
        # Move the robot
        for base in LaboremRobotBase.objects.all():
            if base.element is not None and str(base.element.active) == '0':
                self.write_variable_property("LABOREM", "message_laborem", "Le robot place les éléments...",
                                             value_class='string')
                r_element = base.element.R
                theta_element = base.element.theta
                z_element = base.element.z
                r_base = base.R
                theta_base = base.theta
                z_base = base.z
                take_and_drop(self, self.inst_robot, r_element, theta_element, z_element, r_base, theta_base, z_base)
                base.element.change_active_to_base_id(base.pk)
            else:
                if base.element is None:
                    logger.debug("Base : %s  - Element : %s" % (base, base.element))
                else:
                    logger.debug("Base : %s  - Element : %s - base.element.active : %s " %
                                 (base, base.element, base.element.active))
        self.write_variable_property(variable_name='LABOREM', property_name='ROBOT_PUT_ON', value=0,
                                     value_class='BOOLEAN')
        self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')

    take_off_robot = bool(self.read_variable_property(variable_name='LABOREM', property_name='ROBOT_TAKE_OFF'))
    if take_off_robot:
        logger.debug("Taking off Elements...")
        for base in LaboremRobotBase.objects.all():
            if base.element is not None and str(base.element.active) != '0':
                self.write_variable_property("LABOREM", "message_laborem", "Le robot retire les éléments...",
                                             value_class='string')
                r_element = base.element.R
                theta_element = base.element.theta
                z_element = base.element.z
                r_base = base.R
                theta_base = base.theta
                z_base = base.z
                take_and_drop(self, self.inst_robot, r_base, theta_base, z_base, r_element, theta_element, z_element)
                base.element.change_active_to_base_id('0')
            else:
                if base.element is None:
                    logger.debug("Base : %s  - Element : %s" % (base, base.element))
                else:
                    logger.debug("Base : %s  - Element : %s - base.element.active : %s " %
                                 (base, base.element, base.element.active))
            base.change_selected_element(None)
        self.write_variable_property(variable_name='LABOREM', property_name='ROBOT_TAKE_OFF', value=0,
                                     value_class='BOOLEAN')
        self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')

    bode = bool(self.read_variable_property(variable_name='Bode_run', property_name='BODE_5_LOOP'))
    if bode:
        logger.debug("Bode running...")
        logger.debug("MDO timeout : %d" % self.inst_mdo.timeout)
        self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                     timestamp=now())
        self.write_variable_property("LABOREM", "message_laborem", "Diagrammes de Bode en cours d'acquisition...",
                                     value_class='string')

        # Send *RST to all instruments
        reset_instrument(self.inst_afg)
        reset_instrument(self.inst_mdo)
        time.sleep(2)

        # Prepare AFG for Bode : output1 on, output imp max
        afg_prepare_for_bode(self, ch=1)

        # Set generator Vpp
        vepp = self.read_variable_property(variable_name='Bode_run', property_name='BODE_1_VEPP')
        afg_set_vpp(self, ch=1, vpp=vepp)

        # Prepare MDO trigger, channel 1 vertical scale, bandwidth
        mdo_prepare_for_bode(self, vpp=vepp)

        fmin = self.read_variable_property(variable_name='Bode_run', property_name='BODE_2_FMIN')
        fmax = self.read_variable_property(variable_name='Bode_run', property_name='BODE_3_FMAX')
        nb_points = self.read_variable_property(variable_name='Bode_run', property_name='BODE_4_NB_POINTS')

        # Progress bar
        n = 0
        self.write_variable_property("LABOREM", "progress_bar_now", n, value_class='int16')
        self.write_variable_property("LABOREM", "progress_bar_min", 0, value_class='int16')
        self.write_variable_property("LABOREM", "progress_bar_max", nb_points, value_class='int16')

        range_i = None
        for f in np.geomspace(fmin, fmax, nb_points):
            if self.read_variable_property(variable_name='LABOREM', property_name='USER_STOP'):
                self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                             timestamp=now())
                self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')
                self.write_variable_property(variable_name='Bode_run', property_name='BODE_5_LOOP', value=0,
                                             value_class='BOOLEAN')
                self.write_variable_property("LABOREM", "progress_bar_max", 0, value_class='int16')
                self.write_variable_property("LABOREM", "USER_STOP", 0, value_class='BOOLEAN')
                return
            # Progress bar
            n += 1
            self.write_variable_property("LABOREM", "progress_bar_now", n, value_class='int16')

            # Set the generator frequency to f
            afg_set_frequency(self, ch=1, frequency=f)

            # Set the oscilloscope horizontal scale and find the vertical scale for channel 2
            range_i = mdo_find_vertical_scale(self, ch=2, frequency=f, range_i=range_i)

            # Start reading the phase
            phase, phase2 = mdo_get_phase(self, source1=1, source2=2, frequency=f)

            # Start reading the gain
            gain = mdo_gain(self, source1=1, source2=2)

            logger.debug("Freq : %s - Gain : %s - Phase : %s" % (f, gain, phase))
            # self.write_values_to_db(data={'Bode_Freq': [f], 'Bode_Gain': [gain], 'Bode_Phase': [phase]})
            timevalues = time.time()
            self.write_values_to_db(data={'Bode_Freq': [f], 'timevalues': [timevalues]})
            self.write_values_to_db(data={'Bode_Gain': [gain], 'timevalues': [timevalues]})
            self.write_values_to_db(data={'Bode_Phase': [phase], 'timevalues': [timevalues]})
            self.write_values_to_db(data={'Bode_Phase_numpy': [phase2], 'timevalues': [timevalues]})

        logger.debug("Bode end")
        self.write_variable_property("LABOREM", "viewer_stop_timeline", 1, value_class="BOOLEAN",
                                     timestamp=now())
        time.sleep(2)
        self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')
        self.write_variable_property(variable_name='Bode_run', property_name='BODE_5_LOOP', value=0,
                                     value_class='BOOLEAN')
        self.write_variable_property("LABOREM", "progress_bar_max", 0, value_class='int16')

    waveform = bool(self.read_variable_property(variable_name='Spectre_run', property_name='Spectre_9_Waveform'))
    if waveform:
        logger.debug("Waveform running...")
        self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                     timestamp=now())
        self.write_variable_property("LABOREM", "message_laborem", "Analyse spectrale en cours d'acquisition...",
                                     value_class='string')

        # Send *RST to all instruments
        reset_instrument(self.inst_afg)
        reset_instrument(self.inst_mdo)
        time.sleep(2)

        # Prepare AFG for Bode : output1 on, output imp max
        afg_prepare_for_bode(self, ch=1)

        # Set generator Vpp
        vepp = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_2_VEPP')
        afg_set_vpp(self, ch=1, vpp=vepp)

        # Prepare MDO trigger, channel 1 vertical scale, bandwidth
        mdo_prepare_for_bode(self, vpp=vepp)

        # Set generator function shape
        func_shape = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_3_FUNCTION_SHAPE')
        afg_set_function_shape(self, ch=1, function_shape=func_shape)

        # Set the generator frequency to f
        f = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_1_F')
        afg_set_frequency(self, ch=1, frequency=f)

        # Set the oscilloscope horizontal scale and vertical scale for the output
        range_i = None
        mdo_find_vertical_scale(self, ch=2, frequency=f, range_i=range_i)

        mdo_horizontal_scale_in_period(self, period=4.0, frequency=f)

        resolution = 10000
        scaled_wave_ch1 = mdo_query_waveform(self, ch=1, points_resolution=resolution, frequency=f, refresh=True)
        scaled_wave_ch2 = mdo_query_waveform(self, ch=2, points_resolution=resolution, frequency=f, refresh=False)

        scaled_wave_ch1_mini = list()
        scaled_wave_ch2_mini = list()
        time_values = list()
        time_values_to_show = list()
        time_now = time.time()

        # Prepare the lists to save
        save_resolution = 100
        for i in range(0, save_resolution):
            time_values.append(time_now + 0.001 * i)  # store one value each ms
            time_values_to_show.append(0.001 * i * mdo_horizontal_time(self) * 1000 * 10)  # store time in ms
            scaled_wave_ch1_mini.append(scaled_wave_ch1[i * int(len(scaled_wave_ch1) / save_resolution)])
            scaled_wave_ch2_mini.append(scaled_wave_ch2[i * int(len(scaled_wave_ch2) / save_resolution)])

        # FFT CH1
        spectrum_hanning_1 = fft(scaled_wave_ch1)
        tscale = float(self.inst_mdo.query('wfmoutpre:xincr?'))
        frequencies = np.linspace(0, 1 / tscale, len(scaled_wave_ch1), endpoint=False).tolist()
        # FFT CH2
        spectrum_hanning_2 = fft(scaled_wave_ch2)

        logger.debug("tscale %s - f %s - Ech/s %s - Vepp %s" % (tscale, f, f / tscale, vepp))
        logger.debug("spectrum_hanning_1 %s - frequencies %s" % (len(spectrum_hanning_1), len(frequencies)))

        if self.read_variable_property(variable_name='LABOREM', property_name='USER_STOP'):
            self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                         timestamp=now())
            self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')
            self.write_variable_property(variable_name='Spectre_run', property_name='Spectre_9_Waveform', value=0,
                                         value_class='BOOLEAN')
            self.write_variable_property("LABOREM", "USER_STOP", 0, value_class='BOOLEAN')
            return

        self.write_values_to_db(data={'Wave_CH1': scaled_wave_ch1_mini, 'timevalues': time_values})
        self.write_values_to_db(data={'Wave_CH2': scaled_wave_ch2_mini, 'timevalues': time_values})
        self.write_values_to_db(data={'Wave_time': time_values_to_show, 'timevalues': time_values})
        self.write_values_to_db(data={'FFT_CH1': spectrum_hanning_1[:100], 'timevalues': time_values})
        self.write_values_to_db(data={'FFT_CH2': spectrum_hanning_2[:100], 'timevalues': time_values})
        self.write_values_to_db(data={'Bode_Freq': frequencies[:100], 'timevalues': time_values})
        self.write_variable_property("LABOREM", "viewer_stop_timeline", 1, value_class="BOOLEAN",
                                     timestamp=now())
        time.sleep(4)
        self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')
        self.write_variable_property(variable_name='Spectre_run', property_name='Spectre_9_Waveform', value=0,
                                     value_class='BOOLEAN')

    self.write_variable_property("LABOREM", "USER_STOP", 0, value_class='BOOLEAN')


# AFG functions
def afg_prepare_for_bode(self, ch=1):
    self.inst_afg.query('OUTP%d:STATe ON;OUTP%d:IMP MAX;SOUR%d:AM:STAT OFF;*OPC?;' % (ch, ch, ch))


def afg_set_vpp(self, ch=1, vpp=1):
    self.inst_afg.query('SOUR%d:VOLT:LEV:IMM:AMPL %sVpp;*OPC?;' % (ch, str(vpp)))


def afg_set_function_shape(self, ch=1, function_shape='SIN'):
    self.inst_afg.query('SOUR%d:FUNC:SHAP %s;*OPC?;' % (ch, function_shape))


def afg_set_frequency(self, ch=1, frequency=1000):
    self.inst_afg.query('SOUR%d:FREQ:FIX %s;*OPC?;' % (ch, str(frequency)))


# MDO functions
def mdo_query_waveform(self, ch=1, points_resolution=100, frequency=1000, refresh=False):
    self.inst_mdo.query(':SEL:CH%d 1;:HORIZONTAL:POSITION 0;:CH%d:YUN "V";' 
                        ':CH%d:BANdwidth 10000000;:TRIG:A:TYP EDGE;:TRIG:A:EDGE:COUPLING AC;:TRIG:A:EDGE:SOU CH%d;'
                        ':TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM;*OPC?' % (ch, ch, ch, ch))

    # io config
    self.inst_mdo.write('header 0')
    self.inst_mdo.write('data:encdg SRIBINARY')
    self.inst_mdo.write('data:source CH%d' % ch)  # channel
    self.inst_mdo.write('data:snap')  # last sample
    self.inst_mdo.write('wfmoutpre:byt_n 1')  # 1 byte per sample

    if refresh:
        # acq config
        self.inst_mdo.write('acquire:state 0')  # stop
        self.inst_mdo.write('acquire:stopafter SEQUENCE')  # single
        self.inst_mdo.write('acquire:state 1')  # run

    # data query
    self.inst_mdo.query('*OPC?')
    bin_wave = self.inst_mdo.query_binary_values('curve?', datatype='b', container=np.array, delay=2 * 10 / frequency)

    # retrieve scaling factors
    # tscale = float(self.inst_mdo.query('wfmoutpre:xincr?'))
    vscale = float(self.inst_mdo.query('wfmoutpre:ymult?'))  # volts / level
    voff = float(self.inst_mdo.query('wfmoutpre:yzero?'))  # reference voltage
    vpos = float(self.inst_mdo.query('wfmoutpre:yoff?'))  # reference position (level)

    # create scaled vectors
    # horizontal (time)
    # total_time = tscale * record
    # tstop = tstart + total_time
    # scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
    # vertical (voltage)
    unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion
    scaled_wave = (unscaled_wave - vpos) * vscale + voff
    scaled_wave = scaled_wave.tolist()

    scaled_wave_mini = list()
    for i in range(0, points_resolution):
        scaled_wave_mini.append(scaled_wave[i * int(len(scaled_wave) / points_resolution)])

    return np.asarray(scaled_wave_mini)


def mdo_get_phase(self, source1=1, source2=2, frequency=1000):
    mdo_horizontal_scale_in_period(self, period=4.0, frequency=frequency)
    self.inst_mdo.write(':MEASUrement:IMMed:SOUrce1 CH%d;:MEASUrement:IMMed:SOUrce2 CH%d;'
                        ':MEASUREMENT:IMMed:TYPE PHASE' % (source1, source2))

    # Start reading the phase
    retries = 0
    while retries < 3:
        self.inst_mdo.write('acquire:state 0')  # stop
        self.inst_mdo.write('acquire:stopafter SEQUENCE')  # single
        self.inst_mdo.write('acquire:state 1')  # run
        self.inst_mdo.query('*OPC?')
        phase = float(self.inst_mdo.query(':MEASUREMENT:IMMED:VALUE?;'))
        retries += 1
        if -360 < phase < 360:
            break
        if retries >= 3:
            phase = None
            break
        logger.debug('Wrong phase = %s' % phase)
        time.sleep(1)
    if phase < -180 and phase is not None:
        phase += 360
    mdo_horizontal_scale_in_period(self, period=4.0, frequency=frequency)

    a = mdo_query_waveform(self, ch=1, frequency=frequency, refresh=True, points_resolution=10000)
    b = mdo_query_waveform(self, ch=2, frequency=frequency, refresh=False, points_resolution=10000)
    phase2 = find_phase_2_signals(a, b, frequency, mdo_horizontal_time(self))
    logger.debug('phase oscillo = %s - phase scipy = %s' % (phase, phase2))
    return phase, phase2


def mdo_horizontal_time(self):
    record = int(self.inst_mdo.query('horizontal:recordlength?'))
    tscale = float(self.inst_mdo.query('wfmoutpre:xincr?'))
    return tscale * record


def fft(eta):
    nfft = len(eta)
    hanning = np.hanning(nfft) * eta
    spectrum_hanning = abs(np.fft.fft(hanning))
    spectrum_hanning = spectrum_hanning * 2 * 2 / nfft  # also correct for Hann filter
    return spectrum_hanning


def mdo_horizontal_scale_in_period(self, period=1.0, frequency=1000):
    mdo_horiz_scale = str(round(float(period / (10.0 * float(frequency))), 6))
    self.inst_mdo.query(':HORIZONTAL:SCALE %s;*OPC?' % mdo_horiz_scale)


def mdo_find_vertical_scale(self, ch=1, frequency=1000, range_i=None):
    vranges = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
    if range_i is None:
        range_i = int(np.ceil(len(vranges) / 2.0))
    mdo_horizontal_scale_in_period(self, period=1.0, frequency=frequency)

    failed = 0
    mdo_div_quantity = 8.0
    range_i_min = 0
    while range_i < len(vranges):
        logger.debug(range_i)
        self.inst_mdo.query(':CH%d:SCALE %s;*OPC?' % (ch, str(vranges[range_i])))
        data = mdo_query_waveform(self, ch=ch, frequency=frequency, refresh=True)
        if data is None:
            failed += 1
            if failed > 3:
                logger.debug('data is None more than 3 times')
                break
            continue
        failed = 0
        if np.max(abs(data)) > (mdo_div_quantity * 0.9 * vranges[range_i] / 2.0):
            range_i_min = range_i + 1
            range_i += 3
            range_i = min(len(vranges) - 1, range_i)
        if range_i == 0:
            if np.max(abs(data)) < (mdo_div_quantity * 0.9 * vranges[range_i] / 2.0):
                break
            range_i = 1
            continue
        if (mdo_div_quantity * 0.9 * vranges[range_i - 1] / 2.0) <= np.max(abs(data)) \
                < (mdo_div_quantity * 0.9 * vranges[range_i] / 2.0):
            break
        range_i_old = range_i
        range_i = max(range_i_min, np.where(vranges > 2.0 * np.max(abs(data)) / mdo_div_quantity * 0.9)[0][0])
        if range_i == range_i_old:
            break

    logger.debug(range_i)
    mdo_ch2_scale = str(vranges[range_i])
    logger.debug("Freq = %s - horiz scale = %s - ch2 scale = %s"
                 % (int(frequency), str(round(float(1.0 / (10.0 * float(frequency))), 6)), mdo_ch2_scale))
    return range_i


def mdo_query_peak_to_peak(self, ch=1):
    return float(self.inst_mdo.query((':MEASUrement:IMMed:SOUrce1 CH%d;:MEASUREMENT:IMMED:TYPE PK2PK;'
                                      ':MEASUREMENT:IMMED:VALUE?' % ch)))


def mdo_gain(self, source1=1, source2=2):
    return 20 * np.log10(mdo_query_peak_to_peak(self, ch=source2) / mdo_query_peak_to_peak(self, ch=source1))


def mdo_prepare_for_bode(self, vpp):
    self.inst_mdo.query(':SEL:CH1 1;:SEL:CH2 1;:HORIZONTAL:POSITION 0;:CH1:YUN "V";:CH1:SCALE %s;:CH2:YUN "V";'
                        ':CH2:BANdwidth 10000000;:CH1:BANdwidth 10000000;:TRIG:A:TYP EDGE;:TRIG:A:EDGE:COUPLING AC;'
                        ':TRIG:A:EDGE:SOU CH1;:TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM;:CH1:COUP AC;:CH2:COUP AC;'
                        ':TRIG:A:LEV:CH1 0;*OPC?;' % str(1.2 * float(vpp) / (2 * 4)))


def reset_instrument(inst):
    inst.query('*RST;*OPC?')


def find_phase_2_signals(a, b, frequency, tmax):
    period = 1 / frequency                            # period of oscillations (seconds)
    tmax = float(tmax)
    nsamples = int(a.size)
    logger.debug('tmax = %s - nsamples = %s' % (tmax, nsamples))                  # length of time series (seconds)

    # construct time array
    t = np.linspace(0.0, tmax, nsamples, endpoint=False)

    # calculate cross correlation of the two signals
    xcorr = np.correlate(a, b, "full")

    # The peak of the cross-correlation gives the shift between the two signals
    # The xcorr array goes from -nsamples to nsamples
    dt = np.linspace(-t[-1], t[-1], 2*nsamples-1)
    recovered_time_shift = dt[np.argmax(xcorr)]

    # force the phase shift to be in [-pi:pi]
    recovered_phase_shift = -1 * 2 * np.pi * (((0.5 + recovered_time_shift / period) % 1.0) - 0.5)
    recovered_phase_shift_before = -1 * 2 * np.pi * (((0.5 + dt[np.argmax(xcorr) - 1] / period) % 1.0) - 0.5)
    recovered_phase_shift_after = -1 * 2 * np.pi * (((0.5 + dt[np.argmax(xcorr) + 1] / period) % 1.0) - 0.5)
    logger.debug('phase - 1 = %s - phase = %s - phase + 1 = %s' %
                 (recovered_phase_shift_before*180/np.pi, recovered_phase_shift*180/np.pi,
                  recovered_phase_shift_after*180/np.pi))

    return recovered_phase_shift*180/np.pi

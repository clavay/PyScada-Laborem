#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyscada.models import Device, Variable, DeviceProtocol, Unit
from pyscada.laborem.models import LaboremRobotBase, LaboremMotherboardDevice
import logging
import visa
import time
from django.utils.timezone import now
import numpy as np

logger = logging.getLogger(__name__)


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

    try:
        device_laborem = LaboremMotherboardDevice.objects.first()
        for d in Device.objects.all():
            if d == device_laborem.MotherboardIOConfig.mdo1:
                self.inst_mdo = d.visadevice.instrument.get_handler_instance()
            if d == device_laborem.MotherboardIOConfig.afg1:
                self.inst_afg = d.visadevice.instrument.get_handler_instance()
    except Device.DoesNotExist:
        logger.error("Script Laborem - Device(s) does not exist, please create all the devices first.")
        return False
    except AttributeError:
        logger.error("Script Laborem - The motherboard does not have the good IO configuration for this script.")
        return False

    try:
        for d in Device.objects.all():
            if d == device_laborem.laboremmotherboard_device.MotherboardIOConfig.mdo1:
                self.inst_robot = d.get_handler_instance()
    except Device.DoesNotExist:
        self.inst_robot = None
        logger.debug("Script Laborem - Robot does not exist.")

    if self.inst_robot is not None:
        self.inst_robot.init()

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
            self.inst_mdo.inst.close()
            self.inst_mdo.inst = None
    except AttributeError:
        pass
    try:
        if self.inst_afg is not None:
            self.inst_afg.inst.close()
            self.inst_afg.inst = None
    except AttributeError:
        pass
    try:
        if self.inst_robot is not None:
            self.inst_robot.init()
            self.inst_robot.inst.close()
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
        if self.inst_robot is None:
            self.write_variable_property("LABOREM", "message_laborem", "Pas de robot configuré.", value_class='string')
            time.sleep(5)
        else:
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
                    self.inst_robot.take_and_drop(r_element, theta_element, z_element, r_base, theta_base, z_base)
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
        if self.inst_robot is None:
            self.write_variable_property("LABOREM", "message_laborem", "Pas de robot configuré.", value_class='string')
            time.sleep(5)
        else:
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
                    self.inst_robot.take_and_drop(r_base, theta_base, z_base, r_element, theta_element, z_element)
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
        logger.debug("MDO timeout : %d" % self.inst_mdo.inst.timeout)
        self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                     timestamp=now())
        self.write_variable_property("LABOREM", "message_laborem", "Diagrammes de Bode en cours d'acquisition...",
                                     value_class='string')

        # Send *RST to all instruments
        self.inst_afg.reset_instrument()
        self.inst_mdo.reset_instrument()
        time.sleep(2)

        # Prepare AFG for Bode : output1 on, output imp max
        self.inst_afg.afg_prepare_for_bode(ch=1)

        # Set generator Vpp
        vepp = self.read_variable_property(variable_name='Bode_run', property_name='BODE_1_VEPP')
        self.inst_afg.afg_set_vpp(ch=1, vpp=vepp)

        # Prepare MDO trigger, channel 1 vertical scale, bandwidth
        self.inst_mdo.mdo_prepare_for_bode(vpp=vepp)

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
            self.inst_afg.afg_set_frequency(ch=1, frequency=f)

            # Set the oscilloscope horizontal scale and find the vertical scale for channel 2
            range_i = self.inst_mdo.mdo_find_vertical_scale(ch=2, frequency=f, range_i=range_i)

            # Start reading the phase
            phase, phase2 = self.inst_mdo.mdo_get_phase(source1=1, source2=2, frequency=f)

            # Start reading the gain
            gain = self.inst_mdo.mdo_gain(source1=1, source2=2)

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
        self.inst_afg.reset_instrument()
        self.inst_mdo.reset_instrument()
        time.sleep(2)

        # Prepare AFG for Bode : output1 on, output imp max
        self.inst_afg.afg_prepare_for_bode(ch=1)

        # Set generator Vpp
        vepp = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_2_VEPP')
        self.inst_afg.afg_set_vpp(ch=1, vpp=vepp)

        # Prepare MDO trigger, channel 1 vertical scale, bandwidth
        self.inst_mdo.mdo_prepare_for_bode(vpp=vepp)

        # Set generator function shape
        func_shape = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_3_FUNCTION_SHAPE')
        self.inst_afg.afg_set_function_shape(ch=1, function_shape=func_shape)

        # Set the generator frequency to f
        f = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_1_F')
        self.inst_afg.afg_set_frequency(ch=1, frequency=f)

        # Set the oscilloscope horizontal scale and vertical scale for the output
        range_i = None
        self.inst_mdo.mdo_find_vertical_scale(ch=2, frequency=f, range_i=range_i)

        self.inst_mdo.mdo_horizontal_scale_in_period(period=4.0, frequency=f)

        resolution = 10000
        scaled_wave_ch1 = self.inst_mdo.mdo_query_waveform(ch=1, points_resolution=resolution, frequency=f,
                                                           refresh=True)
        scaled_wave_ch2 = self.inst_mdo.mdo_query_waveform(ch=2, points_resolution=resolution, frequency=f,
                                                           refresh=False)

        scaled_wave_ch1_mini = list()
        scaled_wave_ch2_mini = list()
        time_values = list()
        time_values_to_show = list()
        time_now = time.time()

        # Prepare the lists to save
        save_resolution = 100
        for i in range(0, save_resolution):
            time_values.append(time_now + 0.001 * i)  # store one value each ms
            time_values_to_show.append(0.001 * i * self.inst_mdo.mdo_horizontal_time() * 1000 * 10)  # store time in ms
            scaled_wave_ch1_mini.append(scaled_wave_ch1[i * int(len(scaled_wave_ch1) / save_resolution)])
            scaled_wave_ch2_mini.append(scaled_wave_ch2[i * int(len(scaled_wave_ch2) / save_resolution)])

        # FFT CH1
        spectrum_hanning_1 = self.inst_mdo.fft(scaled_wave_ch1)
        tscale = self.inst_mdo.mdo_xincr()
        frequencies = np.linspace(0, 1 / tscale, len(scaled_wave_ch1), endpoint=False).tolist()
        # FFT CH2
        spectrum_hanning_2 = self.inst_mdo.fft(scaled_wave_ch2)

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

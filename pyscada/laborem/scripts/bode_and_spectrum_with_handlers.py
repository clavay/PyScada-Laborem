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

    try:
        io_conf = LaboremMotherboardDevice.objects.first().MotherboardIOConfig
    except AttributeError:
        logger.error("Script Laborem - The motherboard does not have the good IO configuration for this script.")
        return False

    self.instruments = lambda: None
    self.instruments.inst_mdo = connect_check_visa(io_conf.mdo1)
    self.instruments.inst_afg = connect_check_visa(io_conf.afg1)
    self.instruments.inst_robot = connect_check_visa(io_conf.robot1, False)
    self.instruments.inst_mdo2 = connect_check_visa(io_conf.mdo2)

    self.instruments.inst_robot.init() if self.instruments.inst_robot is not None else True

    self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')

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
        self.instruments.inst_mdo.inst.close()
        self.instruments.inst_afg.inst.close()
        self.instruments.inst_robot.inst.close()
        self.instruments.inst_mdo2.inst.close()
    except visa.VisaIOError as e:
        logger.error(e)

    return True


def script(self):
    """
    write your code loop code here, don't change the name of this function

    :return:
    """
    if self.instruments.inst_afg.inst is not None and self.instruments.inst_mdo.inst is not None:
        # and self.instruments.inst_robot.inst is not None:
        put_on_robot = bool(self.read_variable_property(variable_name='LABOREM', property_name='ROBOT_PUT_ON'))
        if put_on_robot:
            if self.instruments.inst_robot is None:
                self.write_variable_property("LABOREM", "message_laborem", "Pas de robot configuré.",
                                             value_class='string')
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
                        self.instruments.inst_robot.take_and_drop(
                            r_element, theta_element, z_element, r_base, theta_base, z_base)
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
            if self.instruments.inst_robot is None:
                # self.write_variable_property("LABOREM", "message_laborem", "Pas de robot configuré.",
                #                             value_class='string')
                # time.sleep(5)
                pass
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
                        self.instruments.inst_robot.take_and_drop(
                            r_base, theta_base, z_base, r_element, theta_element, z_element)
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
        if bode and self.instruments.inst_mdo is not None and self.instruments.inst_afg is not None:
            logger.debug("Bode running...")
            logger.debug("MDO timeout : %d" % self.instruments.inst_mdo.inst.timeout)
            self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                         timestamp=now())
            self.write_variable_property("LABOREM", "message_laborem", "Diagrammes de Bode en cours d'acquisition...",
                                         value_class='string')

            # Send *RST to all instruments
            self.instruments.inst_afg.reset_instrument()
            self.instruments.inst_mdo.reset_instrument()
            time.sleep(2)

            # Prepare AFG for Bode : output1 on, output imp max
            self.instruments.inst_afg.afg_prepare_for_bode(ch=1)

            # Set generator Vpp
            vepp = self.read_variable_property(variable_name='Bode_run', property_name='BODE_1_VEPP')
            self.instruments.inst_afg.afg_set_vpp(ch=1, vpp=vepp)

            # Prepare MDO trigger, channel 1 vertical scale, bandwidth
            self.instruments.inst_mdo.mdo_prepare_for_bode(vpp=vepp)

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
                self.instruments.inst_afg.afg_set_frequency(ch=1, frequency=f)

                period = 4.0

                # Set the oscilloscope horizontal scale and find the vertical scale for channel 2
                range_i = self.instruments.inst_mdo.mdo_find_vertical_scale(
                    ch=2, frequency=f, range_i=range_i, period=period)

                # Start reading the phase
                phase_osc, phase_np = self.instruments.inst_mdo.mdo_get_phase(
                    source1=1, source2=2, frequency=f, period=period)

                # Start reading the gain
                period = 2.0
                self.instruments.inst_mdo.mdo_horizontal_scale_in_period(period=period, frequency=f)
                gain = self.instruments.inst_mdo.mdo_gain(source1=1, source2=2, frequency=f, period=period)

                logger.debug("Freq : %s - Gain : %s - Phase Osc : %s - Phase Np : %s" % (f, gain, phase_osc, phase_np))

                timevalues = time.time()
                self.write_values_to_db(data={'Bode_Freq': [f], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Gain': [gain], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Phase': [phase_osc], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Phase_numpy': [phase_np], 'timevalues': [timevalues]})

            logger.debug("Bode end")
            self.write_variable_property("LABOREM", "viewer_stop_timeline", 1, value_class="BOOLEAN",
                                         timestamp=now())
            time.sleep(2)
            self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')
            self.write_variable_property(variable_name='Bode_run', property_name='BODE_5_LOOP', value=0,
                                         value_class='BOOLEAN')
            self.write_variable_property("LABOREM", "progress_bar_max", 0, value_class='int16')

        bode_compare_instruments = bool(self.read_variable_property(variable_name='Bode_run',
                                                                    property_name='BODE_5_LOOP_COMPARE'))
        if bode_compare_instruments and self.instruments.inst_mdo is not None \
                and self.instruments.inst_afg is not None and self.instruments.inst_mdo2 is not None:
            logger.debug("Bode running...")
            logger.debug("MDO1 timeout : %d" % self.instruments.inst_mdo.inst.timeout)
            logger.debug("MDO2 timeout : %d" % self.instruments.inst_mdo2.inst.timeout)
            self.write_variable_property("LABOREM", "viewer_start_timeline", 1, value_class="BOOLEAN",
                                         timestamp=now())
            self.write_variable_property("LABOREM", "message_laborem", "Diagrammes de Bode en cours d'acquisition...",
                                         value_class='string')

            # Send *RST to all instruments
            self.instruments.inst_afg.reset_instrument()
            self.instruments.inst_mdo.reset_instrument()
            self.instruments.inst_mdo2.reset_instrument()
            time.sleep(2)

            # Prepare AFG for Bode : output1 on, output imp max
            self.instruments.inst_afg.afg_prepare_for_bode(ch=1)

            # Set generator Vpp
            vepp = self.read_variable_property(variable_name='Bode_run', property_name='BODE_1_VEPP')
            self.instruments.inst_afg.afg_set_vpp(ch=1, vpp=vepp)

            # Prepare MDO trigger, channel 1 vertical scale, bandwidth
            self.instruments.inst_mdo.mdo_prepare_for_bode(vpp=vepp)
            self.instruments.inst_mdo2.mdo_prepare_for_bode(vpp=vepp)

            fmin = self.read_variable_property(variable_name='Bode_run', property_name='BODE_2_FMIN')
            fmax = self.read_variable_property(variable_name='Bode_run', property_name='BODE_3_FMAX')
            nb_points = self.read_variable_property(variable_name='Bode_run', property_name='BODE_4_NB_POINTS')

            # Progress bar
            n = 0
            self.write_variable_property("LABOREM", "progress_bar_now", n, value_class='int16')
            self.write_variable_property("LABOREM", "progress_bar_min", 0, value_class='int16')
            self.write_variable_property("LABOREM", "progress_bar_max", nb_points, value_class='int16')

            range_i = None
            range_i_2 = None
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
                self.instruments.inst_afg.afg_set_frequency(ch=1, frequency=f)

                period = 4.0

                # Set the oscilloscope horizontal scale and find the vertical scale for channel 2
                range_i = self.instruments.inst_mdo.mdo_find_vertical_scale(
                    ch=2, frequency=f, range_i=range_i, period=period)
                range_i_2 = self.instruments.inst_mdo2.mdo_find_vertical_scale(
                    ch=2, frequency=f, range_i=range_i_2, period=period)

                # Start reading the phase
                phase_osc, phase_np = self.instruments.inst_mdo.mdo_get_phase(
                    source1=1, source2=2, frequency=f, period=period)
                phase_osc2, phase_np2 = self.instruments.inst_mdo2.mdo_get_phase(
                    source1=1, source2=2, frequency=f, period=period)

                # Start reading the gain
                period = 2.0
                self.instruments.inst_mdo.mdo_horizontal_scale_in_period(period=period, frequency=f)
                gain = self.instruments.inst_mdo.mdo_gain(source1=1, source2=2, frequency=f, period=period)
                self.instruments.inst_mdo2.mdo_horizontal_scale_in_period(period=period, frequency=f)
                gain2 = self.instruments.inst_mdo2.mdo_gain(source1=1, source2=2, frequency=f, period=period)

                logger.debug("Freq : %s - Gain : %s - Phase Osc : %s - Phase Np : %s" % (f, gain, phase_osc, phase_np))
                logger.debug("Freq : %s - Gain2 : %s - Phase2 Osc : %s - Phase2 Np : %s" %
                             (f, gain2, phase_osc2, phase_np2))

                timevalues = time.time()
                self.write_values_to_db(data={'Bode_Freq': [f], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Gain': [gain], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Phase': [phase_osc], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Phase_numpy': [phase_np], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Gain2': [gain2], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Phase2': [phase_osc2], 'timevalues': [timevalues]})
                self.write_values_to_db(data={'Bode_Phase_numpy2': [phase_np2], 'timevalues': [timevalues]})

            logger.debug("Bode end")
            self.write_variable_property("LABOREM", "viewer_stop_timeline", 1, value_class="BOOLEAN",
                                         timestamp=now())
            time.sleep(2)
            self.write_variable_property("LABOREM", "message_laborem", "", value_class='string')
            self.write_variable_property(variable_name='Bode_run', property_name='BODE_5_LOOP_COMPARE', value=0,
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
            self.instruments.inst_afg.reset_instrument()
            self.instruments.inst_mdo.reset_instrument()
            time.sleep(2)

            # Prepare AFG for Bode : output1 on, output imp max
            self.instruments.inst_afg.afg_prepare_for_bode(ch=1)

            # Set generator Vpp
            vepp = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_2_VEPP')
            self.instruments.inst_afg.afg_set_vpp(ch=1, vpp=vepp)

            # Prepare MDO trigger, channel 1 vertical scale, bandwidth
            self.instruments.inst_mdo.mdo_prepare_for_bode(vpp=vepp)

            # Set generator function shape
            func_shape = self.read_variable_property(variable_name='Spectre_run',
                                                     property_name='SPECTRE_3_FUNCTION_SHAPE')
            self.instruments.inst_afg.afg_set_function_shape(ch=1, function_shape=func_shape)

            # Set the generator frequency to f
            f = self.read_variable_property(variable_name='Spectre_run', property_name='SPECTRE_1_F')
            self.instruments.inst_afg.afg_set_frequency(ch=1, frequency=f)

            # Set the oscilloscope horizontal scale and vertical scale for the output
            range_i = None
            self.instruments.inst_mdo.mdo_find_vertical_scale(ch=2, frequency=f, range_i=range_i)

            self.instruments.inst_mdo.mdo_horizontal_scale_in_period(period=4.0, frequency=f)

            resolution = 10000
            scaled_wave_ch1 = self.instruments.inst_mdo.mdo_query_waveform(
                ch=1, points_resolution=resolution, frequency=f, refresh=True)
            scaled_wave_ch2 = self.instruments.inst_mdo.mdo_query_waveform(
                ch=2, points_resolution=resolution, frequency=f, refresh=False)

            scaled_wave_ch1_mini = list()
            scaled_wave_ch2_mini = list()
            time_values = list()
            time_values_to_show = list()
            time_now = time.time()

            # Prepare the lists to save
            save_resolution = min(100, len(scaled_wave_ch1), len(scaled_wave_ch2))
            logger.debug('save_resolution : %s' % save_resolution)
            for i in range(0, save_resolution):
                # store one value each ms
                time_values.append(time_now + 0.001 * i)
                # store time in ms
                time_values_to_show.append(0.001 * i * self.instruments.inst_mdo.mdo_horizontal_time() * 1000 * 10)
                scaled_wave_ch1_mini.append(scaled_wave_ch1[i * int(len(scaled_wave_ch1) / save_resolution)])
                scaled_wave_ch2_mini.append(scaled_wave_ch2[i * int(len(scaled_wave_ch2) / save_resolution)])

            # FFT CH1
            spectrum_hanning_1 = self.instruments.inst_mdo.fft(scaled_wave_ch1)
            tscale = self.instruments.inst_mdo.mdo_xincr()
            frequencies = np.linspace(0, 1 / tscale, len(scaled_wave_ch1), endpoint=False).tolist()
            # FFT CH2
            spectrum_hanning_2 = self.instruments.inst_mdo.fft(scaled_wave_ch2)

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


def connect_check_visa(config, idn=True):
    inst = None
    range_i = range(0, 10)
    for i in range_i:
        try:
            inst = config.get_device_instance().get_handler_instance()
        except Device.DoesNotExist:
            logger.error("Script Laborem - Device %s does not exist" % config)
        except AttributeError:
            logger.error("Script Laborem - The motherboard does not have the good IO configuration for this script.")
        if inst is not None and inst.inst is not None:
            try:
                if idn:
                    logger.debug(inst.inst.query("*IDN?"))
                break
            except visa.VisaIOError:
                logger.error("%s - visa.VisaIOError for device : %s" % (i, config))
                if i == max(range_i):
                    inst = None
            except AttributeError as e:
                logger.error("%s - visa.AttributeError for device : %s - %s" % (i, config, e))
                if i == max(range_i):
                    inst = None
            except UnicodeDecodeError:
                logger.error("Script Laborem - Device %s - UnicodeDecodeError" % config)
        time.sleep(10)
    return inst


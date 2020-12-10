# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)
# -*- coding: utf-8 -*-
"""Object based access to the robot Tergane 45 from Terel


Example::
    from pyscada.laborem.scripts.Robot_Tergane45 import Tergane45
    unit = Tergane45()
    import pyvisa
    import time
    visa_backend = '@py'  # use PyVISA-py as backend
    rm = pyvisa.ResourceManager(visa_backend)
    inst = rm.open_resource('ASRL/dev/ttyS0::INSTR', baud_rate=9600, data_bits=8, parity=pyvisa.constants.Parity.none,
        stop_bits=pyvisa.constants.StopBits.one, write_termination='')
    unit.connect(inst)
    unit.init()
    unit.pince(0)
    time.sleep(1)
    unit.pince(1)

"""
__author__ = "Camille Lavayssière"
__copyright__ = "Copyright 2020, UPPA"
__credits__ = []
__license__ = "GPLv3"
__version__ = "0.1.0"
__maintainer__ = "Camille Lavayssière"
__email__ = "clavayssiere@univ-pau.fr"
__status__ = "Beta"
__docformat__ = 'reStructuredText'


class Tergane45(object):

    def __init__(self):
        self.instr = None
        self.old_theta = 0

    def connect(self, instr):
        if self.instr is None and instr is None:
            return
        self.instr = instr

    def init(self):
        # on tourne le bras
        self.rotation_base(0)
        # on baisse le bras
        self.prepare_epaule_coude_poignet(17, 1, 2)
        # on ouvre la pince
        self.pince(1)
        self.pince(0)

    def take_and_drop(self, r1, theta1, z1, r2, theta2, z2):
        # init
        self.pince(1)
        # prepare_epaule_coude_poignet(20, 5, 3)
        # rotation_base(0)
        # on place le bras pour prendre
        self.prepare_epaule_coude_poignet(r1, z1, 1)
        # on tourne le bras pour prendre
        self.rotation_base(theta1)
        # on ferme la pince
        self.pince(0)
        # on leve le bras
        self.prepare_epaule_coude_poignet(r1, 4, 2)
        self.prepare_epaule_coude_poignet(r2, 4, 1)
        # on tourne le bras pour deposer
        self.rotation_base(theta2)
        # on place le bras pour deposer
        self.prepare_epaule_coude_poignet(r2, sum([z2], 0.8), 3)
        # on ouvre la pince
        self.pince(1)
        # on se releve
        self.prepare_epaule_coude_poignet(r2, 4, 2)
        # prepare_epaule_coude_poignet(20, 4, 3)
        self.rotation_base(0)
        return True

    def format_ascii(self, rot_ascii, axe):
        if rot_ascii < 0:
            ret = axe + '-' + str(int(rot_ascii))[1:].zfill(3)
            return ret
        else:
            ret = axe + '+' + str(int(rot_ascii)).zfill(3)
            return ret

    def deg_to_ascii(self, angle_deg, angle_max_deg):
        return int(min(max(angle_deg, -angle_max_deg), angle_max_deg) * 511 / angle_max_deg)

    def prepare_epaule_coude_poignet(self, r, z, mouvement):
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
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                                angle_max_poignet), 'F'))
            time.sleep(temps_entre_cmd)
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(temps_entre_cmd)
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(1)
        elif mouvement == 2:
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(temps_entre_cmd)
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(temps_entre_cmd)
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                                angle_max_poignet), 'F'))
            time.sleep(1)
        elif mouvement == 3:
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(temps_entre_cmd)
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(temps_entre_cmd)
            self.instr.write(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                                angle_max_poignet), 'F'))
            time.sleep(1)
        return True

    def rotation_base(self, theta):
        angle_max_base = 130
        theta_base = theta * np.pi / 180
        self.instr.write(self.format_ascii(self.deg_to_ascii(theta_base * 180 / np.pi, angle_max_base), 'B'))
        try:
            theta = 0.0 - self.old_theta
            tempo = abs(sum([self.deg_to_ascii(theta_base * 180 / np.pi, angle_max_base), theta])) * 5000 / 1024
            time.sleep(tempo / 1000)
            self.old_theta = self.deg_to_ascii(theta_base * 180 / np.pi, angle_max_base)
        except Exception as e:
            logger.warning(e)
            time.sleep(3)
        return True

    def pince(self, openclose):
        if openclose == 0:
            self.instr.write('P+511')
            time.sleep(1.7)
        else:
            self.instr.write('P-511')
            time.sleep(1.7)
        return True


class Handler(GenericDevice):
    """
    Tergane 45 Robot from Terel
    """
    device = None

    def connect(self):
        super(Handler, self).connect()
        self.device = Tergane45()
        self.device.connect(self.inst)

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        return None

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        return None

    def parse_value(self, value):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        return None

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
import numpy as np
import time
import logging
from pyvisa.errors import VisaIOError

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
inst = rm.open_resource('ASRL/dev/serial0::INSTR', baud_rate=9600, data_bits=8, parity=pyvisa.constants.Parity.none, stop_bits=pyvisa.constants.StopBits.one, write_termination='')
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
        try:
            logger.debug(self.instr.read_raw())
        except:
            pass
        # on tourne le bras
        self.rotation_base(0)
        # on baisse le bras
        self.prepare_epaule_coude_poignet(17, 1, 2)
        # on ouvre la pince
        # self.pince(1)
        # self.pince(0)
        # self.pince(1)

    def query(self, write_sring):
        self.instr.timeout = 50
        i = 0
        while i < 10:
            while True:
                try:
                    self.instr.read_raw()
                except VisaIOError:
                    break
            self.instr.write(write_sring)
            r1 = str(self.instr.read_raw())
            r2 = str(self.instr.read_raw())
            if write_sring in r1 and 'MESSAGE CORRECT' in r2:
                #logger.debug(write_sring + ' ok')
                break
            else:
                i += 1
                logger.debug(write_sring + ' nok')
                logger.debug(r1)
                logger.debug(r2)
                time.sleep(1)

    def take_and_drop(self, to_take, to_drop):
        r_to_take = to_take.R
        theta_to_take = to_take.theta
        z_to_take = to_take.z
        r_to_drop = to_drop.R
        theta_to_drop = to_drop.theta
        z_to_drop = to_drop.z
        self._take_and_drop(r_to_take, theta_to_take, z_to_take, r_to_drop, theta_to_drop, z_to_drop)

    def _take_and_drop(self, r1, theta1, z1, r2, theta2, z2):
        # on ouvre la pince
        self.pince(1)
        # prepare_epaule_coude_poignet(20, 5, 3)
        # rotation_base(0)
        # on place le bras pour prendre en l'air
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

        temps_entre_cmd = 0.05

        xp = r
        yp = z - l_base + l_poignet

        r_alpha = (xp ** 2 + yp ** 2 - l_epaule ** 2 - l_coude ** 2) / (-2 * l_epaule * l_coude)
        alpha = np.arccos(r_alpha)
        theta_coude = -np.pi + alpha

        theta_5 = np.arctan2(yp, xp) + np.arcsin(l_coude * np.sin(alpha) / (xp ** 2 + yp ** 2) ** 0.5)
        theta_epaule = -np.pi / 4 + theta_5

        theta_poignet = -np.pi / 2 - np.pi / 4 - theta_epaule - theta_coude

        if mouvement == 1:
            self.query(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                           angle_max_poignet), 'F'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(1)
        elif mouvement == 2:
            self.query(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                           angle_max_poignet), 'F'))
            time.sleep(1)
        elif mouvement == 3:
            self.query(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                           angle_max_poignet), 'F'))
            time.sleep(1)
        elif mouvement == 4:
            self.query(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                           angle_max_poignet), 'F'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(1)
        elif mouvement == 5:
            self.query(self.format_ascii(self.deg_to_ascii(theta_epaule * 180 / np.pi, angle_max_epaule), 'E'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_poignet * 180 / np.pi + correction_angle_poignet,
                                                           angle_max_poignet), 'F'))
            time.sleep(temps_entre_cmd)
            self.query(self.format_ascii(self.deg_to_ascii(theta_coude * 180 / np.pi, angle_max_coude), 'C'))
            time.sleep(1)
        return True

    def rotation_base(self, theta):
        angle_max_base = 130
        theta_base = theta * np.pi / 180
        self.query(self.format_ascii(self.deg_to_ascii(theta_base * 180 / np.pi, angle_max_base), 'B'))
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
            self.query('P+511')
            time.sleep(1.7)
        else:
            self.query('P-511')
            time.sleep(1.7)
        return True

    def set_bases(self, bases_dict):
        logger.debug("set_bases")
        temp_actions = dict()

        # Find moves between bases
        for i in bases_dict.keys():
            if bases_dict[i].requested_element is None:
                continue
            if bases_dict[i].requested_element == bases_dict[i].element:
                # Nothing to move
                logger.debug("Nothing to do")
                pass
            elif bases_dict[i].element is not None and \
                    bases_dict[i].requested_element.value == bases_dict[i].element.value and \
                    bases_dict[i].requested_element.unit == bases_dict[i].element.unit:
                # Replace requested element by is brother
                logger.debug("Replace req element by element")
                bases_dict[i].requested_element = bases_dict[i].element
                bases_dict[i].save()
                while bases_dict[i].requested_element != bases_dict[i].element:
                    bases_dict[i].refresh_from_db()
                    logger.debug("Waiting to replace req element by element...")
                    time.sleep(1)
            else:
                # Find requested element in other base
                for j in bases_dict.keys():
                    if i != j and bases_dict[j].element is not None \
                            and bases_dict[i].requested_element == bases_dict[j].element:
                        # Req element in other base
                        logger.debug("Req element in other base")
                        temp_actions[i] = bases_dict[j]
                        break
                if i not in temp_actions.keys():
                    logger.debug("Not in other base")
                    temp_actions[i] = None

        # Break loops
        for i in bases_dict.keys():
            stop = False
            k = i
            count = 0
            while not stop and len(temp_actions):
                if k in temp_actions.keys():
                    count += 1
                    if temp_actions[k] == bases_dict[i]:
                        if count == 1:
                            logger.debug("Something is strange !")
                            stop = True
                        else:
                            logger.debug("Temp actions is a loop")
                            stop = True
                            temp_actions[k] = None
                    elif temp_actions[k] is not None and temp_actions[k].id in temp_actions.keys():
                        k = temp_actions[k].id
                        logger.debug("Replacing k")
                    else:
                        logger.debug("Temp actions is not a loop")
                        stop = True
                else:
                    stop = True

        while len(temp_actions):
            actions = dict()
            logger.debug("loop temp actions")
            logger.debug(temp_actions.keys())
            logger.debug(temp_actions.values())
            for i in temp_actions.keys():
                if bases_dict[i] not in temp_actions.values():
                    logger.debug("First action" + str(i))
                    actions[i] = temp_actions[i]
                else:
                    logger.debug("base " + str(i) + ": " + str(bases_dict[i]) + " - in temp action : ")

            for i in actions.keys():
                del temp_actions[i]
                self.unset_base(bases_dict[i])
                if actions[i] is None:
                    self.set_base(bases_dict[i])
                else:
                    self.move_base(actions[i], bases_dict[i])

    def unset_base(self, base):
        logger.debug("unset_base")
        if base.element is not None:
            self.take_and_drop(base, base.element)
            base.element = None
            base.save()
            while base.element is not None:
                base.refresh_from_db()
                time.sleep(1)

    def set_base(self, base):
        logger.debug("set_base")
        self.take_and_drop(base.requested_element, base)
        base.element = base.requested_element
        base.save()
        while base.element != base.requested_element:
            base.refresh_from_db()
            time.sleep(1)

    def move_base(self, base1, base2):
        logger.debug("move_base")
        self.take_and_drop(base1, base2)
        e = base1.element
        base2.element = e
        base2.save()
        base1.element = None
        base1.save()
        while base2.element != e or base1.element is not None:
            base2.refresh_from_db()
            base1.refresh_from_db()
            time.sleep(1)


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

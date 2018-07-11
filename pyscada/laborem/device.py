# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, device):
        pass

    def request_data(self):
        """
        request data from the instrument/device
        """
        return False

    def write_data(self,variable_id, value, task):
        '''
        write value to the instrument/device
        '''
        return False

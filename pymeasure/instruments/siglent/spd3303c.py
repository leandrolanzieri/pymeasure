#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

CONTROLLABLE_CHANNELS = [1, 2]
"List of controllable channels on the power supply"

ALL_CHANNELS = CONTROLLABLE_CHANNELS + [3]
"List of all channels on the power supply"

CHANNEL_STATUS_VALUE_MAP = {True: 'ON', False: 'OFF'}
"Values map for channel status validator"

CHANNEL_VOLTAGE_RANGE = [0.0, 32.0]
"Range of valid voltage values for the controllable channels"

CHANNEL_CURRENT_RANGE = [0, 3.2]
"Range of valid current values for the controllable channels"

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SPD3303C(Instrument):
    """ Represents the imaginary Siglent SPD3303C Power Supply.

    .. code-block:: python

        # TODO: Check
        pwr_supply = SPD3303C("/dev/usbtmc0")

        pwr_supply.ch1_voltage = 3.3        # set CH1 voltage
        pwr_supply.ch1_current = 0.5        # limit CH1 current to 0.5 A
        pwr_supply.ch1_status = True        # turn CH1 ON
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            'Siglent SPD3303C',
            **kwargs
        )
        self.ch1_status = False
        self.ch2_status = False
        self.ch3_status = False

    def _get_system_status(self):
        """Asks for the current system status.

        Return
            Integer value representing the current system status.
        """
        response = self.ask('SYSTem:STATus?').split('0x')[1]
        return int(response, 16)

    @staticmethod
    def _decode_channel_status(status, channel):
        """Decodes the system `status` to get status of a `channel`

        Arguments
            `status`: System status integer to decode.
            `channel`: Number of the channel whose status to get.

        Return
            `ON` if the channel is ON, `OFF` otherwise.
        """
        assert(channel in CONTROLLABLE_CHANNELS)
        mask = 1 << (channel + 3)
        return 'ON' if (status & mask) != 0 else 'OFF'

    ch1_status = Instrument.control(
        'SYSTem:STATus?',
        'OUTPut CH1,%s',
        """Sets the channel 1 status, ON (True) or OFF (False)""",
        validator=strict_discrete_set,
        values=CHANNEL_STATUS_VALUE_MAP,
        get_process=lambda status: SPD3303C._decode_channel_status(status, 1),
    )

    ch2_status = Instrument.control(
        'SYSTem:STATus?',
        'OUTPut CH2,%s',
        """Sets the channel 2 status, ON (True) or OFF (False)""",
        validator=strict_discrete_set,
        values=CHANNEL_STATUS_VALUE_MAP,
        get_process=lambda status: SPD3303C._decode_channel_status(status, 2),
    )

    ch3_status = Instrument.setting(
        'OUTPut CH3,%s',
        """Sets the channel 3 status, ON (True) or OFF (False)""",
        validator=strict_discrete_set,
        values=CHANNEL_STATUS_VALUE_MAP,
    )

    ch1_voltage = Instrument.control(
        'CH1:VOLTage %s',
        'CH1:VOLTage?',
        """Sets or queries the voltage of channel 1 in Volts""",
        validator=strict_range,
        values=CHANNEL_VOLTAGE_RANGE,
    )

    ch2_voltage = Instrument.control(
        'CH2:VOLTage %s',
        'CH2:VOLTage?',
        """Sets or queries the voltage of channel 2 in Volts""",
        validator=strict_range,
        values=CHANNEL_VOLTAGE_RANGE,
    )

    ch1_current = Instrument.control(
        'CH1:CURRent %s',
        'CH1:CURRent?',
        """Sets or queries the current of channel 1 in Amperes""",
        validator=strict_range,
        values=CHANNEL_CURRENT_RANGE,
    )

    ch2_current = Instrument.control(
        'CH2:CURRent %s',
        'CH2:CURRent?',
        """Sets or queries the current of channel 2 in Amperes""",
        validator=strict_range,
        values=CHANNEL_CURRENT_RANGE,
    )

    ch1_instant_voltage = Instrument.measurement(
        'MEASure:VOLTage? CH1',
        """Measures the instantaneous voltage of channel 1 in Volts""",
    )

    ch2_instant_voltage = Instrument.measurement(
        'MEASure:VOLTage? CH2',
        """Measures the instantaneous voltage of channel 2 in Volts""",
    )

    ch1_instant_current = Instrument.measurement(
        'MEASure:CURRent? CH1',
        """Measures the instantaneous current of channel 1 in Amperes""",
    )

    ch2_instant_current = Instrument.measurement(
        'MEASure:CURRent? CH2',
        """Measures the instantaneous current of channel 2 in Amperes""",
    )

    def shutdown(self):
        """Turn all channels OFF and close connection to the device."""
        self.ch1_status = False
        self.ch2_status = False
        self.ch3_status = False
        super().shutdown()

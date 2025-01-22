#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.instruments.keithley.buffer import KeithleyBuffer

import numpy as np
import time

log = logging.getLogger(__name__)
for handler in log.handlers[:]:
    log.removeHandler(handler)
log.addHandler(logging.NullHandler())

def clist_validator(value, values):
    """ Provides a validator function that returns a valid clist string
    for channel commands of the Keithley 2700. Otherwise it raises a
    ValueError.

    :param value: A value to test
    :param values: A range of values (range, list, etc.)
    :raises: ValueError if the value is out of the range
    """
    # Convert value to list of strings
    if isinstance(value, str):
        clist = [value.strip(" @(),")]
    elif isinstance(value, (int, float)):
        clist = [f"{value:d}"]
    elif isinstance(value, (list, tuple, np.ndarray, range)):
        clist = [f"{x:d}" for x in value]
    else:
        raise ValueError(f"Type of value ({type(value)}) not valid")

    # Pad numbers to length (if required)
    clist = [c.rjust(2, "0") for c in clist]
    clist = [c.rjust(3, "1") for c in clist]

    # Check channels against valid channels
    for c in clist:
        if int(c) not in values:
            raise ValueError(
                f"Channel number {value:g} not valid."
            )

    # Convert list of strings to clist format
    clist = "(@{:s})".format(", ".join(clist))

    return clist


def text_length_validator(value, values):
    """ Provides a validator function that a valid string for the display
    commands of the Keithley. Raises a TypeError if value is not a string.
    If the string is too long, it is truncated to the correct length.

    :param value: A value to test
    :param values: The allowed length of the text
    """

    if not isinstance(value, str):
        raise TypeError("Value is not a string.")

    return value[:values]


class Keithley2700_with_7700(Instrument, KeithleyBuffer):
    """ Represents the Keithely 2700 Multimeter/Switch System and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2700("GPIB::1")

    """

    CLIST_VALUES = list(range(101, 300))

    # Routing commands
    closed_channels = Instrument.control(
        "ROUTe:MULTiple:CLOSe?", "ROUTe:MULTiple:CLOSe %s",
        """ Parameter that controls the opened and closed channels.
        All mentioned channels are closed, other channels will be opened.
        """,
        validator=clist_validator,
        values=CLIST_VALUES,
        check_get_errors=True,
        check_set_errors=True,
        separator=None,
        get_process=lambda v: [
            int(vv) for vv in (v.strip(" ()@,").split(",")) if not vv == ""
        ],
    )

    open_channels = Instrument.setting(
        "ROUTe:MULTiple:OPEN %s",
        """ A parameter that opens the specified list of channels. Can only
        be set.
        """,
        validator=clist_validator,
        values=CLIST_VALUES,
        check_set_errors=True
    )
    
    def get_state_of_channels(self, channels):
        """ Get the open or closed state of the specified channels

        :param channels: a list of channel numbers, or single channel number
        """
        #clist = clist_validator(channels, self.CLIST_VALUES)
        clist = clist_validator(channels, self.CLIST_VALUES)
        state = self.ask("ROUTe:CLOSe:STATe? %s" % clist)
        return state

    def open_all_channels(self):
        """ Open all channels of the Keithley 2700.
        """
        self.write(":ROUTe:OPEN:ALL")
        
    def close_channels(self, channels):
        clist = clist_validator(channels, self.CLIST_VALUES)
        self.write("ROUTe:MULT:CLOSe %s" % clist)

    def close_23(self):
        self.write("ROUT:MULT:CLOS (@123)")

    def __init__(self, adapter, name="Keithley 2700 MultiMeter/Switch System", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

        self.check_errors()
        self.determine_valid_channels()
        self.open_all_channels()

    def determine_valid_channels(self):
        """ Determine what cards are installed into the Keithley 2700
        and from that determine what channels are valid.
        """
        self.CLIST_VALUES.clear()

        self.cards = {slot: card for slot, card in enumerate(self.options, 1)}

        for slot, card in self.cards.items():

            if card == "NONE":
                continue
            elif card == "7700":
                channels = range(1, 25)
            elif card == "7709":
                """The 7709 is a 6(rows) x 8(columns) matrix card, with two
                additional switches (49 & 50) that allow row 1 and 2 to be
                connected to the DMM backplane (input and sense respectively).
                """
                channels = range(1, 51)
            else:
                log.warning(
                    f"Card type {card} at slot {slot} is not yet implemented."
                )
                continue

            channels = [100 * slot + ch for ch in channels]

            self.CLIST_VALUES.extend(channels)

    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', '')
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("Keithley 2700 reported error: %d, %s" % (code, message))
            print(code, message)
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2700 error retrieval.")

    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    options = Instrument.measurement(
        "*OPT?",
        """Property that lists the installed cards in the Keithley 2700.
        Returns a dict with the integer card numbers on the position.""",
        cast=False
    )

    ###########
    # DISPLAY #
    ###########

    text_enabled = Instrument.control(
        "DISP:TEXT:STAT?", "DISP:TEXT:STAT %d",
        """ A boolean property that controls whether a text message can be
        shown on the display of the Keithley 2700.
        """,
        values={True: 1, False: 0},
        map_values=True,
    )
    display_text = Instrument.control(
        "DISP:TEXT:DATA?", "DISP:TEXT:DATA '%s'",
        """ A string property that controls the text shown on the display of
        the Keithley 2700. Text can be up to 12 ASCII characters and must be
        enabled to show.
        """,
        validator=text_length_validator,
        values=12,
        cast=str,
        separator="NO_SEPARATOR",
        get_process=lambda v: v.strip("'\""),
    )

    def display_closed_channels(self):
        """ Show the presently closed channels on the display of the Keithley
        2700.
        """

        # Get the closed channels and make a string of the list
        channels = self.closed_channels
        channel_string = " ".join([
            str(channel % 100) for channel in channels
        ])

        # Prepend "Closed: " or "C: " to the string, depending on the length
        str_length = 12
        if len(channel_string) < str_length - 8:
            channel_string = "Closed: " + channel_string
        elif len(channel_string) < str_length - 3:
            channel_string = "C: " + channel_string

        # enable displaying text-messages
        self.text_enabled = True

        # write the string to the display
        self.display_text = channel_string
        
###############################################################################        
        
#sourcemeter = Keithley2700_with_7700("GPIB::3")
#print(sourcemeter.get_state_of_channels([1,2,3]))
#sourcemeter.close_channels([1])
#print(sourcemeter.get_state_of_channels([1,2,3]))
#sourcemeter.reset() 
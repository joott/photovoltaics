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
import time

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from pymeasure.instruments.keithley.buffer import KeithleyBuffer


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2400(KeithleyBuffer, Instrument):
    """ Represents the Keithley 2400 SourceMeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2400("GPIB::1")

        keithley.apply_current()                # Sets up to source current
        keithley.source_current_range = 10e-3   # Sets the source current range to 10 mA
        keithley.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        keithley.source_current = 0             # Sets the source current to 0 mA
        keithley.enable_source()                # Enables the source output

        keithley.measure_voltage()              # Sets up to measure voltage

        keithley.ramp_to_current(5e-3)          # Ramps the current to 5 mA
        print(keithley.voltage)                 # Prints the voltage in Volts

        keithley.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    source_mode = Instrument.control(
        ":SOUR:FUNC?", ":SOUR:FUNC %s",
        """ A string property that controls the source mode, which can
        take the values 'current' or 'voltage'. The convenience methods
        :meth:`~.Keithley2400.apply_current` and :meth:`~.Keithley2400.apply_voltage`
        can also be used. """,
        validator=strict_discrete_set,
        values={'current': 'CURR', 'voltage': 'VOLT'},
        map_values=True
    )

    source_enabled = Instrument.control(
        "OUTPut?", "OUTPut %d",
        """A boolean property that controls whether the source is enabled, takes
        values True or False. The convenience methods :meth:`~.Keithley2400.enable_source` and
        :meth:`~.Keithley2400.disable_source` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    auto_output_off = Instrument.control(
        ":SOUR:CLE:AUTO?", ":SOUR:CLE:AUTO %d",
        """ A boolean property that enables or disables the auto output-off.
        Valid values are True (output off after measurement) and False (output
        stays on after measurement). """,
        values={True: 1, False: 0},
        map_values=True,
    )

    source_delay = Instrument.control(
        ":SOUR:DEL?", ":SOUR:DEL %g",
        """ A floating point property that sets a manual delay for the source
        after the output is turned on before a measurement is taken. When this
        property is set, the auto delay is turned off. Valid values are
        between 0 [seconds] and 999.9999 [seconds].""",
        validator=truncated_range,
        values=[0, 999.9999],
    )

    source_delay_auto = Instrument.control(
        ":SOUR:DEL:AUTO?", ":SOUR:DEL:AUTO %d",
        """ A boolean property that enables or disables auto delay. Valid
        values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    auto_zero = Instrument.control(
        ":SYST:AZER:STAT?", ":SYST:AZER:STAT %s",
        """ A property that controls the auto zero option. Valid values are
        True (enabled) and False (disabled) and 'ONCE' (force immediate). """,
        values={True: 1, False: 0, "ONCE": "ONCE"},
        map_values=True,
    )

    line_frequency = Instrument.control(
        ":SYST:LFR?", ":SYST:LFR %d",
        """ An integer property that controls the line frequency in Hertz.
        Valid values are 50 and 60. """,
        validator=strict_discrete_set,
        values=[50, 60],
        cast=int,
    )

    line_frequency_auto = Instrument.control(
        ":SYST:LFR:AUTO?", ":SYST:LFR:AUTO %d",
        """ A boolean property that enables or disables auto line frequency.
        Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    measure_concurent_functions = Instrument.control(
        ":SENS:FUNC:CONC?", ":SENS:FUNC:CONC %d",
        """ A boolean property that enables or disables the ability to measure
        more than one function simultaneously. When disabled, volts function
        is enabled. Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        ":READ?",
        """ Reads the current in Amps, if configured for this reading.
        """
    )
    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ A floating point property that controls the measurement current
        range in Amps, which can take values between -1.05 and +1.05 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )
    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?", ":SENS:CURR:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    compliance_current = Instrument.control(
        ":SENS:CURR:PROT?", ":SENS:CURR:PROT %g",
        """ A floating point property that controls the compliance current
        in Amps. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )
    source_current = Instrument.control(
        ":SOUR:CURR?", ":SOUR:CURR:LEV %g",
        """ A floating point property that controls the source current
        in Amps. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )
    source_current_range = Instrument.control(
        ":SOUR:CURR:RANG?", ":SOUR:CURR:RANG:AUTO 0;:SOUR:CURR:RANG %g",
        """ A floating point property that controls the source current
        range in Amps, which can take values between -1.05 and +1.05 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":READ?",
        """ Reads the voltage in Volts, if configured for this reading.
        """
    )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ A floating point property that controls the measurement voltage
        range in Volts, which can take values from -210 to 210 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-210, 210]
    )
    voltage_nplc = Instrument.control(
        ":SENS:VOLT:NPLC?", ":SENS:VOLT:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    compliance_voltage = Instrument.control(
        ":SENS:VOLT:PROT?", ":SENS:VOLT:PROT %g",
        """ A floating point property that controls the compliance voltage
        in Volts. """,
        validator=truncated_range,
        values=[-210, 210]
    )
    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT:LEV %g",
        """ A floating point property that controls the source voltage
        in Volts. """
    )
    source_voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG:AUTO 0;:SOUR:VOLT:RANG %g",
        """ A floating point property that controls the source voltage
        range in Volts, which can take values from -210 to 210 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-210, 210]
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":READ?",
        """ Reads the resistance in Ohms, if configured for this reading.
        """
    )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %g",
        """ A floating point property that controls the resistance range
        in Ohms, which can take values from 0 to 210 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 210e6]
    )
    resistance_nplc = Instrument.control(
        ":SENS:RES:NPLC?", ":SENS:RES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 2-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    wires = Instrument.control(
        ":SYSTEM:RSENSE?", ":SYSTEM:RSENSE %d",
        """ An integer property that controls the number of wires in
        use for resistance measurements, which can take the value of
        2 or 4.
        """,
        validator=strict_discrete_set,
        values={4: 1, 2: 0},
        map_values=True
    )

    buffer_points = Instrument.control(
        ":TRAC:POIN?", ":TRAC:POIN %d",
        """ An integer property that controls the number of buffer points. This
        does not represent actual points in the buffer, but the configuration
        value instead. """,
        validator=truncated_range,
        values=[1, 2500],
        cast=int
    )
    means = Instrument.measurement(
        ":CALC3:FORM MEAN;:CALC3:DATA?;",
        """ Reads the calculated means (averages) for voltage,
        current, and resistance from the buffer data  as a list. """
    )
    maximums = Instrument.measurement(
        ":CALC3:FORM MAX;:CALC3:DATA?;",
        """ Returns the calculated maximums for voltage, current, and
        resistance from the buffer data as a list. """
    )
    minimums = Instrument.measurement(
        ":CALC3:FORM MIN;:CALC3:DATA?;",
        """ Returns the calculated minimums for voltage, current, and
        resistance from the buffer data as a list. """
    )
    standard_devs = Instrument.measurement(
        ":CALC3:FORM SDEV;:CALC3:DATA?;",
        """ Returns the calculated standard deviations for voltage,
        current, and resistance from the buffer data as a list. """
    )

    ###########
    # Trigger #
    ###########

    trigger_count = Instrument.control(
        ":TRIG:COUN?", ":TRIG:COUN %d",
        """ An integer property that controls the trigger count,
        which can take values from 1 to 9,999. """,
        validator=truncated_range,
        values=[1, 2500],
        cast=int
    )
    trigger_delay = Instrument.control(
        ":TRIG:SEQ:DEL?", ":TRIG:SEQ:DEL %g",
        """ A floating point property that controls the trigger delay
        in seconds, which can take values from 0 to 999.9999 s. """,
        validator=truncated_range,
        values=[0, 999.9999]
    )

    ###########
    # Filters #
    ###########

    filter_type = Instrument.control(
        ":SENS:AVER:TCON?", ":SENS:AVER:TCON %s",
        """ A String property that controls the filter's type.
        REP : Repeating filter
        MOV : Moving filter""",
        validator=strict_discrete_set,
        values=['REP', 'MOV'],
        map_values=False)

    filter_count = Instrument.control(
        ":SENS:AVER:COUNT?", ":SENS:AVER:COUNT %d",
        """ A integer property that controls the number of readings that are
        acquired and stored in the filter buffer for the averaging""",
        validator=truncated_range,
        values=[1, 100],
        cast=int)

    filter_state = Instrument.control(
        ":SENS:AVER?", ":SENS:AVER %s",
        """ A string property that controls if the filter is active.""",
        validator=strict_discrete_set,
        values=['ON', 'OFF'],
        map_values=False)

    #####################
    # Output subsystem #
    #####################

    output_off_state = Instrument.control(
        ":OUTP:SMOD?", ":OUTP:SMOD %s",
        """ Select the output-off state of the SourceMeter.
        HIMP : output relay is open, disconnects external circuitry.
        NORM : V-Source is selected and set to 0V, Compliance is set to 0.5%
        full scale of the present current range.
        ZERO : V-Source is selected and set to 0V, compliance is set to the
        programmed Source I value or to 0.5% full scale of the present current
        range, whichever is greater.
        GUAR : I-Source is selected and set to 0A""",
        validator=strict_discrete_set,
        values=['HIMP', 'NORM', 'ZERO', 'GUAR'],
        map_values=False)

    ####################
    # Methods        #
    ####################

    def __init__(self, adapter, name="Keithley 2400 SourceMeter", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    def four_probe(self):
        self.write(":SYST:RSEN ON")
    
    def enable_source(self):
        """ Enables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTPUT ON")

    def disable_source(self):
        """ Disables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTPUT OFF")

    def measure_resistance(self, nplc=1, resistance=2.1e5, auto_range=True):
        """ Configures the measurement of resistance.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param resistance: Upper limit of resistance in Ohms, from -210 MOhms to 210 MOhms
        :param auto_range: Enables auto_range if True, else uses the set resistance
        """
        log.info("%s is measuring resistance." % self.name)
        self.write(":SENS:FUNC 'RES';"
                   ":SENS:RES:MODE MAN;"
                   ":SENS:RES:NPLC %f;:FORM:ELEM RES;" % nplc)
        if auto_range:
            self.write(":SENS:RES:RANG:AUTO 1;")
        else:
            self.resistance_range = resistance
        self.check_errors()

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param voltage: Upper limit of voltage in Volts, from -210 V to 210 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        log.info("%s is measuring voltage." % self.name)
        self.write(":SENS:FUNC 'VOLT';"
                   ":SENS:VOLT:NPLC %f;:FORM:ELEM VOLT;" % nplc)
        if auto_range:
            self.write(":SENS:VOLT:RANG:AUTO 1;")
        else:
            self.voltage_range = voltage
        self.check_errors()

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -1.05 A to 1.05 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
        log.info("%s is measuring current." % self.name)
        self.write(":SENS:FUNC 'CURR';"
                   ":SENS:CURR:NPLC %f;:FORM:ELEM CURR;" % nplc)
        if auto_range:
            self.write(":SENS:CURR:RANG:AUTO 1;")
        else:
            self.current_range = current
        self.check_errors()

    def auto_range_source(self):
        """ Configures the source to use an automatic range.
        """
        if self.source_mode == 'current':
            self.write(":SOUR:CURR:RANG:AUTO 1")
        else:
            self.write(":SOUR:VOLT:RANG:AUTO 1")

    def apply_current(self, current_range=None,
                      compliance_voltage=0.1):
        """ Configures the instrument to apply a source current, and
        uses an auto range unless a current range is specified.
        The compliance voltage is also set.

        :param compliance_voltage: A float in the correct range for a
                                   :attr:`~.Keithley2400.compliance_voltage`
        :param current_range: A :attr:`~.Keithley2400.current_range` value or None
        """
        log.info("%s is sourcing current." % self.name)
        self.source_mode = 'current'
        if current_range is None:
            self.auto_range_source()
        else:
            self.source_current_range = current_range
        self.compliance_voltage = compliance_voltage
        self.check_errors()

    def apply_voltage(self, voltage_range=None,
                      compliance_current=0.1):
        """ Configures the instrument to apply a source voltage, and
        uses an auto range unless a voltage range is specified.
        The compliance current is also set.

        :param compliance_current: A float in the correct range for a
                                   :attr:`~.Keithley2400.compliance_current`
        :param voltage_range: A :attr:`~.Keithley2400.voltage_range` value or None
        """
        log.info("%s is sourcing voltage." % self.name)
        self.source_mode = 'voltage'
        if voltage_range is None:
            self.auto_range_source()
        else:
            self.source_voltage_range = voltage_range
        self.compliance_current = compliance_current
        self.check_errors()

    def beep(self, frequency, duration):
        """ Sounds a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")

    def triad(self, base_frequency, duration):
        """ Sounds a musical triad using the system beep.

        :param base_frequency: A frequency in Hz between 65 Hz and 1.3 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency * 5.0 / 4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency * 6.0 / 4.0, duration)

    display_enabled = Instrument.control(
        ":DISP:ENAB?", ":DISP:ENAB %d",
        """ A boolean property that controls whether or not the display of the
        sourcemeter is enabled. Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

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
            log.info("Keithley 2400 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2400 error retrieval.")

    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    def ramp_to_current(self, target_current, steps=30, pause=20e-3):
        """ Ramps to a target current from the set current value over
        a certain number of linear steps, each separated by a pause duration.

        :param target_current: A current in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps
        """
        currents = np.linspace(
            self.source_current,
            target_current,
            steps
        )
        for current in currents:
            self.source_current = current
            time.sleep(pause)

    def ramp_to_voltage(self, target_voltage, steps=30, pause=20e-3):
        """ Ramps to a target voltage from the set voltage value over
        a certain number of linear steps, each separated by a pause duration.

        :param target_voltage: A voltage in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps
        """
        voltages = np.linspace(
            self.source_voltage,
            target_voltage,
            steps
        )
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

    def trigger(self):
        """ Executes a bus trigger, which can be used when
        :meth:`~.trigger_on_bus` is configured.
        """
        return self.write("*TRG")

    def trigger_immediately(self):
        """ Configures measurements to be taken with the internal
        trigger at the maximum sampling rate.
        """
        self.write(":ARM:SOUR IMM;:TRIG:SOUR IMM;")

    def trigger_on_bus(self):
        """ Configures the trigger to detect events based on the bus
        trigger, which can be activated by :meth:`~.trigger`.
        """
        self.write(":ARM:COUN 1;:ARM:SOUR BUS;:TRIG:SOUR BUS;")

    def set_trigger_counts(self, arm, trigger):
        """ Sets the number of counts for both the sweeps (arm) and the
        points in those sweeps (trigger), where the total number of
        points can not exceed 2500
        """
        if arm * trigger > 2500 or arm * trigger < 0:
            print("this broken")
            #raise RangeException("Keithley 2400 has a combined maximum "
            #                     "of 2500 counts")
        if arm < trigger:
            self.write(":ARM:COUN %d;:TRIG:COUN %d" % (arm, trigger))
        else:
            self.write(":TRIG:COUN %d;:ARM:COUN %d" % (trigger, arm))

    def sample_continuously(self):
        """ Causes the instrument to continuously read samples
        and turns off any buffer or output triggering
        """
        self.disable_buffer()
        self.disable_output_trigger()
        self.trigger_immediately()

    def set_timed_arm(self, interval):
        """ Sets up the measurement to be taken with the internal
        trigger at a variable sampling rate defined by the interval
        in seconds between sampling points
        """
        if interval > 99999.99 or interval < 0.001:
            print("this broken")
        #    raise RangeException("Keithley 2400 can only be time"
        #                         " triggered between 1 mS and 1 Ms")
        self.write(":ARM:SOUR TIM;:ARM:TIM %.3f" % interval)

    def trigger_on_external(self, line=1):
        """ Configures the measurement trigger to be taken from a
        specific line of an external trigger

        :param line: A trigger line from 1 to 4
        """
        cmd = ":ARM:SOUR TLIN;:TRIG:SOUR TLIN;"
        cmd += ":ARM:ILIN %d;:TRIG:ILIN %d;" % (line, line)
        self.write(cmd)

    def output_trigger_on_external(self, line=1, after='DEL'):
        """ Configures the output trigger on the specified trigger link
        line number, with the option of supplying the part of the
        measurement after which the trigger should be generated
        (default to delay, which is right before the measurement)

        :param line: A trigger line from 1 to 4
        :param after: An event string that determines when to trigger
        """
        self.write(":TRIG:OUTP %s;:TRIG:OLIN %d;" % (after, line))

    def disable_output_trigger(self):
        """ Disables the output trigger for the Trigger layer
        """
        self.write(":TRIG:OUTP NONE")

    @property
    def mean_voltage(self):
        """ Returns the mean voltage from the buffer """
        return self.means[0]

    @property
    def max_voltage(self):
        """ Returns the maximum voltage from the buffer """
        return self.maximums[0]

    @property
    def min_voltage(self):
        """ Returns the minimum voltage from the buffer """
        return self.minimums[0]

    @property
    def std_voltage(self):
        """ Returns the voltage standard deviation from the buffer """
        return self.standard_devs[0]

    @property
    def mean_current(self):
        """ Returns the mean current from the buffer """
        return self.means[1]

    @property
    def max_current(self):
        """ Returns the maximum current from the buffer """
        return self.maximums[1]

    @property
    def min_current(self):
        """ Returns the minimum current from the buffer """
        return self.minimums[1]

    @property
    def std_current(self):
        """ Returns the current standard deviation from the buffer """
        return self.standard_devs[1]

    @property
    def mean_resistance(self):
        """ Returns the mean resistance from the buffer """
        return self.means[2]

    @property
    def max_resistance(self):
        """ Returns the maximum resistance from the buffer """
        return self.maximums[2]

    @property
    def min_resistance(self):
        """ Returns the minimum resistance from the buffer """
        return self.minimums[2]

    @property
    def std_resistance(self):
        """ Returns the resistance standard deviation from the buffer """
        return self.standard_devs[2]

    def status(self):
        return self.ask("status:queue?;")

    def RvsI(self, startI, stopI, stepI, compliance, delay=10.0e-3, backward=False):
        num = int(float(stopI - startI) / float(stepI)) + 1
        currRange = 1.2 * max(abs(stopI), abs(startI))
        # self.write(":SOUR:CURR 0.0")
        self.write(":SENS:VOLT:PROT %g" % compliance)
        self.write(":SOUR:DEL %g" % delay)
        self.write(":SOUR:CURR:RANG %g" % currRange)
        self.write(":SOUR:SWE:RANG FIX")
        self.write(":SOUR:CURR:MODE SWE")
        self.write(":SOUR:SWE:SPAC LIN")
        self.write(":SOUR:CURR:STAR %g" % startI)
        self.write(":SOUR:CURR:STOP %g" % stopI)
        self.write(":SOUR:CURR:STEP %g" % stepI)
        self.write(":TRIG:COUN %d" % num)
        if backward:
            currents = np.linspace(stopI, startI, num)
            self.write(":SOUR:SWE:DIR DOWN")
        else:
            currents = np.linspace(startI, stopI, num)
            self.write(":SOUR:SWE:DIR UP")
        self.connection.timeout = 30.0
        self.enable_source()
        data = self.values(":READ?")

        self.check_errors()
        return zip(currents, data)

    def RvsIaboutZero(self, minI, maxI, stepI, compliance, delay=10.0e-3):
        data = []
        data.extend(self.RvsI(minI, maxI, stepI, compliance=compliance, delay=delay))
        data.extend(self.RvsI(minI, maxI, stepI, compliance=compliance, delay=delay, backward=True))
        self.disable_source()
        data.extend(self.RvsI(-minI, -maxI, -stepI, compliance=compliance, delay=delay))
        data.extend(self.RvsI(-minI, -maxI, -stepI, compliance=compliance, delay=delay,
                              backward=True))
        self.disable_source()
        return data

    def use_rear_terminals(self):
        """ Enables the rear terminals for measurement, and
        disables the front terminals. """
        self.write(":ROUT:TERM REAR")

    def use_front_terminals(self):
        """ Enables the front terminals for measurement, and
        disables the rear terminals. """
        self.write(":ROUT:TERM FRON")

    def shutdown(self):
        """ Ensures that the current or voltage is turned to zero
        and disables the output. """
        log.info("Shutting down %s." % self.name)
        if self.source_mode == 'current':
            self.ramp_to_current(0.0)
        else:
            self.ramp_to_voltage(0.0)
        self.stop_buffer()
        self.disable_source()
        super().shutdown()

import numpy as np
import Keithley2400_with_4_probe as K24
import Keithley2700_with_7700 as K27
from tqdm import tqdm
from time import sleep

def prepare_2400(K2400, four_probe=True):

    '''
        Arguments:
            K2400: keithley object to prepare
            four_probe: activates four-probe measurement
    '''

    K2400.stop_buffer()
    K2400.disable_buffer()
    # Activates auto-zero, increasing measurement accuracy
    K2400.auto_zero = True
    # Activates four-probe measurements
    if four_probe:
        K2400.four_probe()
    # Displays information on the front terminal
    K2400.use_front_terminals()
    # Allows the 2400 to begin sourcing voltage
    K2400.enable_source()

def close_shutter(K2400, K2700):
    K2400.apply_voltage(compliance_current=0.5)
    K2700.open_all_channels()
    K2700.close_channels(7)
    K2400.source_voltage = 3.0
    sleep(0.5)
    K2400.source_voltage = 0.0

def open_shutter(K2400, K2700):
    K2400.apply_voltage(compliance_current=0.5)
    K2700.open_all_channels()
    K2700.close_channels(7)
    K2400.source_voltage = 3.0
    sleep(1.0)
    K2400.source_voltage = 0.0

def measure_current(
        K2400, K2700,
        n_buffer, devices,
        V_arr, four_probe):

    '''
        Arguments:
            K2400, K2700: keithley objects
            n_buffer, n_devices: number of buffers and devices
            V_arr: array of voltages to take measurements at
            four_probe: true to activate four-probe

        Returns:
            A 2d array of current readings with columns for each device
    '''

    I_out = np.zeros((len(V_arr), len(devices)))

    for col, dev in enumerate(devices):
        K2400.apply_voltage(compliance_current=0.5)
        # Closes a channel on the 2700 relevant to the selected device number
        K2700.open_all_channels()
        K2700.close_23()
        K2700.close_channels(int(dev+1))
        K2700.close_channels(int(dev+11))

        for row, v in enumerate(tqdm(V_arr)):
            K2400.config_buffer(n_buffer)
            K2400.source_voltage = v
            K2400.start_buffer()
            # Doesn't progress until the buffer is full, checking every 0.025 seconds
            K2400.wait_for_buffer(interval=0.025)
            I_out[row, col] = K2400.means[1]

    return I_out

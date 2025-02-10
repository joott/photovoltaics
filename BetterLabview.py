import numpy as np
import Keithley2400_with_4_probe as K24
import Keithley2700_with_7700 as K27
import matplotlib.pyplot as plt
from time import sleep
import random as rnd

# ========================
# Random "data" collection
# ========================

# Generates randomized floats from 0-1, in the same manner as the actual 
# function below. Useful when access to the Keithleys is limited. Not as
# heavily commented, will likely be removed on release
def random_data(GPIB2400,GPIB2700,buffer_num,device_list,V_min,V_max,V_step):
    
    # Correcting integer 'device_list' inputs into lists with one item
    #device_list = [int(device_list)]
    
    # Creating V_arr
    V_arr = np.arange(V_min,V_max+V_step,V_step)
    
    count = 0
    # Loop over the voltage range and write data to array
    for i in device_list:
        count += 1
        for j in V_arr:
            sleep(0.1)
            random_current = rnd.uniform(0,1)
            yield [count,j,random_current]


# ===============
# Data collection
# ===============

# Collects actual data from the Keithleys. Takes as inputs the GPIB connections,
# the number of measurements collected for each data point by the buffer, a list
# of devices (and thus channels) to iterate over, the voltage and sweep values
# needed to determine what voltage to source from the 2400.
def collect_data_current(GPIB2400,GPIB2700,buffer_num,device_list,V_min,V_max,V_step, current_arrays, voltage_arrays):

    # Correcting integer 'device_list' inputs into lists with one item
    #if type(device_list) != 'list':
    #    device_list = [int(device_list)]

    # Recreating V_arr based on the given inputs
    V_arr = np.arange(V_min,V_max+V_step,V_step)

    # Initializing Keithleys
    K2400 = K24.Keithley2400(GPIB2400)
    K2700 = K27.Keithley2700_with_7700(GPIB2700)
    # Deactivates and clears the buffer, which is not explicitly done during a reset
    K2400.stop_buffer()
    K2400.disable_buffer()
    # Activates auto-zero, increasing measurement accuracy
    K2400.auto_zero = True
    # Activates four-probe measurements
    K2400.four_probe()
    # Displays information on the front terminal
    K2400.use_front_terminals()
    # Allows the 2400 to begin sourcing voltage
    K2400.enable_source()

    # Loop over the voltage range and write data to array
    # Currently hardcoded pause, used to give the 2400 a moment to calibrate itself.
    # Without this, the first few data points tend to be meaningless. This should be
    # fixed before release
    #sleep(2.0)
    count=0
    for i in device_list:
        K2400.apply_voltage(compliance_current=0.5)
        # Closes a channel on the 2700 relevant to the selected device number
        K2700.open_all_channels()
        K2700.close_23()
        K2700.close_channels(i)
        K2700.close_channels(i+10)
        count = count+1
        for j in V_arr:
            # Configures the buffer to collect the specified number of points
            K2400.config_buffer(buffer_num)
            # Sets the output voltage to a specific entry in V_arr
            K2400.source_voltage = j
            # Activates the buffer
            K2400.start_buffer()
            # Doesn't progress until the buffer is full, checking every 0.025 seconds
            K2400.wait_for_buffer(interval=0.025)
            # outputs a list of the device number, the voltage, and the current
            #yield [count,K2400.means[0],K2400.means[1]]

            current_arrays[count-1].append(K2400.means[1])
            voltage_arrays[count-1].append(K2400.means[0])

    return current_arrays, voltage_arrays

    K2400.reset()
    K2700.reset()



#says voltage for all current values and vice versa
def collect_data_voltage(GPIB2400,GPIB2700,buffer_num,device_list,I_min,I_max,I_step, current_arrays, voltage_arrays):
    
    # Correcting integer 'device_list' inputs into lists with one item
    #if type(device_list) != 'list':
    #    device_list = [int(device_list)]
    
    # Recreating V_arr based on the given inputs
    I_arr = np.arange(I_min,I_max+I_step,I_step)
    
    # Initializing Keithleys
    K2400 = K24.Keithley2400(GPIB2400)
    K2700 = K27.Keithley2700_with_7700(GPIB2700)
    # Deactivates and clears the buffer, which is not explicitly done during a reset
    K2400.apply_current(compliance_voltage=2)
    K2400.measure_voltage()
    sleep(0.1)
    K2400.stop_buffer()
    K2400.disable_buffer()
    # Activates auto-zero, increasing measurement accuracy
    K2400.auto_zero = True
    # Activates four-probe measurements
    K2400.four_probe()
    # Displays information on the front terminal
    K2400.use_front_terminals()
    # Allows the 2400 to begin sourcing voltage
    K2400.enable_source()
    
    # Loop over the voltage range and write data to array
    # Currently hardcoded pause, used to give the 2400 a moment to calibrate itself.
    # Without this, the first few data points tend to be meaningless. This should be
    # fixed before release
    #sleep(2.0)
    count=0
    for i in device_list:
        # Closes a channel on the 2700 relevant to the selected device number
        K2700.open_all_channels()
        K2700.close_23()
        K2700.close_channels(i)
        K2700.close_channels(i+10)
        count = i
        for j in I_arr:
            # Configures the buffer to collect the specified number of points
            K2400.config_buffer(buffer_num)
            # Sets the output voltage to a specific entry in V_arr
            K2400.source_current = j
            # Activates the buffer
            K2400.start_buffer()
            # Doesn't progress until the buffer is full, checking every 0.025 seconds
            K2400.wait_for_buffer(interval=0.025)
            
            current_arrays[i-1].append(K2400.means[1])
            voltage_arrays[i-1].append(K2400.means[0])

    return current_arrays, voltage_arrays

    # Reset Keithleys    
    #K2400.beep(1000,0.25)
    K2400.reset()
    K2400.shutdown()
    #K2700.reset()






# Collects actual data from the Keithley 2400. Takes as inputs the GPIB connections,
# the number of measurements collected for each data point by the buffer, and the voltage and sweep values
# needed to determine what voltage to source from the 2400.
def collect_data_2400_current(GPIB2400,buffer_num,device_list,I_min,I_max,I_step):

    # Correcting integer 'device_list' inputs into lists with one item
    if type(device_list) != 'list':
        device_list = [int(device_list)]

    # Recreating V_arr based on the given inputs
    I_arr = np.arange(I_min,I_max+I_step,I_step)

    # Initializing Keithleys
    K2400 = K24.Keithley2400(GPIB2400)
    #K2700 = K27.Keithley2700_with_7700(GPIB2700)
    # Deactivates and clears the buffer, which is not explicitly done during a reset
    K2400.apply_current(compliance_voltage=2)
    K2400.measure_voltage()
    sleep(0.1)
    K2400.stop_buffer()
    K2400.disable_buffer()
    # Activates auto-zero, increasing measurement accuracy
    K2400.auto_zero = True
    # Activates four-probe measurements
    #K2400.four_probe()
    # Displays information on the front terminal
    K2400.use_front_terminals()
    # Allows the 2400 to begin sourcing voltage
    K2400.enable_source()

    # Loop over the current range and write data to array
    # Currently hardcoded pause, used to give the 2400 a moment to calibrate itself.
    # Without this, the first few data points tend to be meaningless. This should be
    # fixed before release
    #sleep(2.0)

    #For loop that goes through the current array and sources the values. Then measures the voltage.
    #Produces a list in the form of [voltage,current,resistance] for each current value.
    for j in I_arr:
        # Configures the buffer to collect the specified number of points
        K2400.config_buffer(buffer_num)
        # Sets the output voltage to a specific entry in V_arr
        K2400.source_current = j
        # Activates the buffer
        K2400.start_buffer()
        # Doesn't progress until the buffer is full, checking every 0.025 seconds
        K2400.wait_for_buffer(interval=0.025)
        # Multiply the output current by -1 if the substrate is inverted
        yield j,K2400.means[0]

    # Reset Keithleys    
    #K2400.beep(1000,0.25)
    K2400.reset()
    K2400.shutdown()
    #K2700.reset()


# Collects actual data from the Keithley 2400. Takes as inputs the GPIB connections,
# the number of measurements collected for each data point by the buffer, and the voltage and sweep values
# needed to determine what voltage to source from the 2400.
def collect_data_2400_voltage(GPIB2400,buffer_num,V_min,V_max,V_step,current_arrays,voltage_arrays):

    # Recreating V_arr based on the given inputs
    V_arr = np.arange(V_min,V_max+V_step,V_step)

    # Initializing Keithleys
    K2400 = K24.Keithley2400(GPIB2400)
    #K2700 = K27.Keithley2700_with_7700(GPIB2700)
    K2400.reset()
    # Deactivates and clears the buffer, which is not explicitly done during a reset
    K2400.stop_buffer()
    K2400.disable_buffer()
    # Activates auto-zero, increasing measurement accuracy
    K2400.auto_zero = True
    # Activates four-probe measurements
    #K2400.four_probe()
    # Displays information on the front terminal
    K2400.use_front_terminals()
    # Allows the 2400 to begin sourcing voltage
    K2400.enable_source()
    K2400.apply_voltage(compliance_current=1)

    #For loop that goes through the voltage array and sources the values. Then measures the current.
    #Produces a list in the form of [voltage,current,resistance] for each voltage value.
    for j in V_arr:
        # Configures the buffer to collect the specified number of points
        K2400.config_buffer(buffer_num)
        # Sets the output voltage to a specific entry in V_arr
        K2400.source_voltage = j
        # Activates the buffer
        K2400.start_buffer()
        # Doesn't progress until the buffer is full, checking every 0.025 seconds
        K2400.wait_for_buffer(interval=0.025)

        current_arrays.append(K2400.means[1])
        voltage_arrays.append(K2400.means[0])

    return current_arrays, voltage_arrays


    K2400.reset()
    K2400.shutdown()

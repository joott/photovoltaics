import BetterLabview as bl
import matplotlib.pyplot as plt
import datetime as dt
import Keithley2400_with_4_probe as K24
import Keithley2700_with_7700 as K27
import numpy as np
import sys
import Large_Area_Analysis as LAA


#Set the keithely addresses
GPIB2400 = 'GPIB::24'
GPIB2700 = 'GPIB::17'

#establish the keithleys in object
K2400 = K24.Keithley2400(GPIB2400)

#reset the keithelys before each run
K2400.reset()

# Specify the f1le name
file_name = 'd-12'
substrate_num = '4_72h'
file_path = f'./data/250110_encap/{substrate_num}/{file_name}'

#establish measurement parameters
v_min = -1
v_max = 7
v_step = 0.2
buffer_num = 5
active_area = 6.4 #in cm^2

device_list = [1,2,3]
number_of_devices = len(device_list)

#create empty arrays
current_arrays = [[] for _ in range(number_of_devices)]
voltage_arrays = [[] for _ in range(number_of_devices)]
device_list = [3]

#function that interacts with keithly
current_arrays, voltage_arrays = list(bl.collect_data_current(GPIB2400, GPIB2700, buffer_num, device_list, v_min,v_max,v_step,current_arrays,voltage_arrays))

K2400.reset()

#Plot the data
plt.plot(voltage_arrays[0],current_arrays[0])
plt.show()

#Try to call on Large_Area_Analysis to analyze data
try:
    device_data = LAA.total_data(voltage_arrays[0], current_arrays[0], voltage_arrays[0], current_arrays[0], device_list[0], active_area, substrate_num)
except Exception as e:
    print(f"Error at index {substrate_num}: {e}")

#Export data to files
combined_data = zip(voltage_arrays[0], current_arrays[0])

# Open the file for writing
with open(file_path, 'w') as file:
    # Write column headers if needed
    #file.write("Column1, Column2\n")

    # Write data to the file
    for row in combined_data:
        file.write(f"{row[0]}\t{row[1]}\n")

print(f"Data has been exported to {file_path}")


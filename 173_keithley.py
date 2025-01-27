import BetterLabview as bl
import matplotlib.pyplot as plt
import datetime as dt
import Keithley2400_with_4_probe as K24
import Keithley2700_with_7700 as K27
import numpy as np
import sys
import Large_Area_Analysis as LAA


#Establish GPIB connectoins
GPIB2400 = 'GPIB::24'
GPIB2700 = 'GPIB::17'

#establish the keithleys in object
K2400 = K24.Keithley2400(GPIB2400)
K2700 = K27.Keithley2700_with_7700(GPIB2700)

#reset the keithleys before each run
K2400.reset()
K2700.reset()

batch_path = 'C:/Users/DawsonBoone/Desktop/173 Tester/Data/test/1'

#establish measurement parameters
substrate_num = 1
v_min = -1
v_max = 1
v_step = .05
buffer_num = 5
active_area = .076
device_list = [1,2]
number_of_devices = len(device_list)

#create empty arrays
current_arrays = [[] for _ in range(number_of_devices)]
voltage_arrays = [[] for _ in range(number_of_devices)]

#function that interacts with keithley
current_arrays, voltage_arrays = list(bl.collect_data_current(GPIB2400, GPIB2700, buffer_num, device_list, v_min,v_max,v_step,current_arrays,voltage_arrays))

K2400.reset()

#create figures and axes
fig, axs = plt.subplots(nrows=1, ncols=len(voltage_arrays), figsize=(15, 5))

if number_of_devices == 1:
    axs = [axs]

# Loop through the lists simultaneously and plot in subplots
for i, (x, y) in enumerate(zip(voltage_arrays, current_arrays)):
    axs[i].plot(x, y)
    axs[i].set_xlabel('Voltage')
    axs[i].set_ylabel('Current(mA)')
    axs[i].set_title(f'Plot {i+1}')

plt.tight_layout()
plt.show()


for i in range(len(device_list)):
#define files name
    file_name = f'l-{device_list[i]}'
    file_path = f'{batch_path}/{substrate_num}/{file_name}'

    try:
        device_data = LAA.total_data(voltage_arrays[i], current_arrays[i], voltage_arrays[i], current_arrays[i], device_list[i], active_area, substrate_num)
        solar_df = solar_df._append({'substrate_num': device_data[0], 'Device Number': device_data[1], 'V_OC': device_data[2], 'J_SC': device_data[3], 'FF': device_data[4], 'Eff': device_data[5], 'R_series': device_data[6], 'R_shunt': device_data[7], 'Total Area': device_data[8]}, ignore_index=True)
    except Exception as e:
        print(f"Error at index {i}: {e}")
        continue

    #Export data to files
    combined_data = zip(voltage_arrays[i], current_arrays[i])
    # Open the file for writing
    with open(file_path, 'w') as file:
    # Write column headers if needed
    #file.write("Column1, Column2\n")

    # Write data to the file
        for row in combined_data:
            file.write(f"{row[0]}\t{row[1]}\n")

    print(f"Data has been exported to {file_path}")

#solar_df.to_excel(excel_file_path, index=False)  # Set index=False to exclude the index column

import argparse
import measurement as measure
import os
import pathlib
import numpy as np
import Keithley2400_with_4_probe as K24
import Keithley2700_with_7700 as K27

parser = argparse.ArgumentParser(prog="OPV measurement tool")

parser.add_argument('filename', type=pathlib.Path)
parser.add_argument('-s', '--step', default=0.04, type=float,
                    help="Voltage step size between measurements.")
parser.add_argument('-m', '--min', default=-1.0, type=float,
                    help="Minimum voltage in sweep.")
parser.add_argument('-M', '--max', default=1.0, type=float,
                    help="Maximum voltage in sweep.")
parser.add_argument('-b', '--buffer', default=5, type=int)
parser.add_argument('-d', '--devices', default=4, type=int,
                    help="Number of devices.")
parser.add_argument('-f', '--four', action='store_true',
                    help="Runs measurement as four-probe.")

args = parser.parse_args()

GPIB2400 = 'GPIB::17'
GPIB2700 = 'GPIB::3'
K2400 = K24.Keithley2400(GPIB2400)
K2700 = K27.Keithley2700_with_7700(GPIB2700)

V_arr = np.arange(args.min, args.max+args.step, args.step)
data = measure.measure_current(K2400, K2700, args.buffer, args.devices, V_arr, args.four)

parent_directory = args.filename.parents[0]
if not os.path.exists(parent_directory):
    os.makedirs(parent_directory)

with open(args.filename, 'w') as file:
    for i, v in enumerate(V_arr):
        file.write(f"{v}")
        for j in range(args.devices):
            file.write(f"\t{data[i,j]}")
        file.write(f"\n")

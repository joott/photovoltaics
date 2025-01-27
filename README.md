These files are used to first collect data using a python library called
Pymeasure that was built on the C library PYVISA. Pymeasure is more user
friendly and can offer some cool features if you are curious. The libraries
that I used are a bit hazy (I wrote this over a year and a half ago)... but I
did my best:

- NumPy
    - basic library for maths in python
- PyMeasure
    - This will do most of the heavy lifting
- Scipy
    - Honestly I dont remember what I pulled... but I do use it
- Pandas
    - Data Management
- Matplotlib
    - For generating plots
- openpyxl
    - ...
- sqlite3
    - I was using this library to upload data to a database directly from analysis. A simple tutorial can explain it on youtube. SQL is great and lightweight.

Keithly2400_with_4_probe and Keithly2700_with_7700 are modified scripts from
the Pymeasure library to accommodate our setup. In the 2400 file I called on
PYVISA to send a string to the keithly 2400 to activate 4 probe measurements (I
recommend reading into 4-probe measurements, they are not only interesting but
useful!).In the keithly 2700 file we modified it to accommodate our specific
multiplexer, the 7700 in the back. Both should be plug and play but are worth
understanding.

You will do your measurements with 173_keithly and
run_collect_Data_2400_voltage. These call on the functions within the other
scripts and are where knobs are turned.

BetterLabview is the meat of the code. This file is separated into multiple
functions that can be called on to conduct a measurement. We can collect
voltage, current, and even resistance. Some are for 4 probe others for 2 probe.
It is quite disorganized, but not bad enough to be unfollowable.

To bring it all together, you will work within the 173_keithley and
run_collect_data_2400_voltage which call on betterlabview which will call on
pymeasure and our modified scripts. 173_keithley is designed for multiplexing,
(varying channels in the back of the Keithley 2700) while
run_collect_data_2400_voltage is designed to work on a single channel. I
recommend writing your own script, similar to 173_keithley, if you can find the
time to make sure that it is perfectly tuned to your needs!


email me at dboone2@ncsu.edu if help is needed!


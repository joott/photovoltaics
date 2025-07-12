Code used for measuring IV curves of organic photovoltaics. Run the aptly-named
`run.py` with appropriate arguments to perform a measurement. A breakdown of
the available options (step size, data output location, etc.) can be seen with
`python run.py --help`. For example, to run a four-probe measurement from -1.0
V to 1.0 V with a step size of 0.1 V with 5 buffers and only measure from
devices 0 and 1, you could run
```
python run.py --four -s 0.1 -m -1.0 -M 1.0 -b 5 -e 2 3 [output location].dat
```
The output file is formatted as a plaintext table with three columns for
voltage and light/dark currents respectively. The two parameters which can not
currently be set with an argument are the addresses used for the Keithleys.
These are set in `run.py` (I have the two sets of addresses we used in the
file).

`Keithley2400_with_4_probe.py` and `Keithley2700_with_7700.py` are modified
scripts from PyMeasure with functionality added to suit this specific use case.

Feel free to add fun jingles to `jingle.py`!

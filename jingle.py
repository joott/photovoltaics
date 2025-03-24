import Keithley2400_with_4_probe as K24
from time import sleep
from random import random
import numpy as np

bpm = 170
dt = 60 / (bpm * 4)
A4 = 440

b6_b7_1 = np.array([0,4,7,2,6,9,4,8,11,16]) + 3
lydian_fanfare = np.array([0,2,4,7,0,2,6,7,11,12]) - 2

jingles = [b6_b7_1, lydian_fanfare]

def success_jingle(K24):
    idx = int(np.floor(random() * len(jingles)))
    play_jingle(K24, jingles[idx])

def freq(steps):
    return A4 * 2**(steps/12)

def play_jingle(K24, notes):
    for note in notes:
        K24.beep(freq(note), dt)
        sleep(dt)

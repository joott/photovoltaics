import numpy as np
import scipy.interpolate as itp
import scipy.optimize as opt
from scipy.misc import derivative
import os
import pandas as pd
import matplotlib.pyplot as plt
from findiff import FinDiff
import openpyxl
import sqlite3

#This script is not optimal... maybe you could improve it?

def find_closest_number(target, array):
    closest_number = None
    min_difference = float('inf')

    for num in array:
        difference = abs(num - target)
        if difference < min_difference:
            min_difference = difference
            closest_number = num

    return closest_number

#Function that characterizes the data
def total_data(V_arr, I_arr, V_arr_d, I_arr_d, i, area, substrate_num):

    subcell = i

    #Artifact of old code, could still be useful
    if i >= 10:
        Constant = area #cm^2
    else:
        Constant = area
    #define the input power - P_in = area * Solar_P/1 m^2
    P_in = (100/1000)*(Constant)


    #Interpolate the IV data
    IV_func = itp.interp1d(V_arr, I_arr)
    #Inverse of Interpolation
    IV_func_inv = itp.interp1d(I_arr, V_arr)

    #V_oc is when I=0
    V_OC = IV_func_inv(0)
    #I think this makes value float...? Did this a while ago.
    V_OC = V_OC*1
    #reducing sigfigs
    V_OC = np.round(V_OC,3)


    #I_sc is where V=0
    I_SC = abs(IV_func(0))
    #Generate J_sc.. Current per unit area, in this case milimeters
    J_SC = I_SC*1000/Constant
    #round to two sig figs
    J_SC = np.round(J_SC, 2)

    #Generate power array and then interpolate
    P_arr = []
    for i in range(len(V_arr)):
        P_Li = V_arr[i]*IV_func(V_arr[i])
        P_arr.append(P_Li)
    P_func = itp.interp1d(V_arr, P_arr)

    #Finding the max power point.
    power_test_arr = []
    for i in range(len(V_arr)):
        power_test_arr.append(P_func(V_arr[i]))
    V_MP_guess = V_arr[np.argmin(power_test_arr)]

    if V_MP_guess <= V_arr[0] or V_MP_guess >= V_arr[-1]:
        V_MP = 0
    else:
        V_MP = opt.fmin(P_func,V_MP_guess)[0]
    P_MP = abs(P_func(V_MP))

    if V_MP == 0:
        I_MP = 0
        FF = 0
        Eff = 0
    else:
        #Calculate the FF using MPP and then find eff.
        I_MP = P_MP/V_MP #(V*mA)/V
        FF = abs(P_MP/(V_OC*I_SC))*100 #(V*mA)/(V*mA)
        FF = np.round(FF, 2)
        Eff = P_MP/P_in #((V*mA)*1000)/(V*A)
        Eff = np.round(Eff, 4)

    values = [FF, V_OC, I_SC, J_SC, Eff]


    print(f'the Fill Factor is: {FF}')
    print(f'the V_oc is: {V_OC}')
    print(f'the I_SC is: {I_SC}')
    print(f'the J_sc is: {J_SC}')
    print(f'the efficiency is: {Eff*100}')



#Dark Data
#Same as with light but dark... but not used
    IV_func_d = itp.interp1d(V_arr_d, I_arr_d)
    IV_func_inv_d = itp.interp1d(I_arr_d, V_arr_d)

    V_OC_d = IV_func_inv_d(0)
    
    I_SC_d = abs(IV_func_d(0))
    J_SC_d = I_SC_d*1000/Constant


#determine both series and shunt resistance. This code is very messy and may not be correct. I take the slope at V_oc and J_sc. Ideally this is taken on a dark curve, however it can still give insights
#on light data. There is definitly a better way to do this... a much better way.
    x_1 = np.linspace(min(V_arr_d),0,500)
    x_2 = np.linspace(.001,max(V_arr_d),500)
    x = np.concatenate((x_1, x_2), axis=0)
    kinda_V_OC_d = find_closest_number(V_OC_d, x)
    index_V_OC_d = np.where(x == kinda_V_OC_d)
    kinda_V_SC_d = find_closest_number(0, x)
    index_V_SC_d = np.where(x == kinda_V_SC_d)
    dx = x[1]-x[0]
    f = IV_func_d(x)
    dx_1 = FinDiff(0, dx, 1)
    IV_derivative = dx_1(f)
    R_s_i_2 = 1/IV_derivative[index_V_OC_d]*Constant
    R_shunt_i_2 = 1/IV_derivative[index_V_SC_d]*Constant
    R_s_i_2 = R_s_i_2[0].astype(np.float64)
    R_s_i_2 = np.round(R_s_i_2, 2)
    R_shunt_i_2 = R_shunt_i_2[0].astype(np.float64)
    R_shunt_i_2 = np.round(R_shunt_i_2, 2)

    print(f'the interpolated series resistance is: {R_s_i_2}')
    print(f'the interpolated shunt resistance is: {R_shunt_i_2}')

#Store needed values in array
    array = [f"{substrate_num}", subcell, V_OC, J_SC, FF, Eff*100, R_s_i_2, R_shunt_i_2, area]
    
    return array


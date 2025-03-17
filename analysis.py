''' 
    the new and improved version of Large Area Analysis, 
    updated to include some data processing functions, etc. 

    LAST UPDATE. 17 Mar 2025, Logan White
'''

# loading in libraries
import numpy as np
import scipy.interpolate as itp
import scipy.optimize as opt
from findiff import FinDiff # this needs to be trashed with updated gradient, etc.

def characterize( data, device, verbose = False, area = (7.6)/100 , substrateID = 0):

    '''
        Calculates the 'traditional' metrics for OPV characterization for a specific device. 
        Has the option to print output or just return an array of data (i.e. verbose).

        Args.
            - data: opv measurements under 1 sun intensity.
            - device: device on the substrate
            - verbose: prints output if desired, set to True
            - area: estimated area of the device
            - substrateID: use if characterizing multiple substrates, etc.

        Returns.  
            - fill factor (ff)
            - V_oc
            - short circuit current (I_sc)
            - short circuit current density (J_sc)
            - efficiency (eff) 

            [ff, V_oc, I_sc, J_sc, eff]

    '''


    V = data[:, 0]
    I = data[:, device]

    #define the input power - P_in = area * Solar_P/1 m^2
    P_in = (100/1000) * area

    #Interpolate the IV data
    IV_func = itp.interp1d(V, I)
    #Inverse of Interpolation
    IV_func_inv = itp.interp1d(I, V)

    #V_oc is when I=0
    V_OC = IV_func_inv(0)
    V_OC = np.round(V_OC, 3)


    #I_sc is where V=0
    I_SC = abs(IV_func(0))
    #Generate J_sc.. Current per unit area, in this case milimeters
    J_SC = I_SC * 1000 / area
    J_SC = np.round(J_SC, 3)

    #Generate power array and then interpolate
    P = np.zeros( V.size )
    for i, v in enumerate(V):
        P[i] = v * IV_func(v)

    P_func = itp.interp1d(V, P)

    #Finding the max power point.
    P_test = np.zeros(V.size)
    for i, v in enumerate(V):
        P_test[i] = P_func(v)

    V_MP_guess = V[np.argmin(P_test)]

    if V_MP_guess <= V[0] or V_MP_guess >= V[-1]:
        V_MP = 0
    else:
        V_MP = opt.fmin(P_func,V_MP_guess)[0]

    P_MP = abs(P_func(V_MP))

    if V_MP == 0:
        I_MP = 0
        FF = 0
        eff = 0
    else:
        #Calculate the FF using MPP and then find eff.
        I_MP = P_MP/V_MP #(V*mA)/V
        FF = abs(P_MP/(V_OC*I_SC))*100 #(V*mA)/(V*mA)
        FF = np.round(FF, 3)
        eff = P_MP/P_in #((V*mA)*1000)/(V*A)
        eff = np.round(eff, 3)

    if verbose:
        print(f'the Fill Factor is: {FF}')
        print(f'the V_oc is: {V_OC}')
        print(f'the I_sc is: {I_SC}')
        print(f'the J_sc is: {J_SC}')
        print(f'the efficiency is: {eff*100}')

    return np.asarray([device, FF, V_OC, I_SC, J_SC, eff])


def resistances(data, device, verbose=False, area = (7.6)/100 , substrateID = 0):

    '''
            Calculates shunt and series resistance for a specific device. 
            Has the option to print output or just return an array of data (i.e. verbose).

            Args.
                - data: opv measurements, dark data (0 sun intensity)
                - device: device on the substrate
                - verbose: prints output if desired, set to True
                - area: estimated area of the device
                - substrateID: use if characterizing multiple substrates, etc.

            Returns.  
                - fill factor (ff)
                - V_oc
                - short circuit current (I_sc)
                - short circuit current density (J_sc)
                - efficiency (eff) 

                [ff, V_oc, I_sc, J_sc, eff]

        '''
    
    Vd = data[: 0]
    Id = data[:, device]

    # error message for data processing, checks that voltage is high enough
    if Vd[-1] < 1.8:
        print("ERROR. voltage not high enough to measure resistances (V < 1.8).")
        return

    IV_func_d = itp.interp1d(Vd, Id)
    IV_func_inv_d = itp.interp1d(Id, Vd)

    V_OC_d = IV_func_inv_d(0)
    
    I_SC_d = abs(IV_func_d(0))
    J_SC_d = I_SC_d * 1000 / area

    '''
    could use light data OR take dark data further than 1V (e.g. -1 to 2V)
    to measure series resistance, should be on oom of ~1 ohms
    '''

    # TODO: remove interpolation (e.g. derivative), use scipy/numpy for simpler analysis.

    x = np.linspace(Vd[0], Vd[-1], 2001)

    index_V_OC_d = (np.absolute(x - V_OC_d)).argmin()
    index_V_SC_d = (np.absolute(x)).argmin()

    dx = x[1]-x[0]
    f = IV_func_d(x)
    dx_1 = FinDiff(0, dx, 1)
    IV_derivative = dx_1(f)

    R_series_i_2 = 1/IV_derivative[index_V_OC_d] * area
    R_shunt_i_2 = 1/IV_derivative[index_V_SC_d] * area

    if verbose:
        print(f'series resistance: {R_series_i_2}')
        print(f'shunt resistance: {R_shunt_i_2}')
    
    return np.asarray([R_series_i_2, R_shunt_i_2])
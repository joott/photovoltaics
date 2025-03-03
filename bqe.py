import numpy as np

def J_ph(data_light, data_dark, area = (7.6)/100):

    '''
        Arguments:
            data_light: 2d array, voltage and current
            data_dark: 2d array, voltage and dark current
            area: duh

        Returns:
            A 2d array with voltage and surface current, i.e. [V, J - J_dark]
    '''

    I = data_light[:, 1]
    Id = data_dark[:, 1]

    J = I * 1000 / area
    Jd = Id * 1000 / area

    return np.stack((data_light[:, 0], (J - Jd))).T

def J_sat(data_light, data_dark, area = (7.6)/100):

    '''
        Arguments:
            data_light: 2d array, voltage and current
            data_dark: 2d array, voltage and dark current
            area: duh

        Returns:
            J_ph at the most negative voltage (-1V) in raw data.
    '''
        
    return J_ph(data_light, data_dark, area)[0, 1]

def V_off(data_light, data_dark, area = (7.6)/100):

    '''
        Arguments:
            data_light: 2d array, voltage and current
            data_dark: 2d array, voltage and dark current
            area: duh

        Returns:
            The voltage where J_ph is closest to 0.
    '''
        
    V = data_light[:, 0]
    Jph = J_ph(data_light, data_dark, area)[:, 1]
    min_idx = (np.abs(Jph)).argmin()
    return float(V[min_idx])

def BQE(data_light, data_dark, area = (7.6/100)):

    '''
        Arguments:
            data_light: 2d array, voltage and current
            data_dark: 2d array, voltage and dark current
            area: duh

        Returns:
            A 2d array with V_bulk (V_off - V) and bulk quantum efficiency (J_ph / J_sat)
    '''

    V_bulk = V_off(data_light, data_dark, area) - data_light[:, 0] # V_off - V
    jph = J_ph(data_light, data_dark, area)
    jsat = J_sat(data_light, data_dark, area)

    return np.stack((V_bulk, jph[:, 1]/jsat)).T
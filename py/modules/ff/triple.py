import numpy as np
from modules.ff import calc_ff

def compute(signal, echo_times, *args):
    '''
    this function calculates the fat fraction according to corrected Dixon's method, which considers a single T2* effect.
    parameters: voxelSignal -> array, float >0, signal intensities, at least two values.
    returns:    fat_fraction -> float
    '''
    s1 = signal[0]
    s2 = signal[1]
    s4 = signal[3]
    deltaTE = echo_times[1] - echo_times[0]
    t2star = deltaTE / np.log(s2 / s4)

    rho_water = (s2 * np.exp(echo_times[1] / t2star) + s1 * np.exp(echo_times[0] / t2star)) / 2
    rho_fat = (s2 * np.exp(echo_times[1] / t2star) - s1 * np.exp(echo_times[0] / t2star)) / 2

    return calc_ff.compute(rho_fat, rho_water)

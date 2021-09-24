from modules.ff import calc_ff

def compute(signal, *args):
    '''
    this function calculates the fat fraction according to Dixon's method.
    parameters: voxelSignal -> array, float >0, signal intensities, at least two values.
    returns:    fat_fraction -> float
    '''
    s1 = signal[0]
    s2 = signal[1]
    rho_water = float(s2 + s1)/2.0;
    rho_fat = float(s2 - s1)/2.0;

    return calc_ff.compute(rho_fat, rho_water)

import numpy as np
from scipy.optimize import curve_fit
from modules.ff import calc_ff

def fit_multiinterf(echo_times, rho_fat, rho_water, t2star, imaging_frequency):
    '''
    This function fits the GRE IP-OP signal from human liver, for any number of TEs,
    considering a low flip angle (Taylor approx. around zero) and 3T.
    It is based on studies by Hamilton (T2* and characteristic ppm frequency values).
    parameters: echo times -> array with TEs
                rho_fat    -> float >0, fat proton density
                rho_water  -> float >0, water proton density
    returns:    Sabs -> float > 0, absolute signal intensity in arbitrary units (equivalent to ydata)
    '''

    echo_times = np.array(echo_times)
    rho_fat = np.array(rho_fat)
    rho_water = np.array(rho_water)
    t2star = np.array(t2star)

    # cn is the fractional proton density of each fat moiety (Yokoo) (see freq_ppm)
    cn = np.array([0.12, 0.7, 0.088])

    # frequency in parts per million for each fat moiety
    ppm_fat = np.array([2.1, 1.3, 0.9])
    ppm_water = np.array(4.7)

    hydroGyro = np.array(42.577e6)  # Hydrogen gyromagnetic ratio, Hz/T
    #freq_water = np.array(ppm_water * magField * hydroGyro / 1e6)  # water frequency in Megahertz
    freq_water = np.array(ppm_water * imaging_frequency)  # water frequency in Hertz

    # relative frequency for each fat to that of water
    freqr_fat = np.zeros(len(ppm_fat))
    for n, fppm in enumerate(ppm_fat):
        #freqr_fat[n] = freq_water - (fppm * magField * hydroGyro / 1e6)
        freqr_fat[n] = freq_water - (fppm * imaging_frequency)

    # calculate the signal for each moiety
    S = (len(freqr_fat), len(echo_times))
    S = np.zeros(S, dtype='complex')
    # three fat signals
    for n, moieties in enumerate(freqr_fat):
        for t, TE in enumerate(echo_times):
            S[n, t] = cn[n] * np.exp(2.0 * np.pi * 1j * freqr_fat[n] * TE)

    Ssum = len(echo_times)
    Ssum = np.zeros(Ssum)
    Ssum = np.sum(S, axis=0)  # sum of fat signals
    Sabs = np.absolute(rho_water + rho_fat * Ssum)  # multiply rho_fat and add rho_water, take absolute value
    Sfinal = len(echo_times)
    Sfinal = np.zeros(Sfinal)
    for t, TE in enumerate(echo_times):
        Sfinal[t] = Sabs[t] * np.exp(-TE / t2star)  # exponential decay

    return Sfinal

def compute(signal, echo_times, imaging_frequency):

    bd = (0, [np.inf,np.inf,1])
    #fitted_par, pcov = curve_fit(fit_multiinterf, echo_times, signal, bounds=bd)
    fitted_par, pcov = curve_fit(lambda echo_times, rho_fat, rho_water, t2star:
                                 fit_multiinterf(echo_times, rho_fat, rho_water, t2star, imaging_frequency),
                                 echo_times, signal, bounds=bd, ftol=0.0005, xtol=0.0005)
    rho_fat = fitted_par[0]
    rho_water = fitted_par[1]

    # import matplotlib.pyplot as plt
    # plt.plot(np.linspace(echo_times[0], echo_times[6]),
    #          fit_multiinterf(np.linspace(echo_times[0], echo_times[6]),
    #                          *fitted_par, imaging_frequency=imaging_frequency))
    # plt.plot(echo_times, signal, '*')
    # plt.show()

    return calc_ff.compute(rho_fat, rho_water)
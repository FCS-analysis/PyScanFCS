import numpy as np
from scipy import optimize as spopt


def fit_exp(times, trace):
    """Fit an exponential function to the given trace.


    Parameters
    ----------
    times : ndarray of length N
        x-values

    trace : ndarray of length N
        y-values


    Returns
    -------
        parameters, function
    """
    # Set starting parameters for exponential fit
    def expfunc(p, x): return p[0] * np.exp(-x / p[1])
    # parms = [ampl, decaytime]
    parms = np.zeros(2, dtype=np.float32)
    ltr = len(trace)
    border = np.int(np.ceil(ltr / 50.))
    parms[0] = 1. * trace[:border].mean()
    parms[1] = times[-1] / np.log(parms[0])
    # Fit function is an exponential
    # Function to minimize via least squares
    # f_min = lambda p, x: expfunc(np.abs(p), x) - trace

    def f_min(p, x):
        p = np.abs(p)
        return expfunc(np.abs(p), x) - trace
    # Least squares
    popt, chi = spopt.leastsq(f_min, parms[:], args=(times))
    return np.abs(popt), expfunc


def fit_gauss(amplitudes, frequencies,  argmax):
    # Set starting parameters for gaussian fit
    # parms = [freq, ampl, sigma]
    parms = np.zeros(3, dtype=np.float32)
    parms[0] = frequencies[argmax]
    parms[1] = amplitudes[argmax]
    parms[2] = abs(frequencies[1] - frequencies[2]) * 2
    # Fit function is a gaussian

    def gauss(p, x):
        expnt = np.exp(-((x - p[0]) / p[2]) ** 2 / 2)
        norm = p[1] / (p[2] * np.sqrt(2 * np.pi))
        return expnt * norm

    # Function to minimize via least squares
    def f_min(p, x):
        return gauss(p, x) - amplitudes
    # Least squares
    popt, chi = spopt.leastsq(f_min, parms[:], args=(frequencies))
    return np.abs(popt), gauss

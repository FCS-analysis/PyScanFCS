import numpy as np


def reduce_trace(trace, deltat, length):
    """Shorten an array by averaging.

    Given a `trace` of length `len(trace)`, compute a trace of
    length smaller than `length` by averaging.


    Parameters
    ----------
    trace : ndarray, shape (N)
        Input trace that is to be averaged.
    deltat : float
        Time difference between bins in trace.
    length : int
        Maximum length of the new trace.


    Returns
    -------
    newtrace : ndarray, shape (N,2)
        New trace (axis 1) with timepoints (axis 0).

    """
    step = 0
    while len(trace) > length:
        N = len(trace)
        if N % 2 != 0:
            N -= 1
        trace = (trace[0:N:2] + trace[1:N:2]) / 2
        step += 1
    # Return 2d array with times
    T = np.zeros((len(trace), 2))
    T[:, 1] = trace / deltat / 1e3  # in kHz
    T[:, 0] = np.arange(len(trace)) * deltat * 2**step
    return T

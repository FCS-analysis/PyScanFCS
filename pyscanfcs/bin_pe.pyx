import tempfile
import warnings

import numpy as np

# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# currently part of the Cython distribution).
cimport numpy as np
# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPEuint32 = np.uint32
DTYPEuint16 = np.uint16
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.uint32_t DTYPEuint32_t
ctypedef np.uint16_t DTYPEuint16_t

cimport cython

# Negative indices are checked for and handled correctly. The code is
# explicitly coded so that it doesn’t use negative indices, and it (hopefully)
# always access within bounds. We can add a decorator to disable bounds
# checking:
@cython.cdivision(True)
@cython.boundscheck(False)  # turn of bounds-checking for entire function
def bin_photon_events(np.ndarray[DTYPEuint32_t] data, double t_bin,
                      binshift=None, outfile=None, outdtype=DTYPEuint16,
                      callback=None, cb_kwargs={}):
    """Convert photon arrival times to a binned trace

    Bin all photon arrival times in a numpy.uint32 array *data*, using
    the binning time float *t_bin* and saving the intensity trace as
    the file *filename*. *dlg* is a python object that supports
    dlg.Update, like a progress dialog.

    Parameters
    ----------
    data : ndarray (uint32)
        photon events to be binned
    t_bin : (double)
        binning time
    binshift : int
        adding a number of zeros at the beginning of the binned data
    outfile : str
        path to store output
    outdtype : dtype
        numpy dtype of the output file
    callback : callable or None
        Callback function to be called throughout the algorithm. If the
        return value of `callback` is not None, the function will abort.
        Number of function calls: 100
    cb_kwargs : dict, optional
        Keyword arguments for `callback` (e.g. "pid" of process).

    Returns
    -------
    filename : str
        The filename of the binned data.

    Notes
    -----
    The photon stream `data` is created by a program called `Photon.exe`
    from correlator.com.
    """
    cdef int N = len(data)
    BinData = []
    cdef double time_c = 0  # time counter
    cdef int phot_c = 0  # photon counter
    cdef int maxphot = 0
    cdef int j, i, emptybins, bin

    dtype = np.dtype(outdtype)

    if outfile is None:
        outfile = tempfile.mktemp(suffix=".bin")

    # print("Creating file {} ({})".format(outfile, outdtype.__name__))

    NewFile = open(outfile, 'wb')

    # Add number of empty bins to beginning of file
    if binshift is not None:
        NewFile.write(outdtype(np.zeros(binshift)))

    TempTrace = []

    Nperc = int(np.floor(N / 100))

    for j in range(100):
        percent = str(j)

        for i in range(Nperc):
            i = i + Nperc * j
            time_c += data[i]

            if time_c >= t_bin:
                # Append counted photons and
                # reset counters
                # NewFile.write(outdtype(phot_c))
                TempTrace.append(phot_c)
                time_c -= t_bin
                phot_c = 0
                # Empty bins between this and next event:
                emptybins = int(time_c / t_bin)
                TempTrace += emptybins * [0]
                time_c -= emptybins * t_bin
                # Equivalent to:
                # time_c = int(time_c)%int(t_bin)
            phot_c += 1
        NewFile.write(outdtype(TempTrace))
        TempTrace = []

        if callback is not None:
            ret = callback(**cb_kwargs)
            if ret is not None:
                warnings.warn("Aborted by user.")
                return outfile

    # Now write the rest:
    for i in range(Nperc * 100, N):
        time_c += data[i]
        if time_c >= t_bin:
            # Append counted photons and
            # reset counters
            # NewFile.write(outdtype(phot_c))
            TempTrace.append(phot_c)
            time_c -= t_bin
            phot_c = 0
            # Empty bins between this and next event:
            emptybins = int(time_c / t_bin)
            TempTrace += emptybins * [0]
            time_c -= emptybins * t_bin
            # Equivalent to:
            # time_c = int(time_c)%int(t_bin)
        phot_c += 1
    # final photons
    TempTrace.append(phot_c)
    
    NewFile.write(outdtype(TempTrace))
    NewFile.close()
    return outfile

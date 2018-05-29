import tempfile
import warnings

import numpy as np

# See cython documentation for following stuff
# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# currently part of the Cython distribution).
cimport numpy as np
# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPEuint32 = np.uint32
DTYPEuint16 = np.uint16
DTYPEfloat32 = np.float32
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.uint32_t DTYPEuint32_t
ctypedef np.uint16_t DTYPEuint16_t
ctypedef np.float32_t DTYPEfloat32_t

# Negative indices are checked for and handled correctly. The code is
# explicitly coded so that it doesn’t use negative indices, and it (hopefully)
# always access within bounds. We can add a decorator to disable bounds
# checking:
cimport cython

__all__ = ["bin_photon_events", "open_dat"]


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
    del TempTrace
    NewFile.close()
    return outfile


@cython.cdivision(True)
@cython.boundscheck(False)  # turn of bounds-checking for entire function
def open_dat(filename, callback=None, cb_kwargs={}):
    """Load "Flex02-12D" correlator.com files

    We open a .dat file as produced by the "Flex02-12D" correlator in photon
    history recorder mode.
    The file contains the time differences between single photon events.

    Parameters
    ----------
    filename : str
        Path to file
    callback : callable or None
        Callback function to be called throughout the algorithm. If the
        return value of `callback` is not None, the function will abort.
        Number of function calls: 3
    cb_kwargs : dict, optional
        Keyword arguments for `callback` (e.g. "pid" of process).

    Returns
    -------
    system_clock, datData
        The system clock in MHz and the photon time event stream.
        Returns (None, None) if the progress was aborted through the
        callback function.


    Notes
    -----
    Raw data file format (taken from manual):
     1. The file records the difference in system clock ticks (1/60 us)
        between photon event.
     2. The first byte identifies the format of the file 8 : 8 bit, 16: 16 bit
     3. The second byte identifies the system clock. 60MHz.
     4. The time unit is 1/system clock.
     5. 16 bit format. Each WORD (2 bytes) represents a photon event,
        time = WORD/system clock, unless the value is 0xFFFF, in which case,
        the following four bytes represent a photon event.
     6. 8 bit format: Each BYTE represents a photon event unless the value is
        0xFF, in which case, the BYTE means 255 clock ticks passed without a
        photon event. For example 0A 0B FF 08 means there are three
        photon events. The time series are 0x0A+1, 0x0B+1, 0xFF+8+1.

    """
    cdef np.ndarray[DTYPEuint16_t] Data
    cdef np.ndarray[DTYPEuint32_t] datData
    cdef int i, N
    # open file
    File = open(filename, 'rb')
    # 1st byte: get file format
    # should be 16 - for 16 bit
    fformat = int(np.fromfile(File, dtype="uint8", count=1))
    # 2nd byte: read system clock
    system_clock = int(np.fromfile(File, dtype="uint8", count=1))
    if fformat == 8:
        # No 8 bit format supported
        warnings.warn('8 bit format not supported.')
        File.close()
        return system_clock, None
    elif fformat == 32:
        # (There is an utility to convert data to 32bit)
        datData = np.fromfile(File, dtype="uint32", count=-1)
        File.close()
        return system_clock, datData
    elif fformat == 16:
        pass
    else:
        warnings.warn("Unknown format: {} bit".format(fformat))
        File.close()
        return system_clock, None
    # In case of 16 bit file format (assumed), read the rest of the file in
    # 16 bit format.
    # Load bunch of Data
    Data = np.fromfile(File, dtype="uint16", count=-1)
    File.close()

    # Now we need to check if there are any 0xFFFF values which would
    # mean, that we do not yet have the true data in our array.
    # There is 32 bit data after a 0xFFFF = 65535
    if callback is not None:
        ret = callback(**cb_kwargs)
        if ret is not None:
            return None, None

    occurrences = np.where(Data == 65535)[0]
    N = len(occurrences)

    if callback is not None:
        ret = callback(**cb_kwargs)
        if ret is not None:
            return None, None

    # Make a 32 bit array
    datData = np.uint32(Data)
    datData[occurrences] = np.uint32(
        Data[occurrences + 1]) + np.uint32(Data[occurrences + 2]) * 65536

    if callback is not None:
        ret = callback(**cb_kwargs)
        if ret is not None:
            return None, None

    # Now delete the zeros
    zeroids = np.zeros(N * 2)
    zeroids[::2] = occurrences + 1
    zeroids[1::2] = occurrences + 2

    datData = np.delete(datData, zeroids)

    del Data
    return system_clock, datData

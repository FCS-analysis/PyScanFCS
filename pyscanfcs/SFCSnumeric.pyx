# -*- coding: utf-8 -*-
""" 
    PyScanFCS
    
    Binning Data for Multiple Tau Algorithm

    As fast as you can get with python, binning the photon arrival times
    created by Photon.exe from correlator.com.

    See at the end of the file, which .dat file will be opened.
    In console, we ask for binning time in µs and an .int file
    is created.
    
    (C) 2012 Paul Müller

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License 
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

#import codecs, sys, win32console
import sys
import numpy as np                  # NumPy
from scipy import optimize as spopt # For least squares fit

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
# always access within bounds. We can add a decorator to disable bounds checking:
cimport cython
#@cython.boundscheck(False) # turn of bounds-checking for entire function
#def function():

# Vector to use as a list
#from libcpp.vector cimport vector



@cython.cdivision(True)
@cython.boundscheck(False) # turn of bounds-checking for entire function
def BinPhotonEvents(np.ndarray[DTYPEuint32_t] data, double t_bin, filename, dtype, dlg, binshift=None):
    """ Bin all photon arrival times in a numpy.uint32 array *data*, using 
        the binning time float *t_bin* and saving the intensity trace as
        the file *filename*. *dlg* is a python object that suports 
        dlg.Update, like a progress dialog.
    """
    cdef int N = len(data)
    BinData = []
    cdef double time_c = 0                 # time counter
    cdef int phot_c = 0                        # photon counter
    cdef int maxphot = 0
    cdef int j, i, emptybins, bin

    dtype=dtype

    print "Creating file " + filename + " ("+str(dtype.__name__)+")"

    NewFile = open(filename, 'wb')
    
    # Add number of empty bins to beginning of file
    if binshift is not None:
        NewFile.write(dtype(np.zeros(binshift)))
        
    TempTrace = list()

    for j in range(100):
        percent = str(j)
        if dlg.Update(j+1, "Counting photon events...")[0] == False:
            dlg.Destroy()
            return False

        for i in range(N/100):
            i = i+N/100*j
            time_c += data[i]

            if time_c >= t_bin:
                # Append counted photons and
                # reset counters
                #NewFile.write(dtype(phot_c))
                TempTrace.append(phot_c)
                time_c -=  t_bin
                phot_c = 0
                # Empty bins between this and next event:
                emptybins = int(time_c/t_bin)
                TempTrace += emptybins*[0]
                time_c -=  emptybins*t_bin
                # Equivalent to:
                # time_c = int(time_c)%int(t_bin)
            phot_c +=  1
        NewFile.write(dtype(TempTrace))
        TempTrace = list()


    # Now write the rest:
    for i in range(N/100*100,N-1):
        time_c += data[i]
        if time_c >= t_bin:
            # Append counted photons and
            # reset counters
            #NewFile.write(dtype(phot_c))
            TempTrace.append(phot_c)
            time_c -=  t_bin
            phot_c = 0
            # Empty bins between this and next event:
            emptybins = int(time_c/t_bin)
            TempTrace += emptybins*[0]
            time_c -=  emptybins*t_bin
            # Equivalent to:
            # time_c = int(time_c)%int(t_bin)
        phot_c +=  1
    NewFile.write(dtype(TempTrace))
    del TempTrace
    NewFile.close()

    return True


def FitExp(times, trace):
    """Fit an exponential function to the given trace.
       Base is times.
       Returns the functions plus paramtetera
    """
    # Set starting parameters for exponential fit
    expfunc = lambda p, x: p[0]*np.exp(-x/p[1])
    # parms = [ampl, decaytime]
    parms = np.zeros(2, dtype=np.float32)
    ltr = len(trace)
    border = np.int(np.ceil(ltr/50.))
    parms[0] = 1.*trace[:border].mean()
    parms[1] = times[-1]/np.log(parms[0])
    # Fit function is an exponential
    # Function to minimize via least squares
    # f_min = lambda p, x: expfunc(np.abs(p), x) - trace
    def f_min(p,x):
        p = np.abs(p)
        return expfunc(np.abs(p), x) - trace
    # Least squares
    popt, chi = spopt.leastsq(f_min, parms[:], args=(times))
    return np.abs(popt), expfunc


def FitGaussian(amplitudes, frequencies,  argmax):
    # Set starting parameters for gaussian fit
    # parms = [freq, ampl, sigma]
    parms = np.zeros(3, dtype=np.float32)
    parms[0] = frequencies[argmax]
    parms[1] = amplitudes[argmax]
    parms[2] = abs(frequencies[1]-frequencies[2])*2.
    # Fit function is a gaussian
    gauss = lambda p, x: np.exp(-((x-p[0])/p[2])**2 / 2) * p[1]/(p[2]*np.sqrt(2*np.pi))
    # Function to minimize via least squares
    f_min = lambda p, x: gauss(p, x) - amplitudes
    # Least squares
    popt, chi = spopt.leastsq(f_min, parms[:], args=(frequencies))
    return np.abs(popt), gauss



@cython.cdivision(True)
@cython.boundscheck(False) # turn of bounds-checking for entire function
def OpenDat(filename, dlg):
    # Open a data file
    """
    We open a .dat file as produced by the "Flex02-12D" correlator in photon
    history recorder mode.
    The file contains the time differences between single photon events.

    Returns:
    This function makes the filename publicly available, bins a couple
    of events to get 1e+6 points and plots them into the plotting area
    (plotarea), using the Bin_Photon_Events() function.

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
    format = int(np.fromfile(File, dtype="uint8", count=1))
    if format == 8:
        # No 8 bit format supported
        print 'Error 8 bit format not supported.'
        return None
    # 2nd byte: read system clock
    system_clock = int(np.fromfile(File, dtype="uint8", count=1))

    # There is an utility to convert data to 32bit. This makes life easier:
    if format == 32:
        datData = np.fromfile(File, dtype="uint32", count=-1)
        return  system_clock, datData
    # In case of 16 bit file format (assumed), read the rest of the file in
    # 16 bit format.
    # Load bunch of Data
    Data = np.fromfile(File, dtype="uint16", count=-1)
    File.close()

    # Now we need to check if there are any 0xFFFF values which would
    # mean, that we do not yet have the true data in our array.
    # There is 32 bit data after a 0xFFFF = 65535
    if dlg.Pulse("Searching for 32bit events.") == False:
        # Stop and end import of data
        dlg.Destroy()
        return
    occurences = np.where(Data == 65535)[0]
    N = len(occurences)
    if dlg.Pulse("Found "+str(N)+" 32bit events.") == False:
        # Stop and end import of data
        dlg.Destroy()
        return
    # Make a 32 bit array
    datData = np.uint32(Data)
    datData[occurences] = np.uint32(Data[occurences+1]) + np.uint32(Data[occurences+2])*65536

    if dlg.Pulse("Added new 32 bit array. Finishing...") == False:
        # Stop and end import of data
        dlg.Destroy()
        return

    # Now delete the zeros
    zeroids = np.zeros(N*2)
    zeroids[::2] = occurences + 1
    zeroids[1::2] = occurences + 2
    
    datData = np.delete(datData, zeroids)

    del Data
    return system_clock, datData


def ReduceTrace(trace, deltat, length):
    """
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
    T[:,1] = trace/deltat/1e3 # in kHz
    T[:,0] = np.arange(len(trace))*deltat*2**step
    return T




"""
This program creates a .dat file with photon arrival times as
it is produced by the FLEX correlators from correlator.com
in photon history recorder mode by "Photon.exe".
The generated files can be used to test multiple tau algorithm and
workflow of SFCS analyzation programs.
"""
import numpy as np
import multipletau
import csv


def MakeDat(linetime, noisearray, dtype, filename):
    """ Create a .dat file (like Photon.exe).
        System clock is fixed to 60MHz.
        linetime [s]
        noisearray integer array (uint16 or uint32)
    """
    NewFile = open(filename, 'wb')
    if dtype == np.uint32:
        newformat = np.uint8(32)
    elif dtype == np.uint16:
        newformat = np.uint8(16)
    else:
        raise ValueError
    newclock = np.uint8(60)
    NewFile.write(newformat)
    NewFile.write(newclock)
    noisearray = dtype(noisearray)
    # Create matrix. Each line is a scan.
    timeticks = linetime * newclock * 1e6  # 60MHz
    half1 = np.ceil(timeticks / 2)
    half2 = np.floor(timeticks / 2)
    for i in np.arange(len(noisearray)):
        # Create a line
        N = noisearray[i]
        if N == 0:
            line = np.zeros(1, dtype=dtype)
            # Only one event at the far corner
            line[0] = timeticks
            line.tofile(NewFile)
        else:
            line = np.ones(N + 1, dtype=dtype)
            # events are included between two far events
            line[0] = half1 - len(line)
            line[-1] = half2
            line.tofile(NewFile)
    NewFile.close()


def OnSaveDat(filename, data):
    # Save the Data
    """
    Save experimental data as 32bit format.

    Raw data file format:
     1. The file records the difference in system clock ticks (1/60 us)
        between photon events.
     2. The first byte identifies the format of the file: 32 bit
     3. The second byte identifies the system clock: usually 60MHz.
     4. The time unit is 1/system clock.
     5. 32 bit format. 4 bytes represent a photon event, 
        time = 4 bytes/system clock
    """
    # Make a reasonable 32bit filename
    NewFile = open(filename, 'wb')
    newformat = np.uint8(32)
    newclock = np.uint8(60)
    NewFile.write(newformat)
    NewFile.write(newclock)
    data = np.uint32(data)
    data.tofile(NewFile)
    NewFile.close()


def GenerateExpNoise(N, taud=20., variance=1., deltat=1.):
    """
        Generate exponentially correlated noise.
    """
    # length of mean0 trace
    N_steps = N
    dt = deltat
    # AR-1 processes - what does that mean?
    # time constant (inverse of correlationtime taud)
    g = 1. / taud
    # variance
    s0 = variance

    # normalization factor (memory of the trace)
    exp_g = np.exp(-g * dt)
    one_exp_g = 1 - exp_g
    z_norm_factor = np.sqrt(1 - np.exp(-2 * g * dt)) / one_exp_g

    # create random number array
    # generates random numbers in interval [0,1)
    randarray = np.random.random(N_steps)
    # make numbers random in interval [-1,1)
    randarray = 2 * (randarray - 0.5)

    # simulate exponential random behavior
    z = np.zeros(N_steps)
    z[0] = one_exp_g * randarray[0]
    for i in np.arange(N_steps - 1) + 1:
        z[i] = exp_g * z[i - 1] + one_exp_g * randarray[i]

    z = z * z_norm_factor * s0
    return z


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
    T[:, 1] = trace / deltat / 1e3  # in kHz
    T[:, 0] = np.arange(len(trace)) * deltat * 2**step
    return T


def SaveCSV(G, trace, filename):
    """ Save correlation and trace tuple array G and trace to a .csv file
        that can be opened with PyCorrFit.
    """
    # Save Correlation function
    with open(filename, 'w') as fd:
        fd.write('# This file was created using testmultipletau.py\r\n')
        fd.write('# Channel (tau [s])' + " \t,"
                 'Correlation function' + " \r\n")
        dataWriter = csv.writer(fd, delimiter=',')
        for i in np.arange(len(G)):
            dataWriter.writerow([str(G[i, 0]) + " \t", str(G[i, 1])])
    
        fd.write('# BEGIN TRACE \r\n')
        fd.write('# Time ([s])' + " \t,"
                 'Intensity Trace [kHz]' + " \r\n")
    
        for i in np.arange(len(trace)):
            dataWriter.writerow([str(trace[i, 0]) + " \t", str(trace[i, 1])])


# Line time to be found by SFCS analyzation software
linetime = 0.714  # in ms
# Time of exponentially correlated noise
taudiff = 7.  # in ms

noisearray = GenerateExpNoise(200000, taud=taudiff / linetime)
noisearray += np.abs(np.min(noisearray))
noisearray *= 30. / np.max(noisearray)
noisearray = np.uint32(noisearray)


# Create 32bit and 16bit binary .dat files
data = MakeDat(linetime / 1000, noisearray, np.uint16,
               "test_" + str(taudiff) + "ms_16bit.dat")
data = MakeDat(linetime / 1000, noisearray, np.uint32,
               "test_" + str(taudiff) + "ms_32bit.dat")

# Create reference .csv file to check results
G = multipletau.autocorrelate(
    noisearray, deltat=linetime / 1000, normalize=True)
newtrace = ReduceTrace(noisearray, deltat=linetime, length=500)
SaveCSV(G, newtrace, "test_" + str(taudiff) + "ms_reference.csv")

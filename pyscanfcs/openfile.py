"""filetype definitions"""
import astropy.io.fits
import numpy as np
from skimage.external import tifffile


def openAny(path, callback=None):
    """load any supported file type"""
    methods = methods_binned.copy()
    methods.update(methods_stream)

    for key in list(methods.keys()):
        if path.endswith(key):
            return methods[key](path, callback)


def openDAT(path, callback=None, cb_kwargs={}):
    """Load "Flex02-12D" correlator.com files

    We open a .dat file as produced by the "Flex02-12D" correlator in photon
    history recorder mode.
    The file contains the time differences between single photon events.

    Parameters
    ----------
    path : str
        Path to file
    callback : callable or None
        Callback function to be called throughout the algorithm. If the
        return value of `callback` is not None, the function will abort.
        Number of function calls: 3
    cb_kwargs : dict, optional
        Keyword arguments for `callback` (e.g. "pid" of process).

    Returns
    -------
    info: dict
        Dictionary containing the "system_clock" in MHz and the
        "data_stream" (photon arrival time event stream).
        Returns `None` if the progress was aborted through the
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
    # open file
    filed = open(path, 'rb')
    # 1st byte: get file format
    # should be 16 - for 16 bit
    fformat = int(np.fromfile(filed, dtype="<u1", count=1))
    # 2nd byte: read system clock
    system_clock = int(np.fromfile(filed, dtype="<u1", count=1))
    if fformat == 8:
        # No 8 bit format supported
        raise ValueError("8 bit format not supported!")
    elif fformat == 32:
        # (There is an utility to convert data to 32bit)
        data = np.fromfile(filed, dtype="<u4", count=-1)
    elif fformat == 16:
        # convert 16bit to 32bit
        # Read the rest of the file in 16 bit format.
        # Load bunch of Data
        data16 = np.fromfile(filed, dtype="<u2", count=-1)
        # Now we need to check if there are any 0xFFFF values which would
        # mean, that we do not yet have the true data in our array.
        # There is 32 bit data after a 0xFFFF = 65535
        if callback is not None:
            ret = callback(**cb_kwargs)
            if ret is not None:
                return

        # occurences of large values
        occ = np.where(data16 == 65535)[0]
        N = len(occ)

        if callback is not None:
            ret = callback(**cb_kwargs)
            if ret is not None:
                return

        # Make a 32 bit array
        data = np.uint32(data16)
        data[occ] = data16[occ + 1] + data16[occ + 2] * 65536

        if callback is not None:
            ret = callback(**cb_kwargs)
            if ret is not None:
                return None

        # Now delete the zeros
        zeroids = np.zeros(N * 2, dtype=int)
        zeroids[::2] = occ + 1
        zeroids[1::2] = occ + 2
        data = np.delete(data, zeroids)
    else:
        raise ValueError("Unknown format: {} bit".format(fformat))
    filed.close()

    info = {"data_stream": data,
            "system_clock": system_clock
            }

    return info


def openFITS(fname, callback=None):
    """ load .fits files """
    info = dict()

    fits = astropy.io.fits.open(fname)
    series = fits[0]
    head = series.header

    info["type"] = "binned"
    info["data_binned"] = series.data
    info["system_clock"] = head['SysClck']

    try:
        info["total_time"] = head['Total']
    except KeyError:
        info["total_time"] = None

    try:
        info["line_time"] = head['Tline']
    except KeyError:
        # Old "line scanning time" has new name: "scan cycle time"
        info["line_time"] = head['Tcycle']

    info["bin_time"] = head['Tbin']

    try:
        info["bin_shift"] = head['Binshift']
    except KeyError:
        info["bin_shift"] = None

    info["bins_per_line"] = len(series.data[0])

    info["size"] = series.data.shape[0] * series.data.shape[1]

    return info


def openLSM(fname, callback=None):
    """ open LSM780 file using tifffile """
    info = dict()
    info["type"] = "binned"

    lsm = tifffile.TiffFile(fname)

    # two channels 0, 1?
    info["data_binned"] = lsm.asarray()[0]
    info["system_clock"] = 1

    page = lsm.pages[0]
    # pixel time in us
    info["bin_time"] = page.cz_lsm_scan_information["tracks"][0]["pixel_time"]

    # line time in s -> us
    info["line_time"] = (page.cz_lsm_time_stamps[1] -
                         page.cz_lsm_time_stamps[0]) * 1e6

    # total time in s -> us
    info["total_time"] = (page.cz_lsm_time_stamps[-1] -
                          page.cz_lsm_time_stamps[0]) * 1e6

    info["bins_per_line"] = info["data_binned"].shape[1]
    info["size"] = info["data_binned"].shape[0] * info["data_binned"].shape[1]
    info["bin_shift"] = None

    return info


methods_stream = {"dat": openDAT}

methods_binned = {"fits": openFITS,
                  "lsm": openLSM}
#                  "tif": openTIF}

wx_dlg_wc_stream = "stream format ("
wx_dlg_wc_stream_end = ")|"
for key in list(methods_stream.keys()):
    wx_dlg_wc_stream += "*.{}, ".format(key)
    wx_dlg_wc_stream_end += "*.{};".format(key)
wx_dlg_wc_stream = wx_dlg_wc_stream.strip(
    " ,") + wx_dlg_wc_stream_end.strip(";")


wx_dlg_wc_binned = "binned format ("
wx_dlg_wc_binned_end = ")|"
for key in list(methods_binned.keys()):
    wx_dlg_wc_binned += "*.{}, ".format(key)
    wx_dlg_wc_binned_end += "*.{};".format(key)
wx_dlg_wc_binned = wx_dlg_wc_binned.strip(
    " ,") + wx_dlg_wc_binned_end.strip(";")

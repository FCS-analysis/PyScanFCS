# -*- coding: utf-8 -*-
""" PyScanFCS filetype definitions
"""

import numpy as np
import os
import tifffile
import pyfits

from . import SFCSnumeric




def openAny(fname, callback=None):
    """ load any supported file type"""
    methods = methods_binned.copy()
    methods.update(methods_stream)
    
    for key in list(methods.keys()):
        if fname.endswith(key):
            return methods[key](fname, callback) 


def openDAT(fname, callback=None):
    system_clock, intensity_data = SFCSnumeric.OpenDat(fname, callback)
    info = dict()
    info["data_stream"] = intensity_data
    info["system_clock"] = system_clock
    
    return info
    

def openFITS(fname, callback=None):
    """ load .fits files """
    info = dict()
    
    fits = pyfits.open(fname)
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
    """ open LSM file using tifffile """
    info = dict()
    info["type"] = "binned"
    
    lsm = tifffile.TiffFile(fname)
    
    info["data_binned"] = lsm.asarray()[0]
    info["system_clock"] = 1
    info["total_time"] = None
    
    page = lsm.pages[0]
    # pixel time in us
    info["bin_time"] = page.cz_lsm_scan_information["tracks"][0]["pixel_time"]
    
    # line time in s
    info["line_time"] = page.cz_lsm_time_stamps[1] - page.cz_lsm_time_stamps[0]
    
    info["bins_per_line"] = info["data_binned"].shape[1]
    info["size"] = info["data_binned"].shape[0] * info["data_binned"].shape[1]
    info["bin_shift"] = None
    
    return info
    
    

methods_stream = {"dat": openDAT}

methods_binned = {"fits": openFITS,
                  "lsm": openLSM}
#                  "tif": openTIF}

wx_dlg_wc_stream = ""
for key in list(methods_stream.keys()):
    wx_dlg_wc_stream += "{} files (*.{})|*.{}|".format(key, key, key)
wx_dlg_wc_stream.strip("|")


wx_dlg_wc_binned = ""
for key in list(methods_binned.keys()):
    wx_dlg_wc_binned += "{} files (*.{})|*.{}|".format(key, key, key)
wx_dlg_wc_binned.strip("|")


# photon stream files
ext_stream = ["dat"]
ext_binned = ["fits", "lsm", "tif"]

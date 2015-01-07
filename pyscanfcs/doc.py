# -*- coding: utf-8 -*-
u"""
    PyScanFCS

    Module doc

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
import csv
import matplotlib
import multipletau
import numpy
import os
import platform
import pyfits
import scipy
import sys

try:
    import wx
except:
    pass

# The icon file was created with
# img2py -i -n Main PyScanFCS_icon.png icon.py
try:
    from . import icon
except:
    pass
    
from . import uilayer


def GetLocationOfFile(filename):
    dirname = os.path.dirname(os.path.abspath(__file__))
    locations = [
                    dirname+"/../",
                    dirname+"/../pyscanfcs_doc/",
                    dirname+"/../doc/",
                ]
    ## freezed binaries:
    if hasattr(sys, 'frozen'):
        try:
            adir = sys._MEIPASS + "/doc/"
        except:
            adir = "./"
        locations.append(os.path.realpath(adir))
    for loc in locations:
        thechl = os.path.join(loc,filename)
        if os.path.exists(thechl):
            return thechl
            break
    # if this does not work:
    return None


def GetLocationOfChangeLog(filename = "ChangeLog.txt"):
    return GetLocationOfFile(filename)


def GetLocationOfDocumentation(filename = "PyScanFCS_doc.pdf"):
    """ Returns the location of the documentation if there is any."""
    return GetLocationOfFile(filename)



def description():
    return u"""PyScanFCS is a data displaying and processing
tool for perpendicular line scanning FCS utilizing 
correlator.com correlators. PyScanFCS is written in Python."""


def info(version):
    """ Returns a little info about our program and what it can do.
    """
    textwin = u"""
    Copyright 2011-2012 Paul Müller, Biotec - TU Dresden

    Data processing for perpendicular line scanning FCS.
    """
    textlin = u"""
    © 2011-2012 Paul Müller, Biotec - TU Dresden

    Data processing for perpendicular line scanning FCS.
    """
    if (platform.system() != 'Linux'):
        texta = textwin
    else:
        texta = textlin
    one = "    PyScanFCS version "+version+"\n\n"
    lizenz = ""
    for line in licence().splitlines():
        lizenz += "    "+line+"\n"
    ret = one + lizenz + texta
    return ret


def getMainIcon(pxlength=32):
    """ *pxlength* is the side length in pixels of the icon """
    # Set window icon
    iconBMP = icon.getMainBitmap()
    # scale
    image = wx.ImageFromBitmap(iconBMP)
    image = image.Scale(pxlength, pxlength, wx.IMAGE_QUALITY_HIGH)
    iconBMP = wx.BitmapFromImage(image)
    iconICO = wx.IconFromBitmap(iconBMP)
    return iconICO


def licence():
    return u"""PyScanFCS is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 2 of the License, 
or (at your option) any later version.

PyScanFCS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License 
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def SoftwareUsed():
    """ Return some Information about the software used for this program """
    text= "Python "+sys.version+\
           "\n\nModules:"+\
           "\n - matplotlib "+matplotlib.__version__+\
           "\n - multipletau "+multipletau.__version__+\
           "\n - NumPy "+numpy.__version__+\
           "\n - PyFITS "+pyfits.__version__+\
           "\n - SciPy "+scipy.__version__+\
           "\n - uilayer "+uilayer.__version__+\
           "\n - wxPython "+wx.__version__
    if hasattr(sys, 'frozen'):
        pyinst = "\n\nThis executable has been created using PyInstaller."
        text = text+pyinst
    return text


# Standard homepage
HomePage = "http://pyscanfcs.craban.de/"

# Changelog filename
ChangeLog = "ChangeLog.txt"
StaticChangeLog = GetLocationOfChangeLog(ChangeLog)


# Check if we can extract the version
try:
    clfile = open(StaticChangeLog, 'r')
    __version__ = clfile.readline().strip()
    clfile.close()     
except:
    __version__ = "0.0.0-unknown"


# Github homepage
GitChLog = "https://raw.github.com/paulmueller/PyScanFCS/master/ChangeLog.txt"
GitHome = "https://github.com/paulmueller/PyScanFCS"
GitWiki = "https://github.com/paulmueller/PyScanFCS/wiki"

# -*- coding: utf-8 -*-
""" PyScanFCS
    Paul Müller, Biotec - TU Dresden

    Module doc
    *doc* is the documentation. Functions for various text output point here.
"""
import csv
import matplotlib
import numpy
import os
import platform
import scipy
import sys
import wx

# The icon file was created with
# img2py -i -n Main PyScanFCS_icon.png icon.py
import icon
import multipletauc


def GetLocationOfChangeLog(filename = "ChangeLog.txt"):
    locations = list()
    fname1 = os.path.realpath(__file__)
    # Try one directory up
    dir1 = os.path.dirname(fname1)+"/../"
    locations.append(os.path.realpath(dir1))
    # In case of distribution with .egg files (pip, easy_install)
    dir2 = os.path.dirname(fname1)+"/../pyscanfcs_doc/"
    locations.append(os.path.realpath(dir2))
    ## freezed binaries:
    if hasattr(sys, 'frozen'):
        try:
            dir2 = sys._MEIPASS + "/doc/"
        except:
            dir2 = "./"
        locations.append(os.path.realpath(dir2))
    for loc in locations:
        thechl = os.path.join(loc,filename)
        if os.path.exists(thechl):
            return thechl
            break
    # if this does not work:
    return None


def GetLocationOfDocumentation(filename = "PyScanFCS_doc.pdf"):
    """ Returns the location of the documentation if there is any."""
    ## running from source
    locations = list()
    fname1 = os.path.realpath(__file__)
    # Documentation is usually one directory up
    dir1 = os.path.dirname(fname1)+"/../"
    locations.append(os.path.realpath(dir1))
    # In case of distribution with .egg files (pip, easy_install)
    dir2 = os.path.dirname(fname1)+"/../pyscanfcs_doc/"
    locations.append(os.path.realpath(dir2))
    ## freezed binaries:
    if hasattr(sys, 'frozen'):
        try:
            dir2 = sys._MEIPASS + "/doc/"
        except:
            dir2 = "./"
        locations.append(os.path.realpath(dir2))
    for loc in locations:
        thedoc = os.path.join(loc,filename)
        if os.path.exists(thedoc):
            return thedoc
            break
    # if this does not work:
    return None


def description():
    return """PyScanFCS is a data displaying and processing
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
    if platform.system() != 'Linux':
        texta = textwin
    else:
        texta = textlin
    one = "    PyScanFCS version "+version+"\n\n"
    lizenz = ""
    for line in licence().splitlines():
        lizenz += "    "+line+"\n"
    return one + lizenz + texta 


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
    return """PyScanFCS is free software: you can redistribute it and/or modify it
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
    # csv
    # matplotlib
    # NumPy
    # os
    # platform
    # SciPy 
    # struct
    # sys
    # wxPython
    # yaml 
    text= "Python "+sys.version+\
           "\n\nModules:"+\
           "\n - csv "+csv.__version__+\
           "\n - matplotlib "+matplotlib.__version__+\
           "\n - multipletauc "+multipletauc.__version__+\
           "\n - NumPy "+numpy.__version__+\
           "\n - os "+\
           "\n - platform "+platform.__version__+\
           "\n - SciPy "+scipy.__version__+\
           "\n - struct"+\
           "\n - sys "+\
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
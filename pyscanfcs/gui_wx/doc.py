"""
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
import os
import platform
import sys

import astropy
import matplotlib
import multipletau
import numpy
import scipy
import skimage
import wx


from .._version import version as __version__

def GetLocationOfFile(filename):
    dirname = os.path.dirname(os.path.abspath(__file__))
    locations = [
        dirname + "/../",
        dirname + "/../pyscanfcs_doc/",
        dirname + "/../doc/",
    ]

    for i in range(len(locations)):
        # check /usr/lib64/32 -> /usr/lib
        for larch in ["lib32", "lib64"]:
            if dirname.count(larch):
                locations.append(locations[i].replace(larch, "lib", 1))

    # freezed binaries:
    if hasattr(sys, 'frozen'):
        try:
            adir = sys._MEIPASS + "/doc/"
        except:
            adir = "./"
        locations.append(os.path.realpath(adir))
    for loc in locations:
        thechl = os.path.join(loc, filename)
        if os.path.exists(thechl):
            return thechl
            break
    # if this does not work:
    return None


def GetLocationOfChangeLog(filename="CHANGELOG"):
    return GetLocationOfFile(filename)


def GetLocationOfDocumentation(filename="PyScanFCS_doc.pdf"):
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
    one = "    PyScanFCS version " + version + "\n\n"
    lizenz = ""
    for line in licence().splitlines():
        lizenz += "    " + line + "\n"
    ret = one + lizenz + texta
    return ret


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
    text = "Python " + sys.version +\
           "\n\nModules:" +\
           "\n - Astropy " + astropy.__version__ +\
           "\n - matplotlib " + matplotlib.__version__ +\
           "\n - multipletau " + multipletau.__version__ +\
           "\n - NumPy " + numpy.__version__ +\
           "\n - scikit-image " + skimage.__version__ +\
           "\n - SciPy " + scipy.__version__ +\
           "\n - wxPython " + wx.__version__
    if hasattr(sys, 'frozen'):
        pyinst = "\n\nThis executable has been created using PyInstaller."
        text = text + pyinst
    return text


# Standard homepage
HomePage = "http://pyscanfcs.craban.de/"

# Changelog filename
ChangeLog = "CHANGELOG"
StaticChangeLog = GetLocationOfChangeLog(ChangeLog)


# Github homepage
GitChLog = "https://raw.github.com/FCS-analysis/PyScanFCS/master/CHANGELOG"
GitHome = "https://github.com/FCS-analysis/PyScanFCS"
GitWiki = "https://github.com/FCS-analysis/PyScanFCS/wiki"

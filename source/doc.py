# -*- coding: utf-8 -*-
""" ScanFCS
    Paul Müller, Biotec - TU Dresden

    Module doc
    *doc* is the documentation. Functions for various text output point here.
"""
import sys
import csv
import matplotlib
import numpy
import os
import platform
import scipy
import wx


def description():
    return """ScanFSC is a data displaying, fitting and processing
tool, targeted at Scanning FCS utilizing 
correlator.com correlators. FCSfit is written in Python."""


def licence():
    return """ScanFSC is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 2 of the License, 
or (at your option) any later version.

FCSfit is distributed in the hope that it will be useful,
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
           "\n - NumPy "+numpy.__version__+\
           "\n - os "+\
           "\n - platform "+platform.__version__+\
           "\n - SciPy "+scipy.__version__+\
           "\n - struct"+\
           "\n - sys "+\
           "\n - wxPython "+wx.__version__
           #"\n - yaml "+yaml.__version__
    if hasattr(sys, 'frozen'):
        pyinst = "\n\nThis executable has been created using PyInstaller 1.5.1"
        text = text+pyinst
    return text

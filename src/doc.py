# -*- coding: utf-8 -*-
""" PyScanFCS
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
import multipletauc


def description():
    return """PyScanFCS is a data displaying and processing
tool for perpendicular line scanning FCS utilizing 
correlator.com correlators. PyScanFCS is written in Python."""

def info(version):
    """ Returns a little info about our program and what it can do.
    """
    textwin = u"""
    Copyright 20011-2012 Paul Müller, Biotec - TU Dresden

    Data processing for perpendicular line scanning FCS.
    """
    textlin = """
    © 20011-2012 Paul Müller, Biotec - TU Dresden

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
           #"\n - yaml "+yaml.__version__
    if hasattr(sys, 'frozen'):
        pyinst = "\n\nThis executable has been created using PyInstaller."
        text = text+pyinst
    return text

# Changelog filename
ChangeLog = "ChangeLog.txt"
if hasattr(sys, 'frozen'):
    StaticChangeLog = os.path.join(sys._MEIPASS, "doc/"+ChangeLog)
else:
    StaticChangeLog = os.path.join(os.path.dirname(sys.argv[0]), "../"+ChangeLog)

clfile = open(StaticChangeLog, 'r')
__version__ = clfile.readline().strip()
clfile.close()     

# -*- coding: utf-8 -*-
"""
    When a membrane is scanned perpendicularly to its surface, the
    fluorescence signal originating from the membrane itself must be
    separated from the signal of the surrounding medium for an FCS
    analysis. PyScanFCS interactively extracts the fluctuating
    fluorescence signal from such measurements and applies a
    multiple-tau algorithm. The obtained correlation curves can be
    evaluated using PyCorrFit.

    Copyright (C) 2011-2012  Paul Müller

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

import multipletau
import sys
import warnings

from . import doc
from .SFCSnumeric import *

try:
    from .main import Main
except ImportError:
    print(sys.exc_info())
    warnings.warn("Frontend of `pyscanfcs` will not be available."+\
                  " Reason: {}.".format(sys.exc_info()[1]))


__version__ = doc.__version__
__author__ = "Paul Mueller"
__email__ = "paul.mueller@biotec.tu-dresden.de"
__license__ = "GPL v2"

"""PyScanFCS loader"""
from os.path import dirname, abspath
import warnings

import sys
sys.path.insert(0, dirname(dirname(abspath(dirname(__file__)))))

try:
    from pyscanfcs.gui_wx.main import Main
except ImportError:
    print(sys.exc_info())
    warnings.warn("Frontend of `pyscanfcs` will not be available." +
                  " Reason: {}.".format(sys.exc_info()[1]))
else:
    Main()

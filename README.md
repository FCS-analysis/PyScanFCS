![PyScanFCS](https://raw.github.com/paulmueller/PyScanFCS/master/doc-src/Images/PyScanFCS_logo_dark.png)
=========

This repository contains the source code of PyScanFCS - a tool for data evaluation in perpendicular line scanning FCS (fluorescence correlation spectroscopy).

When a membrane is scanned perpendicular to its surface, the fluorescence signal originating from the membrane itself must be separeted from the signal of the surrounding medium for an FCS analysis.
PyScanFCS interactively extracts the fluorecence fluctuation signal from such measurements and applies a multiple-tau algorithm. The obtained correlation curves can be evaluated using [PyCorrFit](https://github.com/paulmueller/PyCorrFit).

It is possible to create test-data containing exponentially correlated data with [MakeTestDat_SFCS.py](https://github.com/paulmueller/multipletau/blob/master/MakeTestDat_SFCS.py). The obtained correlation curves can be fitted with [PyCorrFit](https://github.com/paulmueller/PyCorrFit) using the [appropriate model function](https://github.com/paulmueller/multipletau/blob/master/ExampleFunc_Exp_correlated_noise.txt).

For further information, please visit the PyScanFCS homepage at [http://pyscanfcs.craban.de](http://pyscanfcs.craban.de).

- [Download the latest version](https://github.com/paulmueller/PyScanFCS/releases)
- [Documentation](https://github.com/paulmueller/PyScanFCS/raw/master/PyScanFCS_doc.pdf)
- [Using Cython on Windows XP](https://github.com/paulmueller/PyScanFCS/wiki/Using-Cython-on-Windows-XP)

PyScanFCS - creating binaries with PyInstaller
=========

Usage
-------------------

All cython (~.pyx) files must be compiled before scripts in this directory
can be run. In the PyScanFCS/src/ directory execute:

    python compile\_cython.py build\_ext --inplace

Download PyInstaller v.2.0 from http://www.pyinstaller.org/
To create a single binary file, go to the unpacked pyinstaller directory and execute

    python pyinstaller.py /Path/To/PyCorrFit.py

Alternatively, there are ~.spec files and scripts for Windows XP / Ubuntu12.04 in this directory for bundling binary files.

Note
-------------------

For more details, consult [PyCorrFit/pyinstaller-howto](https://github.com/paulmueller/PyCorrFit/tree/master/pyinstaller-howto).

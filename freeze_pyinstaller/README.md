PyScanFCS - creating binaries with PyInstaller
=========

Usage
-------------------

All cython (~.pyx) files must be compiled before scripts in this directory
can be run. In the PyScanFCS/ directory execute:

    python setup.py build_ext --inplace

Download PyInstaller from http://www.pyinstaller.org/ ([Working revision](https://github.com/pyinstaller/pyinstaller/commit/779d07b236a943a4bf9d2b1a0ae3e0ebcc914798)).
To create a single binary file, go to the unpacked pyinstaller directory and execute

    python pyinstaller.py /Path/To/PyScanFCS.py

Alternatively, there are ~.spec files and scripts for Windows / Mac / Debian  in this directory for bundling binary files.

Note
-------------------

For more details, consult [PyCorrFit/freeze_pyinstaller](https://github.com/paulmueller/PyCorrFit/tree/master/freeze_pyinstaller).

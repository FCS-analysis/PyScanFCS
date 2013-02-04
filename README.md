PyScanFCS
=========

This repository contains the source code of PyScanFCS - a tool for data evaluation in perpendicular line scanning FCS (fluorescence correlation spectroscopy).

When a membrane is scanned perpendicular to its surface, the fluorescence signal originating from the membrane itself must be separeted from the signal of the surrounding medium for an FCS analysis.
PyScanFCS interactively extracts the fluorecence fluctuation signal from such measurements and applies a multiple-tau algorithm. The obtained correlation curves can be evaluated using [PyCorrFit](https://github.com/paulmueller/PyCorrFit).

For further information, please visit the PyScanFCS homepage at [http://fcstools.dyndns.org/pyscanfcs](http://fcstools.dyndns.org/pyscanfcs).


###Cython and Windows XP 32bit - Procedure

Once Cython and MinGW are installed and the directories

    C:\Python27\Scripts  
    C:\MinGW\bin
  
are in the path variable, depending on the version of MinGW, all occurences of *-mno-cygwin* have to be removed from the file

    C:\Python27\Lib\distutils\cygwinccompiler.py
  
The numpy header files have to be included for cygwin. Copy

    C:\Python27\Lib\site-packages\numpy-1.6.2-py2.7-win32.egg\numpy\core\include\numpy

to

    C:\Python27\include\
    
This should enable you to compile the ~.pyx files by running the following code in PyScanFCS/src/

    python compile_cython.py build_ext --inplace

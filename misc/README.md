PyScanFCS - misc
===========

These are functions that are either implemented somehow in PyScanFCS or that can be used to test PyScanFCS.

- **binningc.pyx**: converts 16 bit ~.dat file format to 32 bit ~.dat file format (For further information, see the documentation of PyScanFCS at http://fcstools.dyndns.org/pyscanfcs)
- **dat2csv.py**: using a photon stream from a ~.dat file, it calculates the correlation curve and saves it as a ~.csv file for PyCorrFit http://fcstools.dyndns.org/pycorrfit
- **setup.py**: compiles binningc.pyx using Cython

Testing the PyScanFCS:
- **MakeTestDat_SFCS.py**: create a exponentially correlated noise in a ~.dat file that can be loaded with [PyScanFCS](https://github.com/FCS-analysis/PyScanFCS) (http://fcstools.dyndns.org/pyscanfcs)
- **ExampleFunc_Exp_correlated_noise.txt**: external model function for fitting of exponentially correlated noise using [PyCorrFit]https://github.com/FCS-analysis/PyCorrFit) (http://fcstools.dyndns.org/pycorrfit)

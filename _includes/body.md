When a membrane is scanned perpendicularly to its surface, the fluorescence signal
originating from the membrane itself must be separated from the signal of the
surrounding medium for an FCS analysis. PyScanFCS interactively extracts the
fluctuating fluorescence signal from such measurements and applies a multiple-tau
algorithm. The obtained correlation curves can be evaluated using
[PyCorrFit](https://github.com/paulmueller/PyCorrFit).


#### Supported Operating Systems:
- Windows XP/7 (binary and source code)  
- Ubuntu Linux 12.04 (binary and source code) 
- Any other system with a Python 2.7 and Cython installation (source code only) 

#### Supported Filetypes:
- Correlator.com (*.dat): Those are files usually created by e.g. Flex02-01D correlators.

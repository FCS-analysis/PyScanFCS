|PyScanFCS|
===========

|PyPI Version| |Build Status Win| |Build Status Travis| |Coverage Status| |Docs Status|

A tool for data evaluation in perpendicular line scanning fluorescence correlation spectroscopy (FCS)

When a membrane is scanned perpendicularly to its surface, the fluorescence signal
originating from the membrane itself must be separated from the signal of the
surrounding medium for an FCS analysis. PyScanFCS interactively extracts the
fluctuating fluorescence signal from such measurements and applies a multiple-tau
algorithm. The obtained correlation curves can be evaluated using
`PyCorrFit <https://github.com/FCS-analysis/PyCorrFit>`__.

Getting started
===============

Installation
------------
Installers for PyScanFCS are available at the `release page <https://github.com/FCS-analysis/PyScanFCS/releases>`__.

Documentation
-------------
A detailed documentation including an explanation of the graphical user interface and available model
functions is available as a `PDF file <https://github.com/FCS-analysis/PyScanFCS/wiki/PyScanFCS_doc.pdf>`__.



.. |PyScanFCS| image:: https://raw.github.com/FCS-analysis/PyScanFCS/master/doc/Images/PyScanFCS_logo_dark.png
.. |PyPI Version| image:: http://img.shields.io/pypi/v/PyScanFCS.svg
   :target: https://pypi.python.org/pypi/pyscanfcs
.. |Build Status Win| image:: https://img.shields.io/appveyor/ci/paulmueller/PyScanFCS/master.svg?label=win
   :target: https://ci.appveyor.com/project/paulmueller/pyscanfcs
.. |Build Status Travis| image:: https://img.shields.io/travis/FCS-analysis/PyScanFCS/master.svg?label=linux_osx
   :target: https://travis-ci.org/FCS-analysis/PyScanFCS
.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/FCS-analysis/PyScanFCS/master.svg
   :target: https://codecov.io/gh/FCS-analysis/PyScanFCS
.. |Docs Status| image:: https://readthedocs.org/projects/pyscanfcs/badge/?version=latest
   :target: https://readthedocs.org/projects/pyscanfcs/builds/

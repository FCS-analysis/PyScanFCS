PyScanFCS documentation
=======================
This is the new sphinx-based documentation of PyScanFCS which will replace
the LaTeX-based documentation eventually.


To install the requirements for building the documentation, run

    pip install -r requirements.txt

To compile the documentation, run

    sphinx-build . _build


Notes
=====
To view the sphinx inventory of PyScanFCS, run

   python -m sphinx.ext.intersphinx 'http://pyscanfcs.readthedocs.io/en/latest/objects.inv'

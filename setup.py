#!/usr/bin/env python
# To create a distribution package for pip or easy-install:
# python setup.py sdist
from setuptools import setup, find_packages, Extension
from Cython.Distutils import build_ext
import numpy as np

from os.path import join, dirname, realpath
from warnings import warn

# The next three lines are necessary for setup.py install to include
# ChangeLog and Documentation of PyCorrFit
from distutils.command.install import INSTALL_SCHEMES
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


# Get the version of PyCorrFit from the Changelog.txt
StaticChangeLog = join(dirname(realpath(__file__)), "ChangeLog.txt")

try:
    clfile = open(StaticChangeLog, 'r')
    version = clfile.readline().strip()
    clfile.close()     
except:
    warn("Could not find 'ChangeLog.txt'. PyScanFCS version is unknown.")
    version = "0.0.0-unknown"


EXTENSIONS = [Extension("pyscanfcs.SFCSnumeric",
                        ["pyscanfcs/SFCSnumeric.pyx"],
                        libraries=[],
                        include_dirs=[np.get_include()]
                        )
              ]

name='pyscanfcs'

setup(
    name=name,
    author='Paul Mueller',
    author_email='paul.mueller@biotec.tu-dresden.de',
    url='https://github.com/paulmueller/PyScanFCS',
    version=version,
    packages=[name],
    package_dir={name: name},
    data_files=[('pyscanfcs_doc', ['ChangeLog.txt', 'PyScanFCS_doc.pdf'])],
    license="GPL v2",
    description='Scientific tool for perpendicular line scanning FCS.',
    long_description=open(join(dirname(__file__), 'Readme.txt')).read(),
    scripts=['bin/pyscanfcs'],
    cmdclass={"build_ext": build_ext},
    include_package_data=True,
    ext_modules=EXTENSIONS,
    install_requires=[
        "cython",
        "matplotlib >= 1.1.0",
        "multipletau >= 0.1.4",
        "NumPy >= 1.5.1",
        "pyfits",
        "SciPy >= 0.8.0",
        "wxPython >= 2.8.10.1"
        ],
    keywords=["fcs", "fluorescence", "correlation", "spectroscopy",
              "perpendicular", "scanning", "multiple", "tau"],
    classifiers= [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Visualization',
        'Intended Audience :: Science/Research'
                 ],
    platforms=['ALL']
    )


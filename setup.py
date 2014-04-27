#!/usr/bin/env python
# To create a distribution package for pip or easy-install:
# python setup.py sdist
from setuptools import setup, find_packages
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

setup(
    name='pyscanfcs',
    author='Paul Mueller',
    author_email='paul.mueller@biotec.tu-dresden.de',
    url='https://github.com/paulmueller/PyScanFCS',
    version=version,
    packages=['pyscanfcs'],
    package_dir={'pyscanfcs': 'pyscanfcs'},
    data_files=[('pyscanfcs_doc', ['ChangeLog.txt', 'PyScanFCS_doc.pdf'])],
    license="GPL v2",
    description='Scientific tool for perpendicular line scanning FCS.',
    long_description=open(join(dirname(__file__), 'Readme.txt')).read(),
    scripts=['bin/pyscanfcs'],
    include_package_data=True,
    install_requires=[
        "multipletau >= 0.1.4",
        "NumPy >= 1.5.1",
        "SciPy >= 0.8.0",
        "wxPython >= 2.8.10.1",
        "matplotlib >= 1.1.0"]
    )


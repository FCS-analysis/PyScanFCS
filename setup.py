from setuptools import setup, Extension, find_packages
import sys

from os.path import join, dirname, realpath, exists

# The next three lines are necessary for setup.py install to include
# ChangeLog and Documentation of PyScanFCS
from distutils.command.install import INSTALL_SCHEMES
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# We don't need cython if a .whl package is available.
# Try to import cython and throw a warning if it does not work.
try:
    import numpy as np
except ImportError:
    print("NumPy not available. Building extensions "+
          "with this setup script will not work:", sys.exc_info())
    extensions = []
else:
    extensions = [Extension("pyscanfcs.sfcs_alg",
                            sources=["pyscanfcs/sfcs_alg.pyx"],
                            include_dirs=[np.get_include()]
                            )
                 ]

try:
    import urllib.request
except ImportError:
    pass
else:
    # Download documentation if it was not compiled
    pdfdoc = join(dirname(realpath(__file__)), "doc/PyScanFCS_doc.pdf")
    webdoc = "https://github.com/FCS-analysis/PyScanFCS/wiki/PyScanFCS_doc.pdf"
    if not exists(pdfdoc):
        print("Downloading {} from {}".format(pdfdoc, webdoc))
        import urllib
        #testfile = urllib.URLopener()
        urllib.request.urlretrieve(webdoc, pdfdoc)


author = u"Paul Müller"
authors = [author]
description = 'Scientific tool for perpendicular line scanning FCS.'
name='pyscanfcs'
year = "2012"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
try:
    from _version import version
except:
    version = "unknown"

setup(
    name=name,
    author=author,
    author_email='dev@craban.de',
    url='https://github.com/FCS-analysis/PyScanFCS',
    version=version,
    packages=find_packages(include=(name+"*",)),
    license="GPL v2",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    include_package_data=True,
    ext_modules = extensions,
    install_requires=[
        "astropy",
        "matplotlib>=1.1.0",
        "multipletau>=0.1.4",
        "numpy>=1.5.1",
        "scikit-image>=0.13.1",
        "scipy>=0.8.0",
        "wxpython>=4.0.1",
        ],
    setup_requires=['cython', 'numpy', 'pytest-runner'],
    tests_require=["pytest"],
    python_requires='>=3.4, <4',
    keywords=["fcs", "fluorescence correlation spectroscopy",
              "perpendicular line scanning", "multiple-tau"],
    classifiers= [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Visualization',
        'Intended Audience :: Science/Research'
                 ],
    platforms=['ALL'],
    entry_points={
       "gui_scripts": ["{name:s}={name:s}:Main".format(**{"name":name})]
       }
    )

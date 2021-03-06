# -*- mode: python -*-
import codecs
import os
import platform
import sys

sys.setrecursionlimit(5000)

if not os.path.exists(".appveyor"):
    raise Exception("Please go to `PyScanFCS` directory.")

## Patch matplotlibrc
# This patch is required so matplotlib does not try to start with
# the "TkAgg" backend, resulting in import errors.
import matplotlib
mplrc = matplotlib.matplotlib_fname()
with open(mplrc) as fd:
    data = fd.readlines()
for ii, l in enumerate(data):
    if l.strip().startswith("backend "):
        data[ii] = "backend : WXAgg\n"
with open(mplrc, "w") as fd:
    fd.writelines(data)

name = "PyScanFCS"
DIR = os.path.realpath(".")
PyInstDir = os.path.join(DIR, ".appveyor")
PCFDIR = os.path.join(DIR, "pyscanfcs")
ProgPy = os.path.join(PCFDIR,"gui_wx/PyScanFCS.py")
ChLog = os.path.join(DIR,"CHANGELOG")
DocPDF = os.path.join(DIR,"doc/PyScanFCS_doc.pdf")
ICO = os.path.join(PyInstDir,"PyScanFCS.ico")

sys.path.append(DIR)

## Create inno setup .iss file
import pyscanfcs
version = pyscanfcs.__version__
issfile = codecs.open(os.path.join(PyInstDir,"win7_innosetup.iss.dummy"), 'r', "utf-8")
iss = issfile.readlines()
issfile.close()
for i in range(len(iss)):
    if iss[i].strip().startswith("#define MyAppVersion"):
        iss[i] = '#define MyAppVersion "{:s}"\n'.format(version)
    if iss[i].strip().startswith("#define MyAppPlatform"):
        # sys.maxint returns the same for windows 64bit verions
        iss[i] = '#define MyAppPlatform "win_{}"\n'.format(platform.architecture()[0])
nissfile = codecs.open("win7_innosetup.iss", 'wb', "utf-8")
nissfile.write(u"\ufeff")
nissfile.writelines(iss)
nissfile.close()

hiddenimports = ["scipy.optimize",
                 "scipy._lib.messagestream",
                 "scipy.special._ufuncs_cxx",
                 "scipy.sparse.csgraph",
                 "scipy.sparse.csgraph._validation",
                 ]

a = Analysis([ProgPy],
             pathex=[DIR],
             hiddenimports=hiddenimports,
             hookspath=[PyInstDir],
             runtime_hooks=None,
             )

a.datas += [('doc\\CHANGELOG', ChLog, 'DATA'),
            ('doc\\PyScanFCS_doc.pdf', DocPDF, 'DATA'),
            ]

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=name+'.exe',
          debug=False,
          strip=None,
          upx=True,
          icon=ICO,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=name)

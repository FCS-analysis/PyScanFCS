#!/bin/bash

# **************** Change Variables Here ************
# Directory structure:
# ./PyScanFCS           # git repository
# ./pyinstaller-2.0/    # Pyinstaller files
# ./Uploads             # Binary and zip files
PyInstaller="pyinstaller-2.0/"
Uploads="Uploads/"
# Progname.py should be in the Progdir
Progname="PyScanFCS"
# We require a ChangeLog.txt and a source directory in the Progdir
# BASEDIR/PyScanFCS/freeze_pyinstaller
BASEDIR=$(dirname $0)
cd $BASEDIR
BASEDIR=$(pwd)
cd "../"
StartDir=$(pwd)"/"
Progdir=${StartDir}${Progname}"/"
# We require a Progname_doc.tex in the source-doc directory
DocDir=${StartDir}${Progname}"/doc/"
PyInstallerDir=${Progdir}${PyInstaller}
Specfile=${BASEDIR}"/"${Progname}"_linux.spec"
echo $Specfile

echo "********************************"
echo "* Creating "${Progname}" binary *"
echo "********************************"

cd $StartDir

if [ -f $Specfile ]
then
    # added following line (remove build directory beforehand!)
    # a.datas += [('doc/ChangeLog.txt', '/PATH/TO/PyCorrFit/ChangeLog.txt', 'DATA')]
    pyinstaller -F $Specfile
else
    echo "Could not find specfile. Proceeding without..."
    sleep 1
    pyinstaller -F ${Progdir}"pyscanfcs/"${Progname}".py"
fi

# make executable
chmod +x ${Progdir}"dist/"${Progname}

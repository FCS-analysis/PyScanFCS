#!/bin/bash

BASEDIR=$(dirname $BASH_SOURCE)
cd $BASEDIR
BASEDIR=$(pwd)
cd "../"

# We need to run PyScanFCS in a separate Terminal to prevent this error
# from occuring:
#
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xcf
# in position 0: ordinal not in range(128)
#
# tags: pyinstaller app bundling wxpython

appn="./PyScanFCS.app"

if [ -e $appn ]; then rm -R $appn; fi

python ./Pyinstaller-2.1/pyinstaller.py -y ./freeze_pyinstaller/PyScanFCS_mac.spec

if [ $? != 0 ]; then exit 1; fi

# move aside the binary and replace with script

mv ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS.bin

cp ./freeze_pyinstaller/macOSx_script_starter.sh ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS

chmod +x ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS


vers=$(head -n1 ChangeLog.txt | tr -d '\r')

zipapp="./Mac_OSx_10.6+_PyScanFCS_${vers}_app.zip"

if [ -e $zipapp ]; then rm $zipapp; fi

pushd dist
zip -r -9 $zipapp $appn
popd

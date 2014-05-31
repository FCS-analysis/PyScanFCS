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

python ./Pyinstaller-2.1/pyinstaller.py -y ./pyinstaller-howto/PyScanFCS_mac.spec

# move aside the binary and replace with script

mv ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS.bin

cp ./pyinstaller-howto/macOSx_script_starter.sh ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS

chmod +x ./dist/PyScanFCS.app/Contents/MacOS/PyScanFCS

cd %~dp0
cd ..
DEL /F /Q .\doc\PyScanFCS_doc.pdf
python setup.py build_ext --inplace

pyinstaller -y .\freeze_pyinstaller\PyScanFCS_win7.spec

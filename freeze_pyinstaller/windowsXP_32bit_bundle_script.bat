cd C:\Python27\pyinstaller*
del /q /s ..\PyScanFCS\pyinstaller-howto\build
del /q /s ..\PyScanFCS\pyinstaller-howto\dist
python pyinstaller.py ..\PyScanFCS\freeze_pyinstaller\PyScanFCS_win.spec

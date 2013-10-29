# -*- mode: python -*-
a = Analysis(['C:\\Python27\\PyScanFCS\\src\\PyScanFCS.py'],
             pathex=['C:\\Python27\\pyinstaller-pyinstaller-6ca4af8'],
             hiddenimports=[],
             hookspath=None)
a.datas += [('doc\\ChangeLog.txt', 'C:\\Python27\\PyScanFCS\\ChangeLog.txt', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'PyScanFCS.exe'),
          debug=False,
          strip=None,
          upx=True,
          icon='C:\\Python27\\PyScanFCS\\pyinstaller-howto\\PyScanFCS.ico',
#          console=False )
          console=True )


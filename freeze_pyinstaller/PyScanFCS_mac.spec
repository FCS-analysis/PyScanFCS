# -*- mode: python -*-
a = Analysis(['pyscanfcs/PyScanFCS.py'],
             pathex=['PyInstaller-2.1'],
             hookspath=None)
a.datas += [('doc/ChangeLog.txt', 'ChangeLog.txt', 'DATA'),
            ('doc/PyScanFCS_doc.pdf', 'doc/PyScanFCS_doc.pdf', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PyScanFCS',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='PyScanFCS')
app = BUNDLE(coll,
             name='PyScanFCS.app',
             icon='freeze_pyinstaller/PyScanFCS.icns')

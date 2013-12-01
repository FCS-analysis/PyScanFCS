# -*- mode: python -*-
a = Analysis(['PyScanFCS/src/PyScanFCS.py'],
             pathex=['pyinstaller-2.0'],
             hiddenimports=[],
             hookspath=None)
a.datas += [('doc/ChangeLog.txt', 'PyScanFCS/ChangeLog.txt', 'DATA'),
            ('doc/PyScanFCS_doc.pdf', 'PyScanFCS/PyScanFCS_doc.pdf', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'PyScanFCS'),
          debug=False,
          strip=None,
          upx=True,
          console=True )

# -*- mode: python -*-
a = Analysis(['pyscanfcs/PyScanFCS.py'],
             pathex=[],
             hiddenimports=[],
             hookspath=None)
a.datas += [('doc/ChangeLog.txt', 'ChangeLog.txt', 'DATA'),
            ('doc/PyScanFCS_doc.pdf', 'doc/PyScanFCS_doc.pdf', 'DATA')]
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
          console=False
         )

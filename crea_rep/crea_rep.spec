# -*- mode: python -*-
a = Analysis(['crea_rep.py'],
             pathex=['e:\\crea_rep'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'crea_rep.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='logo.ico')
app = BUNDLE(exe,
             name=os.path.join('dist', 'crea_rep.exe.app'))

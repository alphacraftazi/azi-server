# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\alpay\\.gemini\\antigravity\\scratch\\azi_server\\installers\\Setup_EMLAK_PRO_A3B29DFF-7B1A-46CE-B5FA-297AF4FA35B8\\AlphaEmlak_pro\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AlphaEmlak_pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

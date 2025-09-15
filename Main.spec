# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[('fonts/Retro/Perfect DOS VGA 437.ttf', 'fonts/Retro'), ('sounds/coin/*.mp3', 'sounds/coin'), ('sounds/dash/*.mp3', 'sounds/dash'), ('sounds/portal/*.mp3', 'sounds/portal'), ('music/*.mp3', 'music'), ('background/*.webp', 'background')],
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
    name='Main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

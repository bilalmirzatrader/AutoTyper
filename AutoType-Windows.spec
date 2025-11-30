# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Mark\\Documents\\Mark New\\auto_type_windows.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['customtkinter', 'PIL', 'PIL._tkinter_finder', 'pyautogui', 'win32api', 'win32con', 'win32gui'],
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
    name='AutoType-Windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Mark\\Documents\\Mark New\\icon.ico'],
)

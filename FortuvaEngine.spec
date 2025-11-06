# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Windows build of Fortuva Engine
Usage: pyinstaller --clean modern-login.spec
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all PyQt5 modules and data
pyqt5_datas, pyqt5_binaries, pyqt5_hiddenimports = collect_all('PyQt5')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=pyqt5_binaries,
    datas=[
        ('icons', 'icons'),
        ('img', 'img'),
        ('icons_rc.py', '.'),
        ('engine', 'engine'),
    ] + pyqt5_datas,
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        'solana',
        'solders',
        'anchorpy',
        'base58',
        'requests',
        'plyer',
        'plyer.platforms.win.notification',
    ] + pyqt5_hiddenimports + collect_submodules('PyQt5'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FortuvaEngine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/fortuva.ico',  # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FortuvaEngine',
)


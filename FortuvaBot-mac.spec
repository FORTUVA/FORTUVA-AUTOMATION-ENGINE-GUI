# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for macOS build of Fortuva Bot
Usage: pyinstaller --clean modern-login-mac.spec
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
        ('bot', 'bot'),
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
        'plyer.platforms.macosx.notification',
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
    name='FortuvaBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FortuvaBot',
)

app = BUNDLE(
    coll,
    name='FortuvaBot.app',
    icon='icons/fortuva.ico',  # Application icon
    bundle_identifier='com.fortuva.bot',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025',
    },
)


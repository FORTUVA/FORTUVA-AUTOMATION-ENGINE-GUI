# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Linux build of Fortuva Bot
Usage: pyinstaller --clean modern-login-linux.spec
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules
import os
import sys

block_cipher = None

# Collect all PyQt5 modules and data
pyqt5_datas, pyqt5_binaries, pyqt5_hiddenimports = collect_all('PyQt5')

# Add Qt plugins explicitly
qt_plugins_path = None
if sys.platform.startswith('linux'):
    try:
        from PyQt5.QtCore import QLibraryInfo
        qt_plugins_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
        print(f"Qt plugins path: {qt_plugins_path}")
        
        # Add platform plugins (xcb, wayland, etc.)
        if qt_plugins_path and os.path.exists(qt_plugins_path):
            platforms_dir = os.path.join(qt_plugins_path, 'platforms')
            if os.path.exists(platforms_dir):
                for plugin in os.listdir(platforms_dir):
                    if plugin.endswith('.so'):
                        plugin_path = os.path.join(platforms_dir, plugin)
                        pyqt5_binaries.append((plugin_path, 'PyQt5/Qt5/plugins/platforms'))
                        print(f"Added platform plugin: {plugin}")
            
            # Add xcbglintegrations plugins
            xcb_dir = os.path.join(qt_plugins_path, 'xcbglintegrations')
            if os.path.exists(xcb_dir):
                for plugin in os.listdir(xcb_dir):
                    if plugin.endswith('.so'):
                        plugin_path = os.path.join(xcb_dir, plugin)
                        pyqt5_binaries.append((plugin_path, 'PyQt5/Qt5/plugins/xcbglintegrations'))
                        print(f"Added xcb plugin: {plugin}")
    except Exception as e:
        print(f"Warning: Could not collect Qt plugins: {e}")

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
        'PyQt5.QtDBus',
        'solana',
        'solders',
        'anchorpy',
        'base58',
        'requests',
        'plyer',
        'plyer.platforms.linux.notification',
    ] + pyqt5_hiddenimports + collect_submodules('PyQt5'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyqt5_hook.py'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FortuvaBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Don't strip - can break Qt plugins
    upx=False,    # Don't use UPX - can corrupt Qt libraries
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/fortuva.ico',  # Application icon
)


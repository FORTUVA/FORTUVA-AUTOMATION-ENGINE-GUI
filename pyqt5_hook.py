#!/usr/bin/env python3
"""
Runtime hook for PyQt5 to fix Qt platform plugin loading on Linux
This ensures Qt can find its platform plugins (xcb, wayland, etc.)
"""
import os
import sys
from pathlib import Path

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    bundle_dir = Path(sys._MEIPASS)
    
    # Set Qt plugin path
    qt_plugins_path = bundle_dir / 'PyQt5' / 'Qt5' / 'plugins'
    if qt_plugins_path.exists():
        os.environ['QT_PLUGIN_PATH'] = str(qt_plugins_path)
    
    # Set Qt platform plugin path specifically
    platforms_path = bundle_dir / 'PyQt5' / 'Qt5' / 'plugins' / 'platforms'
    if platforms_path.exists():
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(platforms_path)
    
    # Disable Wayland if causing issues (fallback to X11)
    # This fixes the warning: "Ignoring XDG_SESSION_TYPE=wayland on Gnome"
    if 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
    
    # Set library path for Qt libraries
    lib_path = bundle_dir / 'PyQt5' / 'Qt5' / 'lib'
    if lib_path.exists():
        if 'LD_LIBRARY_PATH' in os.environ:
            os.environ['LD_LIBRARY_PATH'] = str(lib_path) + ':' + os.environ['LD_LIBRARY_PATH']
        else:
            os.environ['LD_LIBRARY_PATH'] = str(lib_path)


#!/usr/bin/env python3
"""
Universal Build Script for Fortuva Engine
Automatically detects platform and builds the appropriate executable

Usage:
    python build_scripts/build_all.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("Fortuva Engine - Universal Build Script")
    print("=" * 60)
    
    # Detect platform
    platform = sys.platform
    
    if platform == 'win32':
        print("\n[Windows] Detected Windows")
        script = Path(__file__).parent / "build_windows.py"
    elif platform == 'darwin':
        print("\n[macOS] Detected macOS")
        script = Path(__file__).parent / "build_macos.py"
    elif platform in ['linux', 'linux2']:
        print("\n[Linux] Detected Linux")
        script = Path(__file__).parent / "build_linux.py"
    else:
        print(f"\n[ERROR] Unsupported platform: {platform}")
        sys.exit(1)
    
    print(f"   Running: {script.name}")
    
    # Run platform-specific build script
    try:
        subprocess.run([sys.executable, str(script)], check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[*] Build cancelled by user")
        sys.exit(1)

if __name__ == "__main__":
    main()


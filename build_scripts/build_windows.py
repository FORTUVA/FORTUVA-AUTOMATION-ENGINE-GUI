#!/usr/bin/env python3
"""
Windows Build Script for Fortuva Engine
Builds a Windows executable using PyInstaller

Requirements:
    - Python 3.8+
    - PyInstaller: pip install pyinstaller
    - All project dependencies from requirements.txt

Usage:
    python build_scripts/build_windows.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("Building Fortuva Engine for Windows")
    print("=" * 60)
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"\n[*] Project root: {project_root}")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller not found!")
        print("        Install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Check if spec file exists
    spec_file = project_root / "FortuvaEngine.spec"
    if not spec_file.exists():
        print(f"[ERROR] Spec file not found: {spec_file}")
        sys.exit(1)
    
    print(f"[OK] Using spec file: {spec_file}")
    
    # Clean previous builds
    print("\n[*] Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"    Removed {dir_name}/")
    
    # Run PyInstaller
    print("\n[*] Building executable...")
    print("    This may take several minutes...")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        # Check if executable was created
        exe_path = project_root / "dist" / "FortuvaEngine" / "FortuvaEngine.exe"
        if exe_path.exists():
            print("\n" + "=" * 60)
            print("[SUCCESS] Build successful!")
            print("=" * 60)
            print(f"\n[*] Executable location:")
            print(f"    {exe_path}")
            print(f"\n[*] Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
            
            # Create distribution folder
            dist_folder = project_root / "dist" / "FortuvaEngine"
            print(f"\n[*] Distribution folder:")
            print(f"    {dist_folder}")
            print(f"\n[*] To distribute:")
            print(f"    1. Zip the entire '{dist_folder.name}' folder")
            print(f"    2. Or create an installer with NSIS/Inno Setup")
            print(f"\n[*] To run:")
            print(f"    Double-click FortuvaEngine.exe")
            
        else:
            print("\n[ERROR] Build failed: Executable not found")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


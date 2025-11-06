#!/usr/bin/env python3
"""
Linux Build Script for Fortuva Engine
Builds a Linux executable using PyInstaller

Requirements:
    - Python 3.8+
    - PyInstaller: pip install pyinstaller
    - All project dependencies from requirements.txt
    - Qt5 libraries (usually pre-installed on desktop Linux)

Usage:
    python build_scripts/build_linux.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("Building Fortuva Engine for Linux")
    print("=" * 60)
    
    # Check if running on Linux
    if sys.platform not in ['linux', 'linux2']:
        print("⚠️  Warning: Not running on Linux")
        print("   The executable may not work correctly")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"\n📁 Project root: {project_root}")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found!")
        print("   Install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Check if spec file exists
    spec_file = project_root / "FortuvaEngine-linux.spec"
    if not spec_file.exists():
        print(f"❌ Spec file not found: {spec_file}")
        sys.exit(1)
    
    print(f"✓ Using spec file: {spec_file}")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed {dir_name}/")
    
    # Run PyInstaller
    print("\n🔨 Building executable...")
    print("   This may take several minutes...")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        # Check if executable was created (single file in dist/)
        exe_path = project_root / "dist" / "FortuvaEngine"
        if exe_path.exists():
            # Make executable
            os.chmod(exe_path, 0o755)
            
            print("\n" + "=" * 60)
            print("✅ Build successful!")
            print("=" * 60)
            print(f"\n📦 Executable location:")
            print(f"   {exe_path}")
            print(f"\n📊 Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
            
            print(f"\n💡 To distribute:")
            print(f"   1. Copy the single 'FortuvaEngine' file")
            print(f"   2. Or create an AppImage (see build_appimage.py)")
            print(f"   3. Or create DEB/RPM packages")
            
            print(f"\n🚀 To run:")
            print(f"   cd dist/")
            print(f"   ./FortuvaEngine")
            
            print(f"\n⚠️  Important Notes:")
            print(f"   1. This binary is compiled for your specific Linux distribution")
            print(f"   2. Users may need to install Qt/X11 system libraries:")
            print(f"      Ubuntu/Debian: sudo apt-get install libxcb-xinerama0 libxcb-icccm4 \\")
            print(f"                     libxcb-image0 libxcb-keysyms1 libxkbcommon-x11-0")
            print(f"   3. See LINUX_TROUBLESHOOTING.md for detailed setup instructions")
            print(f"   4. Consider creating an AppImage for broader compatibility")
            
        else:
            print("\n❌ Build failed: Executable not found")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


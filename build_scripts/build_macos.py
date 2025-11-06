#!/usr/bin/env python3
"""
macOS Build Script for Fortuva Engine
Builds a macOS application bundle using PyInstaller

Requirements:
    - Python 3.8+
    - PyInstaller: pip install pyinstaller
    - All project dependencies from requirements.txt
    - macOS 10.13+ (High Sierra or later)

Usage:
    python build_scripts/build_macos.py

Optional: Code signing
    codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/FortuvaEngine.app
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("Building Fortuva Engine for macOS")
    print("=" * 60)
    
    # Check if running on macOS
    if sys.platform != 'darwin':
        print("⚠️  Warning: Not running on macOS")
        print("   The app bundle may not work correctly")
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
    spec_file = project_root / "FortuvaEngine-mac.spec"
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
    print("\n🔨 Building application bundle...")
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
        
        # Check if app bundle was created
        app_path = project_root / "dist" / "FortuvaEngine.app"
        if app_path.exists():
            print("\n" + "=" * 60)
            print("✅ Build successful!")
            print("=" * 60)
            print(f"\n📦 Application bundle:")
            print(f"   {app_path}")
            
            # Calculate size
            def get_dir_size(path):
                total = 0
                for entry in os.scandir(path):
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_dir_size(entry.path)
                return total
            
            size_mb = get_dir_size(app_path) / (1024*1024)
            print(f"\n📊 Size: {size_mb:.2f} MB")
            
            print(f"\n💡 To distribute:")
            print(f"   1. Test: Open FortuvaEngine.app")
            print(f"   2. Create DMG:")
            print(f"      hdiutil create -volname FortuvaEngine -srcfolder dist/FortuvaEngine.app -ov -format UDZO dist/FortuvaEngine.dmg")
            print(f"   3. (Optional) Code sign:")
            print(f'      codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/FortuvaEngine.app')
            
            print(f"\n🚀 To run:")
            print(f"   1. Double-click FortuvaEngine.app")
            print(f"   2. If unsigned, users may need to:")
            print(f"      Right-click → Open (first time only)")
            
        else:
            print("\n❌ Build failed: Application bundle not found")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


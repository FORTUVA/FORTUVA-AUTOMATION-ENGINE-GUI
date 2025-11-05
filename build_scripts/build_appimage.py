#!/usr/bin/env python3
"""
AppImage Build Script for Fortuva Bot
Creates an AppImage for Linux that works across distributions

Requirements:
    - Built Linux executable (run build_linux.py first)
    - appimagetool (downloaded automatically if not found)

Usage:
    python build_scripts/build_appimage.py

What is AppImage?
    AppImage is a universal Linux package format that bundles an application
    with all its dependencies. It works on most Linux distributions without
    installation or root access.
"""

import os
import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path

def download_appimagetool():
    """Download appimagetool if not available"""
    tool_path = Path("appimagetool-x86_64.AppImage")
    
    if tool_path.exists():
        print(f"✓ appimagetool found: {tool_path}")
        return tool_path
    
    print("📥 Downloading appimagetool...")
    url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    
    try:
        urllib.request.urlretrieve(url, tool_path)
        os.chmod(tool_path, 0o755)
        print(f"✓ Downloaded appimagetool")
        return tool_path
    except Exception as e:
        print(f"❌ Failed to download appimagetool: {e}")
        print(f"   Please download manually from: {url}")
        sys.exit(1)

def create_desktop_file(appdir):
    """Create .desktop file for AppImage"""
    desktop_content = """[Desktop Entry]
Type=Application
Name=Fortuva Bot
Comment=Solana Prediction Bot
Exec=FortuvaBot
Icon=fortuva-bot
Categories=Finance;Utility;
Terminal=false
"""
    
    desktop_file = appdir / "FortuvaBot.desktop"
    desktop_file.write_text(desktop_content)
    os.chmod(desktop_file, 0o755)
    print(f"✓ Created {desktop_file.name}")

def main():
    print("=" * 60)
    print("Building AppImage for Fortuva Bot")
    print("=" * 60)
    
    # Check if running on Linux
    if sys.platform not in ['linux', 'linux2']:
        print("❌ AppImage can only be built on Linux")
        sys.exit(1)
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"\n📁 Project root: {project_root}")
    
    # Check if Linux build exists
    dist_folder = project_root / "dist" / "FortuvaBot"
    exe_path = dist_folder / "FortuvaBot"
    
    if not exe_path.exists():
        print(f"❌ Linux executable not found: {exe_path}")
        print("   Run build_linux.py first!")
        sys.exit(1)
    
    print(f"✓ Found Linux executable")
    
    # Download appimagetool if needed
    appimagetool = download_appimagetool()
    
    # Create AppDir structure
    print("\n📦 Creating AppDir structure...")
    appdir = project_root / "FortuvaBot.AppDir"
    
    # Clean previous AppDir
    if appdir.exists():
        shutil.rmtree(appdir)
    
    # Create directories
    appdir.mkdir()
    (appdir / "usr").mkdir()
    (appdir / "usr" / "bin").mkdir()
    (appdir / "usr" / "share").mkdir()
    (appdir / "usr" / "share" / "icons").mkdir()
    (appdir / "usr" / "share" / "icons" / "hicolor").mkdir()
    (appdir / "usr" / "share" / "icons" / "hicolor" / "48x48").mkdir()
    (appdir / "usr" / "share" / "icons" / "hicolor" / "48x48" / "apps").mkdir()
    
    # Copy executable and dependencies
    print("   Copying files...")
    shutil.copytree(dist_folder, appdir / "usr" / "bin" / "FortuvaBot")
    
    # Create AppRun script
    apprun_content = """#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/FortuvaBot:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
cd "${HERE}/usr/bin/FortuvaBot"
exec "${HERE}/usr/bin/FortuvaBot/FortuvaBot" "$@"
"""
    
    apprun = appdir / "AppRun"
    apprun.write_text(apprun_content)
    os.chmod(apprun, 0o755)
    print(f"✓ Created AppRun script")
    
    # Create desktop file
    create_desktop_file(appdir)
    
    # Copy icon
    icon_src = project_root / "icons" / "rocket_48x48.png"
    icon_dest = appdir / "fortuva-bot.png"
    icon_dest2 = appdir / "usr" / "share" / "icons" / "hicolor" / "48x48" / "apps" / "fortuva-bot.png"
    
    if icon_src.exists():
        shutil.copy(icon_src, icon_dest)
        shutil.copy(icon_src, icon_dest2)
        print(f"✓ Copied icon")
    
    # Build AppImage
    print("\n🔨 Building AppImage...")
    appimage_output = project_root / "dist" / "FortuvaBot-x86_64.AppImage"
    
    # Remove old AppImage
    if appimage_output.exists():
        appimage_output.unlink()
    
    cmd = [
        str(appimagetool.absolute()),
        str(appdir.absolute()),
        str(appimage_output.absolute())
    ]
    
    try:
        # Set ARCH environment variable
        env = os.environ.copy()
        env['ARCH'] = 'x86_64'
        
        result = subprocess.run(cmd, check=True, capture_output=False, env=env)
        
        if appimage_output.exists():
            os.chmod(appimage_output, 0o755)
            
            print("\n" + "=" * 60)
            print("✅ AppImage build successful!")
            print("=" * 60)
            print(f"\n📦 AppImage location:")
            print(f"   {appimage_output}")
            print(f"\n📊 Size: {appimage_output.stat().st_size / (1024*1024):.2f} MB")
            
            print(f"\n💡 To distribute:")
            print(f"   Upload FortuvaBot-x86_64.AppImage")
            print(f"   Works on most Linux distributions (Ubuntu, Fedora, Debian, etc.)")
            
            print(f"\n🚀 To run:")
            print(f"   1. Make executable: chmod +x FortuvaBot-x86_64.AppImage")
            print(f"   2. Run: ./FortuvaBot-x86_64.AppImage")
            
            # Clean up AppDir
            print("\n🧹 Cleaning up...")
            shutil.rmtree(appdir)
            print(f"   Removed AppDir")
            
        else:
            print("\n❌ Build failed: AppImage not created")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


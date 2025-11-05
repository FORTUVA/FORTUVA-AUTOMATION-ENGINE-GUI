# Build Scripts Directory

This directory contains all the scripts needed to build executable versions of Fortuva Bot for different platforms.

## Files Overview

### Build Scripts
- **`build_all.py`** - Universal build script that auto-detects your OS
- **`build_windows.py`** - Build Windows executable (.exe)
- **`build_macos.py`** - Build macOS application bundle (.app)
- **`build_linux.py`** - Build Linux executable
- **`build_appimage.py`** - Build Linux AppImage (universal Linux package)

### Spec Files (in project root)
- **`FortuvaBot.spec`** - PyInstaller spec for Windows
- **`FortuvaBot-mac.spec`** - PyInstaller spec for macOS
- **`FortuvaBot-linux.spec`** - PyInstaller spec for Linux

## Quick Usage

### Option 1: Auto-detect and Build
```bash
python build_scripts/build_all.py
```

### Option 2: Platform-Specific
```bash
# Windows
python build_scripts/build_windows.py

# macOS
python build_scripts/build_macos.py

# Linux
python build_scripts/build_linux.py

# Linux AppImage
python build_scripts/build_linux.py
python build_scripts/build_appimage.py
```

## What Each Script Does

### build_all.py
1. Detects your operating system
2. Runs the appropriate platform-specific build script
3. Simple and convenient for most users

### build_windows.py
1. Checks for PyInstaller installation
2. Cleans previous builds
3. Runs PyInstaller with `FortuvaBot.spec`
4. Creates `dist/FortuvaBot/FortuvaBot.exe`
5. Shows build results and distribution instructions

### build_macos.py
1. Verifies you're running on macOS (warns if not)
2. Cleans previous builds
3. Runs PyInstaller with `FortuvaBot-mac.spec`
4. Creates `dist/FortuvaBot.app` application bundle
5. Provides code signing instructions

### build_linux.py
1. Checks platform
2. Cleans previous builds
3. Runs PyInstaller with `FortuvaBot-linux.spec`
4. Creates `dist/FortuvaBot/FortuvaBot` binary
5. Makes binary executable (chmod +x)

### build_appimage.py
1. Requires Linux build to be completed first
2. Downloads appimagetool if not present
3. Creates AppDir structure
4. Bundles executable with dependencies
5. Creates `dist/FortuvaBot-x86_64.AppImage`
6. Universal Linux package that works across distributions

## Prerequisites

### All Platforms
```bash
# Install project dependencies
pip install -r requirements.txt

# Install build tools
pip install -r requirements-build.txt
# Or: pip install pyinstaller
```

### Linux (for AppImage)
- Will auto-download `appimagetool` on first run
- Or install manually: `apt install appimagetool`

### macOS (for code signing)
- Apple Developer account
- Developer ID certificate
- Xcode command-line tools

### Windows (for code signing)
- Code signing certificate
- SignTool from Windows SDK

## Output Directory Structure

After building, you'll have:

```
dist/
├── FortuvaBot/              # Windows/Linux folder
│   ├── FortuvaBot(.exe)     # Main executable
│   ├── _internal/           # Dependencies
│   ├── icons/               # Resources
│   └── img/                 # Images
│
├── FortuvaBot.app/          # macOS (if built on macOS)
│   └── Contents/
│       ├── MacOS/
│       ├── Resources/
│       └── Info.plist
│
└── FortuvaBot-x86_64.AppImage  # Linux AppImage (if built)
```

## Customization

### Modifying Build Settings

Edit the `.spec` files in the project root to:
- Change app name
- Add/remove dependencies
- Include additional files
- Exclude modules to reduce size
- Change icon
- Modify code signing settings

Example (FortuvaBot.spec):
```python
a = Analysis(
    ['main.py'],
    datas=[
        ('icons', 'icons'),
        ('your_custom_folder', 'destination'),  # Add more files
    ],
    hiddenimports=[
        'PyQt5',
        'your_hidden_import',  # Add hidden imports
    ],
    excludes=['tkinter'],  # Exclude unused modules
)
```

### Changing Output Names

In the spec file, modify:
```python
exe = EXE(
    ...
    name='YourAppName',  # Change here
    ...
)
```

### Adding Icons

Replace in spec file:
```python
icon='path/to/your/icon.ico'  # Windows
icon='path/to/your/icon.icns'  # macOS
```

## Troubleshooting

### Build Fails with "ModuleNotFoundError"
Add missing module to `hiddenimports` in the spec file.

### Build Fails with "Permission Denied"
Run with appropriate permissions or check antivirus settings.

### Executable Doesn't Run
- Windows: Check antivirus, try running as administrator
- macOS: Right-click → Open, or disable Gatekeeper temporarily
- Linux: Ensure `chmod +x` was applied

### Large File Size
- Normal range: 50-150 MB
- Reduce by excluding unused modules
- Use UPX compression (if available)

### Can't Find Resources at Runtime
- Check `datas` parameter in spec file
- Ensure paths are relative to project root
- Test with `--debug` flag

## Advanced Usage

### Debug Build
Add `--debug` flag for verbose output:
```python
# Modify spec file:
exe = EXE(
    ...
    debug=True,
    console=True,  # Show console for debugging
    ...
)
```

### One-File Mode (Windows)
Slower startup but single .exe file:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Include binaries
    a.zipfiles,  # Include zipfiles
    a.datas,     # Include data files
    [],
    name='FortuvaBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True,  # Add this
)
```

### Cross-Compilation (Docker)
Build for other platforms using Docker:
```bash
# Build Windows .exe from Linux
docker run --rm -v "$(pwd):/src" cdrx/pyinstaller-windows

# Build Linux binary from Windows
docker run --rm -v "$(pwd):/src" cdrx/pyinstaller-linux
```

## Best Practices

1. **Clean builds**: Always use `--clean` flag
2. **Test on clean machine**: Without Python installed
3. **Version control**: Keep spec files in git
4. **Document changes**: Note any modifications to build process
5. **Automate**: Consider CI/CD for building releases
6. **Sign executables**: For production distributions

## Need Help?

1. Check main documentation: `BUILDING_EXECUTABLES.md`
2. Detailed guide: `build_executable.md`
3. PyInstaller docs: https://pyinstaller.org/
4. Open an issue if you encounter problems

---

**Remember**: Always test your executables on the target platform before distribution!


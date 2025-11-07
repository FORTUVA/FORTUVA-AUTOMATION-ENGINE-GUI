# Building Executables for All Operating Systems

This guide will help you create standalone executable files for the Fortuva Engine application on Windows, macOS, and Linux.

## Prerequisites

### All Platforms
- Python 3.8 or higher
- All dependencies installed from `requirements.txt`
- PyInstaller: `pip install pyinstaller`

## Quick Start

### Windows
```bash
python build_scripts/build_windows.py
```

### macOS
```bash
python build_scripts/build_macos.py
```

### Linux
```bash
python build_scripts/build_linux.py
```

## Detailed Instructions

### 1. Windows (.exe)

#### Building on Windows:
```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python build_scripts/build_windows.py

# Or manually:
pyinstaller --clean FortuvaEngine.spec
```

**Output:** `dist/FortuvaEngine.exe` (single executable file)

**Distribution:** 
- You can distribute just the `.exe` file
- Alternatively, distribute the entire `dist/FortuvaEngine/` folder if using one-folder mode
- Users can run it directly without Python installed

---

### 2. macOS (.app)

#### Building on macOS:
```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python build_scripts/build_macos.py

# Or manually:
pyinstaller --clean FORTUVA-AUTOMATION-ENGINE-GUI
-mac.spec
```

**Output:** `dist/FortuvaEngine.app` (application bundle)

**Code Signing (Optional but Recommended):**
```bash
# Sign the app to avoid Gatekeeper warnings
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/FortuvaEngine.app
```

**Distribution:**
- Compress to `.dmg` for easy distribution
- Users can drag to Applications folder
- If unsigned, users need to right-click → Open first time

---

### 3. Linux (AppImage/Binary)

#### Building on Linux:
```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python build_scripts/build_linux.py

# Or manually:
pyinstaller --clean FORTUVA-AUTOMATION-ENGINE-GUI
-linux.spec
```

**Output:** `dist/FortuvaEngine` (standalone binary)

**Creating AppImage (Recommended for distribution):**
```bash
# Install appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Build AppImage
python build_scripts/build_appimage.py
```

**Distribution:**
- AppImage: Single file that runs on most Linux distributions
- Binary: Works on similar Linux distributions (same glibc version)
- Users may need to `chmod +x FortuvaEngine` before running

---

## Cross-Platform Building (Advanced)

### Building Windows .exe from Linux/macOS
Use Wine or a Windows virtual machine/container:
```bash
# Using Docker
docker run --rm -v "$(pwd):/src" cdrx/pyinstaller-windows
```

### Building macOS .app from Linux/Windows
⚠️ **Not recommended** - macOS apps should be built on macOS due to code signing and system libraries

### Building Linux binary from Windows/macOS
```bash
# Using Docker
docker run --rm -v "$(pwd):/src" cdrx/pyinstaller-linux
```

---

## Troubleshooting

### Common Issues

#### 1. Missing Dependencies
**Error:** "ModuleNotFoundError" when running executable

**Solution:** Add hidden imports to spec file:
```python
hiddenimports=['anchorpy', 'solana', 'solders', 'base58', 'plyer']
```

#### 2. Qt Platform Plugin Issues
**Error:** "Could not find the Qt platform plugin"

**Solution:** Already handled in spec files with `--hidden-import PyQt5`

#### 3. Resource Files Not Found
**Error:** Cannot find `icons_rc.py`, `img/solana_bg.webp`

**Solution:** Already handled in spec files with `datas` parameter

#### 4. Large Executable Size
The executables will be 50-150MB due to Python runtime, Qt libraries, and blockchain dependencies.

**Optimization:**
- Use UPX compression: `pyinstaller --upx-dir=/path/to/upx ...`
- Remove debug symbols: `--strip` (Linux/macOS)
- Use one-file mode for Windows: `--onefile`

#### 5. Antivirus False Positives (Windows)
Some antivirus software may flag PyInstaller executables.

**Solution:**
- Code sign your executable with a valid certificate
- Submit to antivirus vendors as false positive
- Use one-folder mode instead of one-file

---

## File Structure After Building

```
dist/
├── Windows/
│   └── FortuvaEngine.exe           # Windows executable
├── macOS/
│   └── FortuvaEngine.app/          # macOS app bundle
└── Linux/
    ├── FortuvaEngine               # Linux binary
    └── FortuvaEngine.AppImage      # AppImage (optional)
```

---

## Distribution Checklist

- [ ] Test executable on clean machine (without Python installed)
- [ ] Include README with usage instructions
- [ ] Include LICENSE file
- [ ] Document system requirements (OS version, etc.)
- [ ] Provide sample `id.json` or wallet setup instructions
- [ ] Code sign executables (Windows/macOS)
- [ ] Create installer (optional): NSIS (Windows), DMG (macOS), DEB/RPM (Linux)

---

## Notes

### Security Considerations
- The executable will still contain the Python bytecode
- Sensitive data (private keys) should never be hardcoded
- Consider encrypting sensitive resources
- Users should provide their own wallet credentials

### Updates
- Consider implementing auto-update functionality
- Or provide update instructions for users
- Version numbering in About dialog

### Support
For issues with building executables, check:
1. PyInstaller documentation: https://pyinstaller.org/
2. PyQt5 packaging guide
3. Platform-specific packaging guidelines


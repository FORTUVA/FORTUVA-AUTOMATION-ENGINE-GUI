# Building Executables - Quick Start Guide

This guide shows you how to create standalone executable files for Fortuva Bot that work on Windows, macOS, and Linux.

## 🚀 Quick Start

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build for Your Platform

Choose the command for your operating system:

#### Windows
```bash
python build_scripts/build_windows.py
```
**Output:** `dist/FortuvaBot/FortuvaBot.exe`

#### macOS
```bash
python build_scripts/build_macos.py
```
**Output:** `dist/FortuvaBot.app`

#### Linux
```bash
python build_scripts/build_linux.py
```
**Output:** `dist/FortuvaBot/FortuvaBot`

**Or use the universal script** (auto-detects your OS):
```bash
python build_scripts/build_all.py
```

---

## 📦 What You Get

### Windows
- **One-folder distribution** in `dist/FortuvaBot/`
- Main executable: `FortuvaBot.exe`
- Required DLLs and resources included
- Users can run directly without Python installed
- Size: ~50-100 MB

### macOS
- **Application bundle**: `FortuvaBot.app`
- Can be dragged to Applications folder
- Users can double-click to run
- May need code signing to avoid Gatekeeper warnings
- Size: ~60-120 MB

### Linux
- **Standalone binary** in `dist/FortuvaBot/`
- Includes all dependencies
- Users may need to `chmod +x FortuvaBot`
- Create an AppImage for better compatibility (see below)
- Size: ~50-100 MB

---

## 🐧 Linux AppImage (Recommended)

AppImages work across most Linux distributions (Ubuntu, Fedora, Debian, etc.)

### Build AppImage:
```bash
# First, build the Linux executable
python build_scripts/build_linux.py

# Then create AppImage
python build_scripts/build_appimage.py
```

**Output:** `dist/FortuvaBot-x86_64.AppImage`

### Distribute:
- Single file that works everywhere
- No installation required
- Users just need: `chmod +x FortuvaBot-x86_64.AppImage && ./FortuvaBot-x86_64.AppImage`

---

## 📋 Build Requirements

Before building, ensure you have:

1. **Python 3.8+** installed
2. **All dependencies** from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. **PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

---

## 🎯 Distribution Tips

### Windows
1. **Zip the folder**: Compress `dist/FortuvaBot/` folder
2. **Create installer** (optional): Use NSIS or Inno Setup
3. **Code signing** (optional): Sign with Microsoft Authenticode to avoid SmartScreen warnings

### macOS
1. **Test the app**: Open `FortuvaBot.app` to verify it works
2. **Create DMG** (optional):
   ```bash
   hdiutil create -volname FortuvaBot -srcfolder dist/FortuvaBot.app -ov -format UDZO dist/FortuvaBot.dmg
   ```
3. **Code sign** (optional but recommended):
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/FortuvaBot.app
   ```

### Linux
1. **AppImage**: Best for general distribution
2. **TAR/ZIP**: For binary distribution
3. **DEB/RPM** (advanced): For package managers

---

## 🔧 Troubleshooting

### "ModuleNotFoundError" when running executable

The executable is missing a dependency. Edit the appropriate `.spec` file and add to `hiddenimports`:

```python
hiddenimports=[
    'PyQt5',
    'solana',
    'anchorpy',
    'your_missing_module',  # Add here
],
```

Then rebuild.

### Windows: "Failed to execute script"

- Antivirus may be blocking it (false positive)
- Try one-folder mode instead of one-file
- Check that all resource files are included in `datas`

### macOS: "App is damaged and can't be opened"

The app is not code-signed. Users can bypass:
1. Right-click on app → Open
2. Click "Open" in the dialog
3. Or run: `xattr -cr FortuvaBot.app`

### Linux: "error while loading shared libraries"

The system is missing Qt5 libraries. User should install:
```bash
# Ubuntu/Debian
sudo apt install libqt5widgets5 libqt5gui5 libqt5core5a

# Fedora
sudo dnf install qt5-qtbase qt5-qtbase-gui

# Or use AppImage (includes everything)
```

### Executable size is too large

PyInstaller includes the Python runtime and all dependencies. To reduce size:

1. **Use UPX compression** (if available):
   ```bash
   # Install UPX first
   pyinstaller --upx-dir=/path/to/upx ...
   ```

2. **Exclude unused modules** in `.spec` file:
   ```python
   excludes=['tkinter', 'matplotlib', 'numpy'],
   ```

3. **Use virtual environment** with only required packages

---

## 🔍 Verify Your Build

Before distributing, test on a **clean machine** without Python installed:

### Checklist:
- [ ] Application launches without errors
- [ ] All UI elements display correctly
- [ ] Icons and images load properly
- [ ] Can load/save settings
- [ ] Can connect to RPC and blockchain
- [ ] Wallet import works
- [ ] Betting functionality works
- [ ] Logs display correctly

---

## 📚 Additional Resources

### PyInstaller Documentation
- Official docs: https://pyinstaller.org/
- Spec files: https://pyinstaller.org/en/stable/spec-files.html
- Hooks: https://pyinstaller.org/en/stable/hooks.html

### Platform-Specific Packaging
- **Windows**: [NSIS](https://nsis.sourceforge.io/), [Inno Setup](https://jrsoftware.org/isinfo.php)
- **macOS**: [DMG Canvas](https://www.araelium.com/dmgcanvas), [create-dmg](https://github.com/create-dmg/create-dmg)
- **Linux**: [AppImage](https://appimage.org/), [FPM](https://github.com/jordansissel/fpm)

### Code Signing
- **Windows**: [SignTool](https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool)
- **macOS**: [codesign](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

---

## 💡 Pro Tips

1. **Version your builds**: Update version numbers in the code and spec files
2. **Test thoroughly**: Always test on a clean machine
3. **Include README**: Add user documentation in the distribution
4. **Auto-updates**: Consider implementing update checking
5. **Crash reporting**: Add error logging for debugging user issues
6. **Keep backups**: Save your build environments and dependencies list

---

## 🆘 Still Having Issues?

1. Check the detailed guide: `build_executable.md`
2. Review PyInstaller documentation
3. Search for error messages on Stack Overflow
4. Check if your issue is specific to certain modules (Qt, blockchain libs, etc.)

---

## 📄 License

Make sure to comply with:
- Your project's license
- PyQt5 license (GPL or commercial)
- All dependency licenses
- Include license files in distributions

---

**Happy Building! 🎉**

If you successfully build executables, consider sharing your distribution for others to use!


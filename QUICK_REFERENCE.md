# Quick Reference - Building Executables

## 🎯 TL;DR

```bash
pip install pyinstaller
python build_scripts/build_all.py
```

Done! ✅

---

## 📦 Platform-Specific Commands

| Platform | Command | Output |
|----------|---------|--------|
| **Windows** | `python build_scripts/build_windows.py` | `dist/FortuvaBot/FortuvaBot.exe` |
| **macOS** | `python build_scripts/build_macos.py` | `dist/FortuvaBot.app` |
| **Linux** | `python build_scripts/build_linux.py` | `dist/FortuvaBot/FortuvaBot` |
| **Linux AppImage** | `python build_scripts/build_appimage.py` | `dist/FortuvaBot-x86_64.AppImage` |
| **Auto-detect** | `python build_scripts/build_all.py` | Platform-specific |

---

## ⚡ Quick Fixes

### Build Failed

```bash
# Check PyInstaller
pip install --upgrade pyinstaller

# Clean and rebuild
rm -rf build dist
python build_scripts/build_all.py
```

### Missing Module

Edit `FortuvaBot.spec` (or platform-specific .spec):
```python
hiddenimports=['your_missing_module'],
```

### Executable Won't Run

**Windows**: Right-click → Properties → Unblock
**macOS**: `xattr -cr FortuvaBot.app`
**Linux**: `chmod +x FortuvaBot`

---

## 📋 Files You Need

### Before Building
- ✅ `requirements.txt` - Install: `pip install -r requirements.txt`
- ✅ `pyinstaller` - Install: `pip install pyinstaller`

### Build Files (Included)
- ✅ `FortuvaBot.spec` - Windows config
- ✅ `FortuvaBot-mac.spec` - macOS config
- ✅ `FortuvaBot-linux.spec` - Linux config
- ✅ `build_scripts/*.py` - Build automation

### Output (After Building)
- 📦 `dist/` - Your executables
- 🗑️ `build/` - Temporary (can delete)

---

## 🚀 Distribution Checklist

- [ ] Build executable
- [ ] Test on clean machine (no Python)
- [ ] Include README for users
- [ ] Add LICENSE file
- [ ] (Optional) Code sign
- [ ] Create installer/DMG/AppImage
- [ ] Test on multiple OS versions
- [ ] Upload and share!

---

## 🔍 Troubleshooting Matrix

| Problem | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Won't run | Check antivirus | Right-click Open | chmod +x |
| Missing DLL/lib | Use one-folder | Include in bundle | Use AppImage |
| Size too large | Use UPX | Strip symbols | Strip + UPX |
| Code signing | Authenticode | codesign | Not needed |

---

## 💡 Pro Tips

1. **Virtual environment**: Build in clean venv for smaller size
2. **Test first**: Always test before distributing
3. **Version control**: Keep .spec files in git
4. **Automate**: Use CI/CD for releases
5. **Document**: Note any custom changes

---

## 📚 Full Documentation

- [Quick Start](BUILDING_EXECUTABLES.md) - User-friendly guide
- [Detailed Guide](build_executable.md) - In-depth instructions
- [Build Workflow](BUILD_WORKFLOW.md) - Visual workflow diagrams
- [Build Scripts](build_scripts/README.md) - Script documentation

---

## 🆘 Emergency Commands

```bash
# Nuclear option - clean everything and start fresh
rm -rf build dist __pycache__ *.spec
pip uninstall pyinstaller -y
pip install pyinstaller
python -m PyInstaller --onefile --windowed main.py
```

---

## ⚙️ Common Customizations

### Change App Name
Edit .spec file:
```python
name='YourAppName',
```

### Change Icon
Edit .spec file:
```python
icon='path/to/icon.ico',  # Windows
icon='path/to/icon.icns', # macOS
```

### Exclude Large Modules
Edit .spec file:
```python
excludes=['tkinter', 'matplotlib', 'numpy'],
```

### One-File Mode (Windows)
Edit .spec file:
```python
# Change from COLLECT to single EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Add these
    a.zipfiles,  # Add these
    a.datas,     # Add these
    [],
    name='FortuvaBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True,  # Add this
)
# Remove COLLECT block
```

---

## 📞 Quick Links

- PyInstaller Docs: https://pyinstaller.org/
- Python: https://www.python.org/
- PyQt5: https://www.riverbankcomputing.com/software/pyqt/

---

**Remember**: Most builds take 3-5 minutes. Be patient! ⏱️


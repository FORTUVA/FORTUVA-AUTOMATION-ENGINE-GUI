# Build Workflow Diagram

## Simple 3-Step Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    Step 1: Install PyInstaller                   │
│                                                                   │
│                  pip install pyinstaller                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Step 2: Run Build Script                       │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Windows    │    │    macOS     │    │    Linux     │      │
│  │              │    │              │    │              │      │
│  │  build_      │    │  build_      │    │  build_      │      │
│  │  windows.py  │    │  macos.py    │    │  linux.py    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                              │                                    │
│                              │                                    │
│                    ┌─────────────────┐                           │
│                    │  OR Use:        │                           │
│                    │  build_all.py   │                           │
│                    │  (auto-detects) │                           │
│                    └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Step 3: Get Your Executable                    │
│                                                                   │
│  Windows:    dist/FortuvaEngine/FortuvaEngine.exe                      │
│  macOS:      dist/FortuvaEngine.app                                  │
│  Linux:      dist/FortuvaEngine/FortuvaEngine                          │
│              dist/FortuvaEngine-x86_64.AppImage (if built)          │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Workflow

### For Windows Users

```
Start
  │
  ├─→ Install Python 3.8+
  │
  ├─→ Install Dependencies
  │   pip install -r requirements.txt
  │   pip install pyinstaller
  │
  ├─→ Run Build
  │   python build_scripts\build_windows.py
  │
  ├─→ Build Process
  │   ├─ Clean old builds
  │   ├─ Analyze dependencies
  │   ├─ Collect resources
  │   ├─ Bundle everything
  │   └─ Create .exe
  │
  └─→ Output
      dist\FortuvaEngine\FortuvaEngine.exe
      └─ Distribute entire FortuvaEngine folder
```

### For macOS Users

```
Start
  │
  ├─→ Install Python 3.8+
  │
  ├─→ Install Dependencies
  │   pip install -r requirements.txt
  │   pip install pyinstaller
  │
  ├─→ Run Build
  │   python build_scripts/build_macos.py
  │
  ├─→ Build Process
  │   ├─ Clean old builds
  │   ├─ Analyze dependencies
  │   ├─ Create app bundle
  │   ├─ Bundle resources
  │   └─ Generate .app
  │
  ├─→ (Optional) Code Sign
  │   codesign --deep --force --sign "..." FortuvaEngine.app
  │
  ├─→ (Optional) Create DMG
  │   hdiutil create -volname FortuvaEngine -srcfolder dist/FortuvaEngine.app ...
  │
  └─→ Output
      dist/FortuvaEngine.app
      └─ Distribute .app or .dmg
```

### For Linux Users

```
Start
  │
  ├─→ Install Python 3.8+
  │
  ├─→ Install Dependencies
  │   pip install -r requirements.txt
  │   pip install pyinstaller
  │
  ├─→ Build Binary
  │   python build_scripts/build_linux.py
  │   └─→ Output: dist/FortuvaEngine/FortuvaEngine
  │
  ├─→ (Recommended) Build AppImage
  │   python build_scripts/build_appimage.py
  │   │
  │   ├─ Download appimagetool
  │   ├─ Create AppDir structure
  │   ├─ Bundle executable + deps
  │   ├─ Add desktop file & icon
  │   └─ Generate AppImage
  │
  └─→ Output
      ├─ dist/FortuvaEngine/FortuvaEngine (binary)
      └─ dist/FortuvaEngine-x86_64.AppImage (universal)
```

## Cross-Platform Build Matrix

| Build On  | Target Windows | Target macOS | Target Linux |
|-----------|----------------|--------------|--------------|
| Windows   | ✅ Native      | ❌ No        | ⚠️ Docker    |
| macOS     | ⚠️ Docker      | ✅ Native    | ⚠️ Docker    |
| Linux     | ⚠️ Docker      | ❌ No*       | ✅ Native    |

✅ = Native support (recommended)
⚠️ = Possible via Docker/Wine (limited)
❌ = Not supported
\* = macOS apps should only be built on macOS

## Build Time Estimates

| Platform | Build Time | Output Size |
|----------|------------|-------------|
| Windows  | 3-5 min    | 50-100 MB   |
| macOS    | 3-7 min    | 60-120 MB   |
| Linux    | 3-5 min    | 50-100 MB   |
| AppImage | +2-3 min   | 60-130 MB   |

*Times vary based on hardware and dependencies*

## Distribution Workflow

```
┌──────────────┐
│ Build        │
│ Executable   │
└──────┬───────┘
       │
       ├─→ Windows
       │   ├─ Test on clean Windows machine
       │   ├─ (Optional) Code sign with Authenticode
       │   ├─ Zip FortuvaEngine folder
       │   └─ OR Create installer with NSIS/Inno Setup
       │
       ├─→ macOS
       │   ├─ Test on clean Mac
       │   ├─ (Recommended) Code sign
       │   ├─ Create DMG
       │   └─ (Optional) Notarize with Apple
       │
       └─→ Linux
           ├─ Test on target distributions
           ├─ Create AppImage (recommended)
           ├─ OR Tar/zip binary folder
           └─ OR Create DEB/RPM packages
```

## Troubleshooting Decision Tree

```
Build Failed?
    │
    ├─→ Missing Module?
    │   └─→ Add to hiddenimports in .spec file
    │
    ├─→ Permission Error?
    │   └─→ Check antivirus / Run as admin
    │
    ├─→ Resource Not Found?
    │   └─→ Check datas parameter in .spec file
    │
    └─→ Other Error?
        └─→ Check PyInstaller docs / Search error

Executable Doesn't Run?
    │
    ├─→ Windows
    │   ├─→ Antivirus blocking? Add exception
    │   └─→ DLL missing? Use one-folder mode
    │
    ├─→ macOS
    │   ├─→ "Damaged" error? Right-click → Open
    │   └─→ OR: xattr -cr FortuvaEngine.app
    │
    └─→ Linux
        ├─→ Missing libraries? Use AppImage
        └─→ Not executable? chmod +x FortuvaEngine
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Executables

on: [push, release]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: python build_scripts/build_windows.py
      - uses: actions/upload-artifact@v3
        with:
          name: windows-build
          path: dist/FortuvaEngine/

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: python build_scripts/build_macos.py
      - uses: actions/upload-artifact@v3
        with:
          name: macos-build
          path: dist/FortuvaEngine.app/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt pyinstaller
          sudo apt-get install -y libxcb-xinerama0
      - run: python build_scripts/build_linux.py
      - run: python build_scripts/build_appimage.py
      - uses: actions/upload-artifact@v3
        with:
          name: linux-build
          path: |
            dist/FortuvaEngine/
            dist/FortuvaEngine-x86_64.AppImage
```

## Quick Reference Commands

```bash
# Install build tools
pip install pyinstaller

# Auto-detect and build
python build_scripts/build_all.py

# Platform-specific builds
python build_scripts/build_windows.py    # Windows
python build_scripts/build_macos.py      # macOS
python build_scripts/build_linux.py      # Linux
python build_scripts/build_appimage.py   # Linux AppImage

# Manual PyInstaller (if needed)
pyinstaller --clean FortuvaEngine.spec           # Windows
pyinstaller --clean FortuvaEngine-mac.spec       # macOS
pyinstaller --clean FortuvaEngine-linux.spec     # Linux

# Test executable
cd dist/FortuvaEngine
./FortuvaEngine  # Linux/macOS
FortuvaEngine.exe  # Windows

# Distribution
zip -r FortuvaEngine-Windows.zip FortuvaEngine/              # Windows/Linux
hdiutil create -volname FortuvaEngine -srcfolder \
  FortuvaEngine.app -ov -format UDZO FortuvaEngine.dmg      # macOS
```

## Tips for Success

1. ✅ **Always test on clean machine** (without Python)
2. ✅ **Use virtual environment** for clean dependencies
3. ✅ **Code sign executables** for production
4. ✅ **Include README** with user instructions
5. ✅ **Version your builds** clearly
6. ✅ **Keep build scripts** in version control
7. ✅ **Document any customizations**
8. ✅ **Test all major OS versions**

---

**Remember**: Building executables is a one-time setup. After initial configuration, builds take just a few minutes!


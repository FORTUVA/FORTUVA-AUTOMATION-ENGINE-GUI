# Quick Fix: Linux Issues

## TL;DR - Two Main Issues Fixed

### Issue 1: Qt Platform Plugin Error

**Problem:** `Could not load the Qt platform plugin "xcb"`

**Solution for End Users:**
```bash
# Install system dependencies
sudo apt-get install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxkbcommon-x11-0 libxkbcommon0 libdbus-1-3 \
    libgl1-mesa-glx libglib2.0-0

# Then run
./FortuvaBot
```

**Or use the automated script:**
```bash
chmod +x install_linux_deps.sh
./install_linux_deps.sh
```

### Issue 2: UI Layout - Table Cut Off

**Problem:** "Latest Bets" table cut off at bottom with no scrollbar

**Solution:** Already fixed in the code! Just run the updated version:
```bash
python main.py
```

---

**Solution for Developers (Rebuild):**
```bash
# The build configuration and UI layout have been fixed
# Just rebuild on Linux:
python build_scripts/build_linux.py

# The new build includes:
# - Runtime Qt plugin configuration
# - Bundled Qt platform plugins
# - No strip/UPX (prevents corruption)
# - Fixed table scrollbar and sizing
# - Optimized layout for 825px window height
```

---

## What Was Fixed

### Qt Plugin Fix

1. ✅ Created `pyqt5_hook.py` - runtime Qt configuration
2. ✅ Updated `FortuvaBot-linux.spec` - better Qt plugin handling
3. ✅ Created `install_linux_deps.sh` - automated dependency installer
4. ✅ Fixed table scrollbar visibility and size policies
5. ✅ Reduced table minimum height from 200px to 150px
6. ✅ Reduced logo height from 180px to 160px for better layout
7. ✅ Enhanced scrollbar styling for Linux
8. ✅ Created comprehensive documentation
9. ✅ Updated main README with Linux notes

## Files to Distribute

When distributing your Linux build, include:
```
📦 FortuvaBot-Linux/
├── FortuvaBot                 # The executable
├── README_LINUX_USERS.md      # User guide
└── install_linux_deps.sh      # Dependency installer
```

## Next Steps

1. **Rebuild** on Linux: `python build_scripts/build_linux.py`
2. **Test** on a fresh Linux VM
3. **Distribute** with the user guide and installer script
4. **Users run** `install_linux_deps.sh` before first use

## Documentation

- **[README_LINUX_USERS.md](README_LINUX_USERS.md)** - Give this to end users
- **[LINUX_TROUBLESHOOTING.md](LINUX_TROUBLESHOOTING.md)** - Comprehensive troubleshooting
- **[LINUX_BUILD_FIX.md](LINUX_BUILD_FIX.md)** - Technical details: Qt plugin fix
- **[LINUX_UI_FIX.md](LINUX_UI_FIX.md)** - Technical details: UI layout fix

## Still Not Working?

```bash
# Debug mode
export QT_DEBUG_PLUGINS=1
./FortuvaBot

# Check missing libraries
ldd ./FortuvaBot | grep "not found"

# Try Wayland (if applicable)
export QT_QPA_PLATFORM=wayland
./FortuvaBot
```

See [LINUX_TROUBLESHOOTING.md](LINUX_TROUBLESHOOTING.md) for more solutions.


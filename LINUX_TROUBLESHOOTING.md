# Linux Build Troubleshooting Guide

## Common Issues and Solutions

### 1. Qt Platform Plugin "xcb" Error

**Error Message:**
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized.
```

**Cause:** The xcb platform plugin can't find its system library dependencies.

**Solutions:**

#### Solution A: Install Required System Libraries (Recommended for End Users)

On the target Linux system, install these packages:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libdbus-1-3 \
    libgl1-mesa-glx \
    libglib2.0-0
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install -y \
    xcb-util-wm \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    libxkbcommon-x11 \
    libxkbcommon \
    dbus-libs \
    mesa-libGL \
    glib2
```

**Arch Linux:**
```bash
sudo pacman -S --needed \
    libxcb \
    xcb-util-wm \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    libxkbcommon-x11 \
    dbus \
    mesa \
    glib2
```

#### Solution B: Use Wayland Instead of X11

If you're on a Wayland system, try forcing Wayland:

```bash
export QT_QPA_PLATFORM=wayland
./FortuvaBot
```

#### Solution C: Run with Debug Output

To see more details about what's failing:

```bash
export QT_DEBUG_PLUGINS=1
./FortuvaBot
```

This will show which libraries are missing.

#### Solution D: Rebuild from Source

If the pre-built binary doesn't work on your distribution, rebuild it locally:

```bash
# Clone the repository
git clone <repository-url>
cd modern-login

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-build.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine

# Build
python build_scripts/build_linux.py
```

### 2. Wayland Warning

**Warning Message:**
```
Warning: Ignoring XDG_SESSION_TYPE=wayland on Gnome. Use QT_QPA_PLATFORM=wayland to run on Wayland anyway.
```

**Solution:** This is just a warning and shouldn't prevent the app from running. The app will fall back to X11. If you want to use Wayland explicitly:

```bash
export QT_QPA_PLATFORM=wayland
./FortuvaBot
```

### 3. "Aborted (core dumped)"

**Cause:** The application crashed during startup, usually due to missing dependencies.

**Solutions:**
1. Check if all system libraries are installed (see Solution A above)
2. Try running with `QT_DEBUG_PLUGINS=1` to see what's failing
3. Check if your system has X11 or Wayland running
4. Try running the app in console mode to see Python errors:
   ```bash
   # Edit the spec file and set console=True, then rebuild
   ```

### 4. Distribution Compatibility Issues

**Problem:** Binary built on one distribution doesn't work on another.

**Cause:** Different Linux distributions have different glibc versions and library locations.

**Solutions:**

#### Option 1: Build on the Oldest Supported Distribution
Build on the oldest distribution you want to support (e.g., Ubuntu 20.04) and it should work on newer versions.

#### Option 2: Use AppImage
AppImage bundles more dependencies and is more portable:

```bash
python build_scripts/build_appimage.py
```

#### Option 3: Use Docker for Building
Build in a controlled environment:

```bash
# Use an Ubuntu 20.04 container
docker run -it --rm \
    -v $(pwd):/workspace \
    ubuntu:20.04 \
    bash -c "
        apt-get update && \
        apt-get install -y python3 python3-pip && \
        cd /workspace && \
        pip3 install -r requirements-build.txt && \
        python3 build_scripts/build_linux.py
    "
```

### 5. Missing Icons or Resources

**Cause:** Resources weren't properly bundled.

**Solution:** Check that the spec file includes:
```python
datas=[
    ('icons', 'icons'),
    ('img', 'img'),
    ('icons_rc.py', '.'),
    ('bot', 'bot'),
]
```

### 6. Permission Denied

**Error:** `bash: ./FortuvaBot: Permission denied`

**Solution:** Make the file executable:
```bash
chmod +x ./FortuvaBot
```

## Testing Your Build

After building, test on a clean system or VM:

1. **Create a test VM** with your target distribution
2. **Copy only the executable** (don't include Python or project files)
3. **Install system dependencies** (see Solution A)
4. **Run the executable**

## Build Configuration Changes (Already Applied)

The spec file has been updated with:

1. **Runtime hook** (`pyqt5_hook.py`) that sets Qt plugin paths
2. **Explicit Qt plugin inclusion** - bundles platform plugins
3. **Disabled strip/UPX** - prevents Qt library corruption
4. **Added PyQt5.QtDBus** - required for some Linux desktop integrations

## Reporting Issues

If you're still having problems, provide:

1. Linux distribution and version: `cat /etc/os-release`
2. Qt version: `python -c "from PyQt5.QtCore import QT_VERSION_STR; print(QT_VERSION_STR)"`
3. Python version: `python --version`
4. Output of: `QT_DEBUG_PLUGINS=1 ./FortuvaBot`
5. Output of: `ldd ./FortuvaBot` (shows library dependencies)

## Alternative: Running Without Building

If building is problematic, users can run the Python script directly:

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python main.py
```

This requires Python and the dependencies to be installed but avoids bundling issues.


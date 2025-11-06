# FortuvaEngine - Linux Installation Guide

## Quick Start

### 1. Install Required System Libraries

Before running FortuvaEngine, you need to install some system libraries for the graphical interface.

**Ubuntu/Debian/Linux Mint:**
```bash
sudo apt-get update
sudo apt-get install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 \
    libxcb-xfixes0 libxcb-xkb1 libxkbcommon-x11-0 libxkbcommon0 \
    libdbus-1-3 libgl1-mesa-glx libglib2.0-0
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install -y xcb-util-wm xcb-util-image xcb-util-keysyms \
    xcb-util-renderutil libxkbcommon-x11 libxkbcommon dbus-libs \
    mesa-libGL glib2
```

**Arch Linux/Manjaro:**
```bash
sudo pacman -S --needed libxcb xcb-util-wm xcb-util-image \
    xcb-util-keysyms xcb-util-renderutil libxkbcommon-x11 \
    dbus mesa glib2
```

### 2. Make the Executable Runnable

```bash
chmod +x FortuvaEngine
```

### 3. Run FortuvaEngine

```bash
./FortuvaEngine
```

## Troubleshooting

### Error: "Could not load the Qt platform plugin 'xcb'"

This means you're missing system libraries. Make sure you ran the installation command for your distribution (see step 1 above).

You can also try:
```bash
# See detailed plugin debug info
export QT_DEBUG_PLUGINS=1
./FortuvaEngine

# Or try Wayland (if you use Wayland)
export QT_QPA_PLATFORM=wayland
./FortuvaEngine
```

### Error: "Permission denied"

Make the file executable:
```bash
chmod +x FortuvaEngine
```

### Error: "No such file or directory"

Make sure you're in the same directory as the FortuvaEngine executable:
```bash
cd /path/to/FortuvaEngine/directory
./FortuvaEngine
```

### Still Having Issues?

1. Check if you're running X11 or Wayland:
   ```bash
   echo $XDG_SESSION_TYPE
   ```

2. Verify all required libraries are installed:
   ```bash
   ldd FortuvaEngine | grep "not found"
   ```
   If you see "not found", those libraries need to be installed.

3. Try running from terminal to see error messages:
   ```bash
   ./FortuvaEngine
   ```

## System Requirements

- **OS:** Linux (any modern distribution)
- **Display Server:** X11 or Wayland
- **RAM:** 512 MB minimum
- **Disk Space:** 200 MB
- **Internet:** Required for blockchain operations

## Tested Distributions

- Ubuntu 20.04, 22.04, 24.04
- Debian 11, 12
- Fedora 38, 39, 40
- Arch Linux (rolling)
- Linux Mint 21, 22

The application should work on any modern Linux distribution after installing the required system libraries.

## Running on Different Distributions

If FortuvaEngine doesn't work on your distribution:

1. Make sure all system libraries are installed (see step 1)
2. Check if your distribution uses an older glibc version
3. Consider running from source code:
   ```bash
   # Install Python and dependencies
   sudo apt-get install python3 python3-pip python3-pyqt5
   pip3 install -r requirements.txt
   
   # Run directly
   python3 main.py
   ```

## Security Notes

- FortuvaEngine requires internet access to interact with the Solana blockchain
- Your wallet private keys are stored locally and encrypted
- Always verify you're running the official version from the official repository

## Support

For issues specific to the Linux build, see the full troubleshooting guide in `LINUX_TROUBLESHOOTING.md`.

For general support and bug reports, visit: [Project Repository]

## License

See LICENSE file for details.


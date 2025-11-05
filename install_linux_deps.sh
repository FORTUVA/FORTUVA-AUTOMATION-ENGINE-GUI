#!/bin/bash
# FortuvaBot - Linux Dependency Installer
# This script automatically detects your Linux distribution and installs required system libraries

set -e

echo "========================================"
echo "FortuvaBot - Linux Dependency Installer"
echo "========================================"
echo ""

# Detect the Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
    echo "Detected: $NAME $VERSION"
else
    echo "❌ Cannot detect Linux distribution"
    echo "   Please install dependencies manually"
    echo "   See README_LINUX_USERS.md for instructions"
    exit 1
fi

echo ""
echo "Installing required Qt/X11 system libraries..."
echo ""

# Install based on distribution
case "$DISTRO" in
    ubuntu|debian|linuxmint|pop)
        echo "Using apt package manager..."
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
        ;;
    
    fedora|rhel|centos|rocky|alma)
        echo "Using dnf package manager..."
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
        ;;
    
    arch|manjaro|endeavouros)
        echo "Using pacman package manager..."
        sudo pacman -S --needed --noconfirm \
            libxcb \
            xcb-util-wm \
            xcb-util-image \
            xcb-util-keysyms \
            xcb-util-renderutil \
            libxkbcommon-x11 \
            dbus \
            mesa \
            glib2
        ;;
    
    opensuse*|suse)
        echo "Using zypper package manager..."
        sudo zypper install -y \
            libxcb1 \
            libxcb-xinerama0 \
            libxcb-icccm4 \
            libxcb-image0 \
            libxcb-keysyms1 \
            libxkbcommon-x11-0 \
            libxkbcommon0 \
            libdbus-1-3 \
            Mesa-libGL1 \
            glib2
        ;;
    
    *)
        echo "❌ Unsupported distribution: $DISTRO"
        echo ""
        echo "Please install the following packages manually:"
        echo "  - libxcb and xcb-util libraries"
        echo "  - libxkbcommon and libxkbcommon-x11"
        echo "  - dbus libraries"
        echo "  - OpenGL/Mesa libraries"
        echo "  - glib2"
        echo ""
        echo "See README_LINUX_USERS.md for distribution-specific commands"
        exit 1
        ;;
esac

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "You can now run FortuvaBot:"
echo "  ./FortuvaBot"
echo ""
echo "If you still encounter issues, see LINUX_TROUBLESHOOTING.md"


#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
MIN_PYTHON="3.10"

# ──────────────────────────────────────────────
# Detect Linux distribution
# ──────────────────────────────────────────────
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID" "$VERSION_ID"
    elif command -v lsb_release &>/dev/null; then
        echo "$(lsb_release -is | tr '[:upper:]' '[:lower:]')" "$(lsb_release -rs)"
    else
        echo "unknown" "0"
    fi
}

read -r DISTRO VERSION < <(detect_distro)
echo "Detected: $DISTRO $VERSION"
echo ""

# ──────────────────────────────────────────────
# Install system dependencies per distro
# ──────────────────────────────────────────────
install_system_deps() {
    local PYTHON_BUILD_DEPS="make build-essential libssl-dev zlib1g-dev
        libbz2-dev libreadline-dev libsqlite3-dev wget curl
        libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev"

    local QT_DEPS="libxcb-cursor0 libxcb-xinerama0 libxcb-icccm4
        libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0
        libxcb-shape0 libxcb-xfixes0 libxcb-xkb1 libxkbcommon-x11-0
        libgl1-mesa-glx libegl1 libfontconfig1"

    case "$DISTRO" in
        ubuntu|debian|linuxmint|pop)
            echo "Installing system dependencies for apt-based system..."
            sudo apt update
            sudo apt install -y $PYTHON_BUILD_DEPS $QT_DEPS 2>/dev/null || \
            sudo apt install -y $PYTHON_BUILD_DEPS  # fallback: Qt deps may vary by version
            # Qt fix for older Ubuntu
            sudo apt install -y libxcb-cursor-dev 2>/dev/null || true
            ;;
        fedora|centos|rhel)
            echo "Installing system dependencies for dnf-based system..."
            sudo dnf groupinstall -y "Development Tools"
            sudo dnf install -y openssl-devel bzip2-devel libffi-devel \
                readline-devel sqlite-devel wget curl tk-devel \
                xz-devel zlib-devel libxcb-devel xcb-util-wm-devel \
                xcb-util-image-devel xcb-util-keysyms-devel \
                xcb-util-renderutil-devel mesa-libGL-devel
            ;;
        opensuse*|suse)
            echo "Installing system dependencies for zypper-based system..."
            sudo zypper install -y -t pattern devel_basis
            sudo zypper install -y openssl-devel bzip2-devel libffi-devel \
                readline-devel sqlite3-devel wget curl tk-devel \
                xz-devel zlib-devel libxcb-devel Mesa-libGL-devel
            ;;
        arch|manjaro)
            echo "Installing system dependencies for pacman-based system..."
            sudo pacman -Sy --noconfirm base-devel openssl bzip2 libffi \
                readline sqlite wget curl tk xz zlib libxcb mesa
            ;;
        *)
            echo "Warning: Unknown distro '$DISTRO'. Attempting apt as fallback..."
            sudo apt update 2>/dev/null && sudo apt install -y $PYTHON_BUILD_DEPS || true
            ;;
    esac
}

install_system_deps

# ──────────────────────────────────────────────
# Find or install Python 3.10+
# ──────────────────────────────────────────────
find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            if printf '%s\n' "$MIN_PYTHON" "$ver" | sort -V | head -1 | grep -q "^$MIN_PYTHON$"; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

install_pyenv_python() {
    echo "No Python $MIN_PYTHON+ found. Installing via pyenv..."
    if [ ! -w "$DIR" ]; then
        echo "ERROR: No write permission in $DIR"
        echo "Fix: sudo chown -R $(whoami):$(whoami) \"$DIR\""
        exit 1
    fi
    if ! command -v pyenv &>/dev/null; then
        [ -d "$HOME/.pyenv" ] && rm -rf "$HOME/.pyenv"
        curl https://pyenv.run | bash
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init - bash)"
    fi
    echo "Compiling Python 3.12.7 (this takes 3-10 minutes)..."
    pyenv install 3.12.7 -s
    pyenv local 3.12.7
    echo "Python: $(python --version)"
}

PYTHON=$(find_python) || {
    install_pyenv_python
    PYTHON=$(find_python) || {
        echo "Error: could not install Python $MIN_PYTHON+."
        echo "Run: pyenv install 3.12.7 && pyenv local 3.12.7"
        exit 1
    }
}

echo "Using: $($PYTHON --version)"

# ──────────────────────────────────────────────
# Create virtual environment
# ──────────────────────────────────────────────
if ! "$PYTHON" -c "import ensurepip" &>/dev/null; then
    PYVER=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "ensurepip not available. Installing python$PYVER-venv..."
    sudo apt install -y "python$PYVER-venv" 2>/dev/null || \
    sudo apt install -y python3-venv 2>/dev/null || {
        "$PYTHON" -m venv venv --without-pip
        source venv/bin/activate
        curl -sS "https://bootstrap.pypa.io/pip/$PYVER/get-pip.py" -o get-pip.py
        "$PYTHON" get-pip.py
        rm -f get-pip.py
    }
fi

if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip -q

# ──────────────────────────────────────────────
# Install Python packages
# ──────────────────────────────────────────────
echo "Installing Python dependencies..."
pip install -r requirements.txt

# ──────────────────────────────────────────────
# Final verification
# ──────────────────────────────────────────────
echo ""
echo "Verifying installation..."
PYTHON_OK=$(python -c "import PySide6; print(f'PySide6 {PySide6.__version__}')" 2>&1)
PYMODBUS_OK=$(python -c "import pymodbus; print(f'pymodbus {pymodbus.__version__}')" 2>&1)
SERIAL_OK=$(python -c "import serial; print(f'pyserial {serial.__version__}')" 2>&1)
echo "  $PYTHON_OK"
echo "  $PYMODBUS_OK"
echo "  $SERIAL_OK"

# Check Qt platform plugin loads (non-fatal, just a warning)
QT_XCB_OK=$(python -c "
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
from PySide6.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)
app.quit()
print('OK')
" 2>&1) || QT_XCB_OK="FAILED"
if [ "$QT_XCB_OK" != "OK" ]; then
    echo "  [!] Qt xcb plugin check: $QT_XCB_OK"
    echo "      The app may need a display (X11/Wayland)."
    echo "      If you see 'xcb-cursor0' errors, run:"
    echo "        sudo apt install libxcb-cursor0"
else
    echo "  Qt xcb platform plugin: OK"
fi

if echo "$PYTHON_OK" | grep -q "^PySide6" && \
   echo "$PYMODBUS_OK" | grep -q "^pymodbus" && \
   echo "$SERIAL_OK" | grep -q "^pyserial"; then
    echo ""
    echo "========================================="
    echo "Installation complete!"
    echo "Run:  ./run.sh"
    echo "========================================="
else
    echo ""
    echo "ERROR: Some checks failed."
    echo "Try:  pip install -r requirements.txt"
    [ -d venv ] && rm -rf venv
    exit 1
fi

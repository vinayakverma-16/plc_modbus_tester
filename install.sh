#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PYTHON="${PYTHON:-python3}"

echo "Checking Python..."
if ! command -v "$PYTHON" &>/dev/null; then
    echo "Python not found. Please install Python 3.12+ first."
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYVER=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $PYVER"

if ! "$PYTHON" -c "import ensurepip" &>/dev/null; then
    echo "ensurepip not available. Installing python${PYVER}-venv..."
    if command -v apt &>/dev/null; then
        sudo apt install -y "python${PYVER}-venv" 2>/dev/null || \
        sudo apt install -y python3-venv 2>/dev/null || {
            echo "Could not install python3-venv. Using --without-pip fallback..."
            "$PYTHON" -m venv venv --without-pip
            source venv/bin/activate
            curl -sS https://bootstrap.pypa.io/get-pip.py | python
        }
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-virtualenv
        "$PYTHON" -m venv venv
    else
        echo "Please install python3-venv for your distribution, then re-run."
        exit 1
    fi
fi

if [ ! -d venv ]; then
    echo "Creating Python virtual environment..."
    "$PYTHON" -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Installation complete!"
echo "Run the application with:"
echo "  ./run.sh"
echo "  OR"
echo "  source venv/bin/activate && python main.py"
echo "========================================="

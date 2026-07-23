#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

MIN_PYTHON="3.10"

find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            PYVER=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            if printf '%s\n' "$MIN_PYTHON" "$PYVER" | sort -V | head -1 | grep -q "^$MIN_PYTHON$"; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

install_pyenv_python() {
    echo "No Python $MIN_PYTHON+ found on this system."

    if ! command -v pyenv &>/dev/null; then
        echo "Installing pyenv..."
        sudo apt install -y make build-essential libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev wget curl \
            libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
        curl https://pyenv.run | bash
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"
    fi

    echo "Installing Python 3.12.7 via pyenv (this compiles from source, may take a few minutes)..."
    pyenv install 3.12.7 -s
    pyenv local 3.12.7
    echo "pyenv Python: $(python --version)"
    echo "$(which python)"
}

PYTHON=$(find_python) || {
    install_pyenv_python
    PYTHON=$(find_python) || {
        echo "Error: could not find or install Python $MIN_PYTHON+."
        echo "Manually run: pyenv install 3.12.7 && pyenv local 3.12.7"
        exit 1
    }
}

echo "Using: $($PYTHON --version)"

if ! "$PYTHON" -c "import ensurepip" &>/dev/null; then
    PYVER=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "ensurepip not available. Installing python$PYVER-venv..."
    if command -v apt &>/dev/null; then
        sudo apt install -y "python$PYVER-venv" 2>/dev/null || \
        sudo apt install -y python3-venv 2>/dev/null || {
            echo "Could not install python3-venv. Using --without-pip fallback..."
            "$PYTHON" -m venv venv --without-pip
            source venv/bin/activate
            PIP_URL="https://bootstrap.pypa.io/pip/$PYVER/get-pip.py"
            curl -sS "$PIP_URL" -o get-pip.py
            "$PYTHON" get-pip.py
            rm -f get-pip.py
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

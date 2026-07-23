#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ ! -d venv ]; then
    echo "Virtual environment not found. Run install.sh first."
    exit 1
fi

source venv/bin/activate

if ! python -c "import PySide6" 2>/dev/null; then
    echo "Dependencies not installed. Run install.sh first."
    exit 1
fi

exec python main.py "$@"

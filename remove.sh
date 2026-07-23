#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "PLC Test Utility - Cleanup"
echo "=========================="
echo ""

confirm() {
    read -r -p "$1 (y/N) " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

if confirm "Remove virtual environment (venv/)?"; then
    rm -rf venv
    echo "  Removed venv/"
fi

if confirm "Remove Python cache files (__pycache__, *.pyc)?"; then
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    echo "  Removed Python cache files"
fi

if confirm "Remove session data (sessions/)?"; then
    rm -rf sessions
    echo "  Removed sessions/"
fi

if confirm "Remove PLC profiles (profiles/)?"; then
    rm -rf profiles
    echo "  Removed profiles/"
fi

if confirm "Remove log files (logs/)?"; then
    rm -rf logs
    echo "  Removed logs/"
fi

if confirm "Remove test cache (.pytest_cache)?"; then
    rm -rf .pytest_cache
    echo "  Removed .pytest_cache"
fi

if confirm "Remove pyenv local version (.python-version)?"; then
    rm -f .python-version
    echo "  Removed .python-version"
fi

echo ""
echo "Cleanup complete."

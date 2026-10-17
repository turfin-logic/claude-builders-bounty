#!/usr/bin/env bash
set -e

# Run the python generator if available, or fall back to native git format
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/generate_changelog.py"
elif command -v python >/dev/null 2>&1; then
    python "$SCRIPT_DIR/generate_changelog.py"
else
    echo "Python is required to run the structured changelog parser."
    exit 1
fi

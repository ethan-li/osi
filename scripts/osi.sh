#!/bin/bash
# Unix shell launcher for OSI
# This script handles Python detection and launches OSI on macOS and Linux systems

set -e

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OSI_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    local python_cmd="$1"
    if ! $python_cmd -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Try to find a suitable Python executable
PYTHON_EXE=""

# Check for python3 first
if command_exists python3 && check_python_version python3; then
    PYTHON_EXE="python3"
elif command_exists python && check_python_version python; then
    PYTHON_EXE="python"
else
    echo "Error: Python 3.11 or later not found"
    echo "Please install Python 3.11 or later and ensure it's in your PATH"
    echo ""
    echo "Installation instructions:"
    echo "  macOS: brew install python3  (or download from python.org)"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  CentOS/RHEL: sudo yum install python3"
    echo "  Fedora: sudo dnf install python3"
    exit 1
fi

# Verify we found a working Python
if [ -z "$PYTHON_EXE" ]; then
    echo "Error: No suitable Python interpreter found"
    exit 1
fi

# Launch OSI
exec "$PYTHON_EXE" "$SCRIPT_DIR/osi.py" "$@"

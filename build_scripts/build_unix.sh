#!/bin/bash
# Unix build script for OSI PyInstaller executable
# This script builds OSI into a standalone binary for macOS and Linux

set -e

echo "Building OSI for $(uname -s)..."
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.11+ and try again."
    exit 1
fi

# Check Python version
python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" || {
    echo "Error: Python 3.11+ is required"
    python3 --version
    exit 1
}

# Check if we're in the right directory
if [ ! -f "osi_main.py" ]; then
    echo "Error: osi_main.py not found. Please run this script from the OSI project root."
    exit 1
fi

# Install PyInstaller if not available
python3 -c "import PyInstaller" 2>/dev/null || {
    echo "Installing PyInstaller..."
    python3 -m pip install pyinstaller>=5.0.0
}

# Run the build
python3 build_scripts/build_pyinstaller.py

echo ""
echo "Build completed successfully!"
echo "Executable should be in the dist/ directory"

# Make the script executable
chmod +x build_scripts/build_unix.sh

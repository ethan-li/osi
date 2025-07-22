#!/usr/bin/env python3
"""
OSI Distribution Builder

This script creates multiple distribution formats for OSI to support
different deployment scenarios and user preferences.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Import Unicode utilities for cross-platform compatibility
sys.path.insert(0, str(Path(__file__).parent / "build_scripts"))
from unicode_utils import (
    print_success,
    print_error,
    print_warning,
    print_build,
    print_package,
    print_docker,
    print_info,
    safe_print,
)


def build_executable():
    """Build PyInstaller executable."""
    print_build("Building PyInstaller Executable")
    safe_print("-" * 40)

    try:
        result = subprocess.run(
            [sys.executable, "build_scripts/build_pyinstaller.py"], check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print_error("Executable build failed")
        return False


def build_portable():
    """Build portable Python distribution."""
    print_package("Building Portable Distribution")
    safe_print("-" * 40)

    try:
        result = subprocess.run(
            [sys.executable, "build_scripts/build_portable.py"], check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print_error("Portable build failed")
        return False


def build_docker():
    """Build Docker distribution."""
    print_docker("Building Docker Distribution")
    safe_print("-" * 40)

    try:
        result = subprocess.run(
            [sys.executable, "build_scripts/build_docker.py"], check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print_error("Docker build failed")
        return False


def test_installer():
    """Test the self-contained installer."""
    safe_print("\n[TEST] Testing Self-contained Installer")
    safe_print("-" * 40)

    print_success("Self-contained installer ready: install_osi.py")
    safe_print("   Users can run: python install_osi.py")
    return True


def create_distribution_summary():
    """Create a summary of all distribution methods."""
    summary = """# OSI Distribution Methods

OSI provides multiple distribution methods to accommodate different user needs and environments:

## 1. Self-contained Installer (Recommended for most users)
**File**: `install_osi.py`
**Requirements**: Python 3.11+ only
**Usage**: `python install_osi.py`

- ✅ Automatically creates isolated environment
- ✅ Installs all dependencies automatically
- ✅ Works on Windows, macOS, Linux
- ✅ Smallest download size (~50KB)
- ✅ Easy to update

## 2. PyInstaller Executable
**File**: `dist/osi` or `dist/osi.exe`
**Requirements**: None
**Usage**: Direct execution

- ✅ No Python installation required
- ✅ Single file distribution
- ✅ Fast startup
- ❌ Larger file size (~50-100MB)
- ❌ Platform-specific builds needed

## 3. Portable Python Distribution
**File**: `osi-portable-*.zip`
**Requirements**: None
**Usage**: Extract and run launcher scripts

- ✅ No Python installation required
- ✅ Includes full Python environment
- ✅ Easy to distribute
- ❌ Large file size (~100-200MB)
- ❌ Currently Windows-only

## 4. Docker Container
**Image**: `osi:latest`
**Requirements**: Docker
**Usage**: `docker run --rm -v "$(pwd):/workspace" osi:latest`

- ✅ Consistent environment everywhere
- ✅ Easy to update
- ✅ Isolated from host system
- ❌ Requires Docker installation
- ❌ Larger resource usage

## Recommendations by Use Case

### Individual Users
- **Primary**: Self-contained installer (`install_osi.py`)
- **Alternative**: PyInstaller executable

### Enterprise Deployment
- **Primary**: Docker container
- **Alternative**: Portable distribution

### Air-gapped Environments
- **Primary**: Portable distribution
- **Alternative**: PyInstaller executable

### Development/Testing
- **Primary**: Self-contained installer
- **Alternative**: Docker container

## Quick Start

1. **Download** the appropriate distribution for your needs
2. **Extract/Install** following the method-specific instructions
3. **Run** `osi list` to verify installation
4. **Install tools** using `osi install <tool-name>`

For detailed instructions, see the README file included with each distribution method.
"""

    with open("DISTRIBUTION_GUIDE.md", "w") as f:
        f.write(summary)

    print_success("Distribution guide created: DISTRIBUTION_GUIDE.md")


def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description="Build OSI distributions")
    parser.add_argument("--all", action="store_true", help="Build all distributions")
    parser.add_argument(
        "--executable", action="store_true", help="Build PyInstaller executable"
    )
    parser.add_argument(
        "--portable", action="store_true", help="Build portable distribution"
    )
    parser.add_argument(
        "--docker", action="store_true", help="Build Docker distribution"
    )
    parser.add_argument(
        "--installer", action="store_true", help="Test installer script"
    )

    args = parser.parse_args()

    if not any([args.all, args.executable, args.portable, args.docker, args.installer]):
        args.all = True  # Default to building all

    print("OSI Distribution Builder")
    print("=" * 50)

    results = {}

    # Create build_scripts directory if it doesn't exist
    Path("build_scripts").mkdir(exist_ok=True)

    if args.all or args.installer:
        results["installer"] = test_installer()

    if args.all or args.executable:
        results["executable"] = build_executable()

    if args.all or args.portable:
        results["portable"] = build_portable()

    if args.all or args.docker:
        results["docker"] = build_docker()

    # Create distribution summary
    create_distribution_summary()

    # Print results
    safe_print("\n" + "=" * 50)
    safe_print("[SUMMARY] Build Results Summary")
    safe_print("-" * 50)

    success_count = 0
    total_count = 0

    for method, success in results.items():
        total_count += 1
        if success:
            success_count += 1
            print_success(f"{method.capitalize()}: SUCCESS")
        else:
            print_error(f"{method.capitalize()}: FAILED")

    safe_print(
        f"\n[STATS] Overall: {success_count}/{total_count} distributions built successfully"
    )

    if success_count == total_count:
        safe_print("\n[SUCCESS] All distributions built successfully!")
        print_info("Next steps:")
        safe_print("1. Test each distribution method")
        safe_print("2. Upload to distribution channels")
        safe_print("3. Update documentation")
        safe_print("4. Notify users of new release")
        return 0
    else:
        print_warning(f"{total_count - success_count} distributions failed")
        safe_print("Check the output above for error details")
        return 1


if __name__ == "__main__":
    sys.exit(main())

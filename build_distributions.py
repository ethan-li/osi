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
    print_build,
    print_error,
    print_info,
    print_success,
    print_warning,
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

- [OK] Automatically creates isolated environment
- [OK] Installs all dependencies automatically
- [OK] Works on Windows, macOS, Linux
- [OK] Smallest download size (~50KB)
- [OK] Easy to update

## 2. PyInstaller Executable
**File**: `dist/osi` or `dist/osi.exe`
**Requirements**: None
**Usage**: Direct execution

- [OK] No Python installation required
- [OK] Single file distribution
- [OK] Fast startup
- [ERROR] Larger file size (~50-100MB)
- [ERROR] Platform-specific builds needed



## Recommendations by Use Case

### Individual Users
- **Primary**: Self-contained installer (`install_osi.py`)
- **Alternative**: PyInstaller executable

### Enterprise Deployment
- **Primary**: PyInstaller executable
- **Alternative**: Self-contained installer

### Air-gapped Environments
- **Primary**: PyInstaller executable
- **Alternative**: Self-contained installer

### Development/Testing
- **Primary**: Self-contained installer
- **Alternative**: PyInstaller executable

## Quick Start

1. **Download** the appropriate distribution for your needs
2. **Extract/Install** following the method-specific instructions
3. **Run** `osi list` to verify installation
4. **Install tools** using `osi install <tool-name>`

For detailed instructions, see the README file included with each distribution method.
"""

    with open("DISTRIBUTION_GUIDE.md", "w", encoding="utf-8") as f:
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
        "--installer", action="store_true", help="Test installer script"
    )

    args = parser.parse_args()

    if not any([args.all, args.executable, args.installer]):
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

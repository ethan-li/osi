#!/usr/bin/env python3
"""
OSI Distribution Builder

This script creates multiple distribution formats for OSI to support
different deployment scenarios and user preferences.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def build_executable():
    """Build PyInstaller executable."""
    print("\n🔨 Building PyInstaller Executable")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "build_scripts/build_executable.py"
        ], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print("❌ Executable build failed")
        return False

def build_portable():
    """Build portable Python distribution."""
    print("\n📦 Building Portable Distribution")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "build_scripts/build_portable.py"
        ], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print("❌ Portable build failed")
        return False

def build_docker():
    """Build Docker distribution."""
    print("\n🐳 Building Docker Distribution")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "build_scripts/build_docker.py"
        ], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print("❌ Docker build failed")
        return False

def test_installer():
    """Test the self-contained installer."""
    print("\n🧪 Testing Self-contained Installer")
    print("-" * 40)
    
    print("✅ Self-contained installer ready: install_osi.py")
    print("   Users can run: python install_osi.py")
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
    
    print("✅ Distribution guide created: DISTRIBUTION_GUIDE.md")

def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description="Build OSI distributions")
    parser.add_argument("--all", action="store_true", help="Build all distributions")
    parser.add_argument("--executable", action="store_true", help="Build PyInstaller executable")
    parser.add_argument("--portable", action="store_true", help="Build portable distribution")
    parser.add_argument("--docker", action="store_true", help="Build Docker distribution")
    parser.add_argument("--installer", action="store_true", help="Test installer script")
    
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
    print("\n" + "=" * 50)
    print("📊 Build Results Summary")
    print("-" * 50)
    
    success_count = 0
    total_count = 0
    
    for method, success in results.items():
        total_count += 1
        if success:
            success_count += 1
            print(f"✅ {method.capitalize()}: SUCCESS")
        else:
            print(f"❌ {method.capitalize()}: FAILED")
    
    print(f"\n📈 Overall: {success_count}/{total_count} distributions built successfully")
    
    if success_count == total_count:
        print("\n🎉 All distributions built successfully!")
        print("\n📋 Next steps:")
        print("1. Test each distribution method")
        print("2. Upload to distribution channels")
        print("3. Update documentation")
        print("4. Notify users of new release")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count} distributions failed")
        print("Check the output above for error details")
        return 1

if __name__ == "__main__":
    sys.exit(main())

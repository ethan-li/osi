#!/usr/bin/env python3
"""
Build script to create portable OSI distribution

This script creates a portable Python environment with OSI and all dependencies
pre-installed, allowing users to run OSI without any installation.
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import platform

def download_portable_python():
    """Download portable Python for the current platform."""
    print("Setting up portable Python environment...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        # Use Python embeddable package for Windows
        if "64" in arch or "amd64" in arch:
            python_url = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip"
            python_dir = "python-3.11.7-embed-amd64"
        else:
            python_url = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-win32.zip"
            python_dir = "python-3.11.7-embed-win32"
    else:
        print("❌ Portable Python distribution currently only supports Windows")
        print("For Linux/macOS, consider using the PyInstaller method or Docker")
        return None
    
    portable_dir = Path("portable_osi")
    python_path = portable_dir / "python"
    
    # Create directories
    portable_dir.mkdir(exist_ok=True)
    python_path.mkdir(exist_ok=True)
    
    # Download Python if not already present
    python_zip = portable_dir / "python.zip"
    if not python_zip.exists():
        print(f"Downloading Python from {python_url}...")
        import urllib.request
        urllib.request.urlretrieve(python_url, python_zip)
    
    # Extract Python
    print("Extracting Python...")
    with zipfile.ZipFile(python_zip, 'r') as zip_ref:
        zip_ref.extractall(python_path)
    
    # Remove zip file
    python_zip.unlink()
    
    return python_path

def setup_portable_environment(python_path):
    """Set up the portable environment with OSI and dependencies."""
    print("Setting up portable environment...")
    
    if platform.system().lower() == "windows":
        python_exe = python_path / "python.exe"
        pip_exe = python_path / "Scripts" / "pip.exe"
    else:
        python_exe = python_path / "bin" / "python"
        pip_exe = python_path / "bin" / "pip"
    
    # Install pip if not present (for embeddable Python)
    if not pip_exe.exists():
        print("Installing pip...")
        get_pip_path = python_path / "get-pip.py"
        
        # Download get-pip.py
        import urllib.request
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip_path)
        
        # Install pip
        subprocess.run([str(python_exe), str(get_pip_path)], check=True)
        get_pip_path.unlink()
    
    # Install OSI dependencies
    print("Installing OSI dependencies...")
    with open("requirements.txt", "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.run([str(python_exe), "-m", "pip", "install", req], check=True)
    
    # Copy OSI source code
    print("Copying OSI source code...")
    portable_dir = python_path.parent
    osi_dest = portable_dir / "osi"
    
    if osi_dest.exists():
        shutil.rmtree(osi_dest)
    
    # Copy OSI package
    shutil.copytree("osi", osi_dest / "osi")
    
    # Copy scripts
    shutil.copytree("scripts", osi_dest / "scripts")
    
    # Copy other necessary files
    for file in ["requirements.txt", "README.md"]:
        if Path(file).exists():
            shutil.copy(file, osi_dest)
    
    return portable_dir

def create_launcher_scripts(portable_dir):
    """Create launcher scripts for the portable distribution."""
    print("Creating launcher scripts...")
    
    # Windows batch file
    batch_content = '''@echo off
set SCRIPT_DIR=%~dp0
set PYTHON_HOME=%SCRIPT_DIR%python
set PYTHONPATH=%SCRIPT_DIR%osi
set PATH=%PYTHON_HOME%;%PYTHON_HOME%\\Scripts;%PATH%

"%PYTHON_HOME%\\python.exe" "%SCRIPT_DIR%osi\\scripts\\osi.py" %*
'''
    
    with open(portable_dir / "osi.bat", "w") as f:
        f.write(batch_content)
    
    # PowerShell script
    ps1_content = '''$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonHome = Join-Path $ScriptDir "python"
$OSIPath = Join-Path $ScriptDir "osi"

$env:PYTHONPATH = $OSIPath
$env:PATH = "$PythonHome;$PythonHome\\Scripts;" + $env:PATH

& "$PythonHome\\python.exe" "$OSIPath\\scripts\\osi.py" @args
'''
    
    with open(portable_dir / "osi.ps1", "w") as f:
        f.write(ps1_content)
    
    # Unix shell script
    shell_content = '''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_HOME="$SCRIPT_DIR/python"
OSI_PATH="$SCRIPT_DIR/osi"

export PYTHONPATH="$OSI_PATH"
export PATH="$PYTHON_HOME/bin:$PATH"

"$PYTHON_HOME/bin/python" "$OSI_PATH/scripts/osi.py" "$@"
'''
    
    shell_script = portable_dir / "osi.sh"
    with open(shell_script, "w") as f:
        f.write(shell_content)
    
    # Make shell script executable
    shell_script.chmod(0o755)
    
    print("Created launcher scripts: osi.bat, osi.ps1, osi.sh")

def create_readme(portable_dir):
    """Create README for portable distribution."""
    readme_content = '''# OSI Portable Distribution

This is a portable distribution of OSI (Organized Software Installer) that requires no installation.

## Usage

### Windows
- Double-click `osi.bat` or run from command prompt: `osi.bat <command>`
- Or use PowerShell: `.\\osi.ps1 <command>`

### Linux/macOS
- Run: `./osi.sh <command>`

## Examples

```bash
# Windows
osi.bat list
osi.bat install text-processor
osi.bat run text-processor --help

# Linux/macOS
./osi.sh list
./osi.sh install text-processor
./osi.sh run text-processor --help
```

## Directory Structure

```
portable_osi/
├── python/           # Portable Python environment
├── osi/             # OSI source code and scripts
├── osi.bat          # Windows batch launcher
├── osi.ps1          # PowerShell launcher
├── osi.sh           # Unix shell launcher
└── README.md        # This file
```

## Requirements

- No Python installation required
- No additional dependencies needed
- Works on Windows, Linux, and macOS
- Approximately 50-100 MB total size

## Troubleshooting

If you encounter issues:

1. Ensure the portable_osi directory is not in a path with spaces
2. On Windows, try running as administrator if needed
3. On Linux/macOS, ensure osi.sh has execute permissions: `chmod +x osi.sh`

For more help, see the main OSI documentation.
'''
    
    with open(portable_dir / "README.md", "w") as f:
        f.write(readme_content)

def test_portable_distribution(portable_dir):
    """Test the portable distribution."""
    print("Testing portable distribution...")
    
    if platform.system().lower() == "windows":
        launcher = portable_dir / "osi.bat"
    else:
        launcher = portable_dir / "osi.sh"
    
    try:
        # Test help command
        result = subprocess.run([str(launcher), "--help"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Portable distribution help command works")
        else:
            print(f"❌ Help command failed: {result.stderr}")
            return False
        
        # Test list command
        result = subprocess.run([str(launcher), "list"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Portable distribution list command works")
        else:
            print(f"❌ List command failed: {result.stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Portable distribution test timed out")
        return False
    except Exception as e:
        print(f"❌ Portable distribution test failed: {e}")
        return False

def create_distribution_package(portable_dir):
    """Create a zip package for distribution."""
    print("Creating distribution package...")
    
    zip_name = f"osi-portable-{platform.system().lower()}-{platform.machine().lower()}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(portable_dir.parent)
                zipf.write(file_path, arc_path)
    
    size_mb = Path(zip_name).stat().st_size / (1024 * 1024)
    print(f"✅ Distribution package created: {zip_name} ({size_mb:.1f} MB)")
    return zip_name

def main():
    """Main build process."""
    print("OSI Portable Distribution Builder")
    print("=" * 50)
    
    try:
        # Step 1: Download portable Python
        python_path = download_portable_python()
        if not python_path:
            return 1
        
        # Step 2: Set up environment
        portable_dir = setup_portable_environment(python_path)
        
        # Step 3: Create launcher scripts
        create_launcher_scripts(portable_dir)
        
        # Step 4: Create README
        create_readme(portable_dir)
        
        # Step 5: Test distribution
        if test_portable_distribution(portable_dir):
            print("✅ Portable distribution tested successfully")
        else:
            print("❌ Portable distribution failed testing")
            return 1
        
        # Step 6: Create distribution package
        zip_name = create_distribution_package(portable_dir)
        
        print("\n🎉 Success! Portable OSI distribution created.")
        print(f"📁 Distribution package: {Path(zip_name).absolute()}")
        print(f"📁 Portable directory: {portable_dir.absolute()}")
        print("\n📋 Distribution instructions:")
        print("1. Extract the zip file on target machines")
        print("2. Run osi.bat (Windows) or ./osi.sh (Linux/macOS)")
        print("3. No Python installation required")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

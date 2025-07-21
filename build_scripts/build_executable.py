#!/usr/bin/env python3
"""
Build script to create self-contained OSI executable using PyInstaller

This script creates a single executable file that includes all dependencies,
making OSI truly "download and run" for end users.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_build_dependencies():
    """Install PyInstaller and other build dependencies."""
    print("Installing build dependencies...")
    
    dependencies = [
        "pyinstaller>=5.0",
        "auto-py-to-exe",  # Optional GUI for PyInstaller
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)

def create_main_entry_point():
    """Create a main entry point for PyInstaller."""
    main_content = '''#!/usr/bin/env python3
"""
Main entry point for OSI executable

This file serves as the entry point when OSI is packaged as an executable.
"""

import sys
import os
from pathlib import Path

# Add the bundled OSI package to Python path
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    bundle_dir = Path(sys._MEIPASS)
    sys.path.insert(0, str(bundle_dir))
else:
    # Running as script
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))

try:
    from osi.launcher import main
    sys.exit(main())
except Exception as e:
    print(f"Error starting OSI: {e}")
    input("Press Enter to exit...")
    sys.exit(1)
'''
    
    with open("osi_main.py", "w") as f:
        f.write(main_content)
    
    print("Created main entry point: osi_main.py")

def create_pyinstaller_spec():
    """Create PyInstaller spec file for customized build."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the OSI package path
osi_path = Path.cwd() / "osi"

block_cipher = None

a = Analysis(
    ['osi_main.py'],
    pathex=[str(Path.cwd())],
    binaries=[],
    datas=[
        # Include OSI package
        (str(osi_path), 'osi'),
        # Include scripts directory
        ('scripts', 'scripts'),
    ],
    hiddenimports=[
        'osi',
        'osi.launcher',
        'osi.config_manager',
        'osi.wheel_manager',
        'osi.environment_manager',
        'osi.dependency_resolver',
        'osi.pyproject_parser',
        'osi.tool_config',
        'osi.utils',
        'toml',
        'packaging',
        'virtualenv',
        'pkginfo',
        'zipfile',
        'email.parser',
        'email.message',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='osi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open("osi.spec", "w") as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file: osi.spec")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building OSI executable...")
    
    # Clean previous builds
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    
    # Build using spec file
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "osi.spec"
    ], check=True)
    
    print("Build completed!")
    
    # Check if executable was created
    if sys.platform == "win32":
        exe_path = Path("dist/osi.exe")
    else:
        exe_path = Path("dist/osi")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable created: {exe_path} ({size_mb:.1f} MB)")
        return exe_path
    else:
        print("❌ Executable not found!")
        return None

def test_executable(exe_path):
    """Test the built executable."""
    print(f"Testing executable: {exe_path}")
    
    try:
        # Test basic commands
        result = subprocess.run([str(exe_path), "--help"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Executable help command works")
        else:
            print(f"❌ Help command failed: {result.stderr}")
            return False
        
        # Test list command
        result = subprocess.run([str(exe_path), "list"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Executable list command works")
        else:
            print(f"❌ List command failed: {result.stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Executable test timed out")
        return False
    except Exception as e:
        print(f"❌ Executable test failed: {e}")
        return False

def main():
    """Main build process."""
    print("OSI Executable Builder")
    print("=" * 50)
    
    try:
        # Step 1: Install build dependencies
        install_build_dependencies()
        
        # Step 2: Create entry point
        create_main_entry_point()
        
        # Step 3: Create spec file
        create_pyinstaller_spec()
        
        # Step 4: Build executable
        exe_path = build_executable()
        
        if exe_path:
            # Step 5: Test executable
            if test_executable(exe_path):
                print("\n🎉 Success! OSI executable built and tested successfully.")
                print(f"📁 Executable location: {exe_path.absolute()}")
                print("\n📋 Distribution instructions:")
                print("1. Copy the executable to target machines")
                print("2. No installation required - just run the executable")
                print("3. The executable includes all dependencies")
            else:
                print("\n❌ Executable built but failed testing")
                return 1
        else:
            print("\n❌ Failed to build executable")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return 1
    finally:
        # Cleanup temporary files
        for temp_file in ["osi_main.py", "osi.spec"]:
            if Path(temp_file).exists():
                Path(temp_file).unlink()

if __name__ == "__main__":
    sys.exit(main())

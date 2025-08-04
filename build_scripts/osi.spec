# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for OSI (Organized Software Installer)

This spec file defines how to build OSI into a standalone executable
that includes all necessary modules, dependencies, and resource files.
"""

import os
import sys
from pathlib import Path

# Get the project root directory
# Try multiple methods to find the correct project root
project_root = None
osi_main_path = None

# Method 1: Use environment variable if set (CI environment)
if os.environ.get('OSI_PROJECT_ROOT'):
    project_root = Path(os.environ['OSI_PROJECT_ROOT'])
    print(f"[INFO] Using project root from OSI_PROJECT_ROOT: {project_root}")
else:
    # Method 2: Use SPECPATH (default PyInstaller behavior)
    project_root = Path(SPECPATH).parent
    print(f"[INFO] Using project root from SPECPATH: {project_root}")

osi_main_path = project_root / 'osi_main.py'

# Debug path resolution for CI troubleshooting
print(f"[DEBUG] SPECPATH: {SPECPATH}")
print(f"[DEBUG] project_root: {project_root}")
print(f"[DEBUG] osi_main_path: {osi_main_path}")
print(f"[DEBUG] osi_main.py exists: {osi_main_path.exists()}")
print(f"[DEBUG] Current working directory: {os.getcwd()}")

# List Python files in project root for debugging
try:
    py_files = list(project_root.glob('*.py'))
    print(f"[DEBUG] Python files in project_root: {[f.name for f in py_files]}")
except Exception as e:
    print(f"[DEBUG] Error listing files in project_root: {e}")

# Verify the main script exists
if not osi_main_path.exists():
    # Try alternative paths
    alternative_paths = [
        Path(os.getcwd()) / 'osi_main.py',  # Current working directory
        Path(SPECPATH).parent / 'osi_main.py',  # Original SPECPATH calculation
    ]

    print(f"[ERROR] Main script not found at: {osi_main_path}")
    print(f"[DEBUG] Trying alternative paths:")

    for alt_path in alternative_paths:
        print(f"[DEBUG]   Checking: {alt_path} -> exists: {alt_path.exists()}")
        if alt_path.exists():
            osi_main_path = alt_path
            project_root = alt_path.parent
            print(f"[SUCCESS] Found main script at: {osi_main_path}")
            break
    else:
        # Last resort: list all files to help debug
        print(f"[DEBUG] Files in current directory: {list(Path(os.getcwd()).glob('*'))}")
        print(f"[DEBUG] Files in SPECPATH parent: {list(Path(SPECPATH).parent.glob('*'))}")
        raise FileNotFoundError(f"Could not find osi_main.py in any of the expected locations: {alternative_paths}")

print(f"[FINAL] Using osi_main_path: {osi_main_path}")
print(f"[FINAL] Using project_root: {project_root}")

# Define data files to include
datas = []

# Include kits directory if it exists
kits_dir = project_root / 'kits'
if kits_dir.exists():
    datas.append((str(kits_dir), 'kits'))

# Include wheels directory if it exists
wheels_dir = project_root / 'wheels'
if wheels_dir.exists():
    datas.append((str(wheels_dir), 'wheels'))

# Include third-party license file for legal compliance
license_file = project_root / 'THIRD_PARTY_LICENSES.txt'
if license_file.exists():
    datas.append((str(license_file), '.'))
    print(f"[INFO] Including license file: {license_file}")
else:
    print(f"[WARNING] License file not found: {license_file}")

# Include any configuration templates
config_files = []
for config_file in project_root.glob('*.toml'):
    if config_file.exists():
        config_files.append((str(config_file), '.'))

datas.extend(config_files)

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    'osi.launcher',
    'osi.config_manager',
    'osi.wheel_manager',
    'osi.environment_manager',
    'osi.dependency_resolver',
    'osi.tool_config',
    'osi.pyproject_parser',
    'osi.utils',
    'toml',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
    'virtualenv',
    'pkginfo',
    'pkginfo.wheel',
    'zipfile',
    'subprocess',
    'tempfile',
    'shutil',
    'json',
    'urllib.request',
    'urllib.parse',
    'pathlib',
    'configparser',
    'logging',
    'argparse',
]

# Exclude unnecessary modules to reduce size
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'wx',
]

# Analysis configuration
a = Analysis(
    [str(osi_main_path)],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
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

# Platform-specific configurations
if sys.platform == 'darwin':
    # macOS: Create .app bundle
    app = BUNDLE(
        exe,
        name='OSI.app',
        icon=None,
        bundle_identifier='com.ethanli.osi',
        version='1.0.0',
        info_plist={
            'CFBundleName': 'OSI',
            'CFBundleDisplayName': 'Organized Software Installer',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )

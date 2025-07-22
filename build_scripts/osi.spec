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
# In PyInstaller spec files, we need to use SPECPATH
project_root = Path(SPECPATH).parent
osi_main_path = project_root / 'osi_main.py'

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

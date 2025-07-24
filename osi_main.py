#!/usr/bin/env python3
"""
OSI Main Entry Point for PyInstaller

This is the main entry point for OSI when built as a standalone executable.
It's designed to work with PyInstaller's bundling system and handles
resource path resolution for the executable environment.
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in development mode
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def setup_environment():
    """Setup the environment for OSI execution"""
    # Add the OSI package to Python path
    osi_package_path = get_resource_path("osi")
    if osi_package_path not in sys.path:
        sys.path.insert(0, os.path.dirname(osi_package_path))

    # Set environment variables for resource paths
    os.environ["OSI_EXECUTABLE_MODE"] = "1"
    os.environ["OSI_RESOURCE_PATH"] = get_resource_path("")

    # Set paths for kits and wheels if they exist
    kits_path = get_resource_path("kits")
    if os.path.exists(kits_path):
        os.environ["OSI_KITS_PATH"] = kits_path

    wheels_path = get_resource_path("wheels")
    if os.path.exists(wheels_path):
        os.environ["OSI_WHEELS_PATH"] = wheels_path


def main():
    """Main entry point for OSI executable"""
    try:
        # Setup the environment
        setup_environment()

        # Import and run OSI
        from osi.launcher import main as osi_main

        return osi_main()

    except ImportError as e:
        print(f"Error: Failed to import OSI modules: {e}")
        print("This may indicate a problem with the executable build.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

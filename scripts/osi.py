#!/usr/bin/env python3
"""
Cross-platform Python launcher for OSI

This script serves as the main entry point for OSI on all platforms.
It handles Python path detection and launches the main OSI application.
"""

import sys
import os
from pathlib import Path

# Add the OSI package to the Python path
osi_root = Path(__file__).parent.parent
sys.path.insert(0, str(osi_root))

try:
    from osi.launcher import main
    sys.exit(main())
except ImportError as e:
    print(f"Error: Failed to import OSI modules: {e}")
    print("Make sure OSI is properly installed and all dependencies are available.")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

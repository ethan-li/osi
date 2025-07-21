"""
OSI Test Suite

This package contains all tests for the OSI (Organized Software Installer) system.

Test Structure:
- test_config_manager.py: Tests for configuration management
- test_wheel_manager.py: Tests for wheel discovery and management
- test_launcher.py: Tests for the main launcher functionality
- test_environment_manager.py: Tests for environment management
- test_dependency_resolver.py: Tests for dependency resolution
- test_integration.py: Integration tests for the complete system
- test_distribution.py: Tests for distribution methods

To run all tests:
    python -m unittest discover tests/

To run specific test files:
    python -m unittest tests.test_config_manager
    python -m unittest tests.test_wheel_manager

To run specific test classes:
    python -m unittest tests.test_config_manager.TestConfigManager

To run specific test methods:
    python -m unittest tests.test_config_manager.TestConfigManager.test_load_tool_config
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so tests can import osi modules
test_dir = Path(__file__).parent
project_root = test_dir.parent
sys.path.insert(0, str(project_root))

# Common test utilities and fixtures can be added here
TEST_DATA_DIR = test_dir / "data"
TEST_WHEELS_DIR = test_dir / "wheels"
TEST_KITS_DIR = test_dir / "kits"


def ensure_test_directories() -> None:
    """Ensure test data directories exist."""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    TEST_WHEELS_DIR.mkdir(exist_ok=True)
    TEST_KITS_DIR.mkdir(exist_ok=True)


# Initialize test directories
ensure_test_directories()

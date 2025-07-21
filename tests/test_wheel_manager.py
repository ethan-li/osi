#!/usr/bin/env python3
"""
Unit tests for OSI WheelManager

Tests the wheel discovery, validation, and management functionality.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from osi.utils import setup_logging
from osi.wheel_manager import WheelInfo, WheelManager


class TestWheelManager(unittest.TestCase):
    """Test cases for WheelManager class."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        setup_logging("WARNING")

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.wheel_manager = WheelManager()
        self.test_kits_dir = Path(__file__).parent / "kits"

    def test_initialization(self):
        """Test WheelManager initialization."""
        self.assertIsInstance(self.wheel_manager, WheelManager)
        self.assertIsNotNone(self.wheel_manager.logger)
        self.assertTrue(self.wheel_manager.wheels_dir.exists())
        self.assertTrue(self.wheel_manager.kits_dir.exists())

    def test_discover_wheels(self):
        """Test wheel discovery functionality."""
        wheels = self.wheel_manager.discover_wheels()
        self.assertIsInstance(wheels, list)

        # All discovered items should be WheelInfo objects
        for wheel in wheels:
            self.assertIsInstance(wheel, WheelInfo)
            self.assertIsInstance(wheel.name, str)
            self.assertIsInstance(wheel.version, str)
            self.assertTrue(wheel.path.exists())

    def test_discover_wheels_with_custom_paths(self):
        """Test wheel discovery with custom search paths."""
        if self.test_kits_dir.exists():
            custom_paths = [self.test_kits_dir]
            wheels = self.wheel_manager.discover_wheels(custom_paths)
            self.assertIsInstance(wheels, list)

            # Should find wheels in test kits
            if wheels:
                for wheel in wheels:
                    self.assertIsInstance(wheel, WheelInfo)
                    # Path should be within our test kits directory
                    self.assertTrue(
                        str(wheel.path).startswith(str(self.test_kits_dir)),
                        f"Wheel path {wheel.path} should be in test kits directory",
                    )
        else:
            self.skipTest("Test kits directory not available")

    def test_get_wheel_info(self):
        """Test extracting information from wheel files."""
        wheels = self.wheel_manager.discover_wheels()

        if wheels:
            wheel_path = wheels[0].path
            wheel_info = self.wheel_manager.get_wheel_info(wheel_path)

            self.assertIsInstance(wheel_info, WheelInfo)
            self.assertIsInstance(wheel_info.name, str)
            self.assertIsInstance(wheel_info.version, str)
            self.assertIsInstance(wheel_info.dependencies, list)
            self.assertIsInstance(wheel_info.entry_points, dict)
            self.assertEqual(wheel_info.path, wheel_path)
        else:
            self.skipTest("No wheels available for testing")

    def test_find_wheel_by_name(self):
        """Test finding wheels by tool name."""
        wheels = self.wheel_manager.discover_wheels()

        if wheels:
            # Test finding existing wheel
            existing_wheel = wheels[0]
            found_wheel = self.wheel_manager.find_wheel_by_name(
                existing_wheel.tool_name
            )

            self.assertIsNotNone(
                found_wheel, f"Should find wheel for {existing_wheel.tool_name}"
            )
            self.assertEqual(found_wheel.name, existing_wheel.name)

        # Test finding non-existent wheel
        non_existent = self.wheel_manager.find_wheel_by_name("non_existent_tool_12345")
        self.assertIsNone(non_existent, "Should not find non-existent wheel")

    def test_list_available_tools(self):
        """Test listing available tools from wheels."""
        tools = self.wheel_manager.list_available_tools()
        self.assertIsInstance(tools, list)

        # All tools should be WheelInfo objects
        for tool in tools:
            self.assertIsInstance(tool, WheelInfo)
            self.assertIsInstance(tool.tool_name, str)

    def test_validate_wheel(self):
        """Test wheel file validation."""
        wheels = self.wheel_manager.discover_wheels()

        if wheels:
            wheel_path = wheels[0].path
            is_valid = self.wheel_manager.validate_wheel(wheel_path)
            self.assertTrue(is_valid, f"Wheel {wheel_path} should be valid")
        else:
            self.skipTest("No wheels available for testing")

        # Test with non-existent file
        non_existent_path = Path("/non/existent/wheel.whl")
        is_valid = self.wheel_manager.validate_wheel(non_existent_path)
        self.assertFalse(is_valid, "Non-existent wheel should be invalid")


class TestKitManagement(unittest.TestCase):
    """Test cases for kit management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.wheel_manager = WheelManager()

    def test_list_kits(self):
        """Test listing available kits."""
        kits = self.wheel_manager.list_kits()
        self.assertIsInstance(kits, list)

        # All kit names should be strings
        for kit in kits:
            self.assertIsInstance(kit, str)

    def test_get_kit_tools(self):
        """Test getting tools from a specific kit."""
        kits = self.wheel_manager.list_kits()

        if kits:
            kit_name = kits[0]
            tools = self.wheel_manager.get_kit_tools(kit_name)

            self.assertIsInstance(tools, list)

            # All tools should be WheelInfo objects
            for tool in tools:
                self.assertIsInstance(tool, WheelInfo)
        else:
            self.skipTest("No kits available for testing")

    def test_get_nonexistent_kit_tools(self):
        """Test getting tools from non-existent kit."""
        tools = self.wheel_manager.get_kit_tools("non_existent_kit_12345")
        self.assertIsInstance(tools, list)
        self.assertEqual(len(tools), 0, "Non-existent kit should return empty list")


class TestWheelInfo(unittest.TestCase):
    """Test cases for WheelInfo dataclass."""

    def test_wheel_info_creation(self):
        """Test creating WheelInfo objects."""
        wheel_info = WheelInfo(
            name="test-tool",
            version="1.0.0",
            filename="test_tool-1.0.0-py3-none-any.whl",
            path=Path("/test/path.whl"),
            metadata={},
            dependencies=[],
            entry_points={},
        )

        self.assertEqual(wheel_info.name, "test-tool")
        self.assertEqual(wheel_info.version, "1.0.0")
        self.assertEqual(wheel_info.tool_name, "test-tool")  # sanitized name

    def test_tool_name_property(self):
        """Test the tool_name property sanitization."""
        wheel_info = WheelInfo(
            name="test-tool-with-dashes",
            version="1.0.0",
            filename="test.whl",
            path=Path("/test.whl"),
            metadata={},
            dependencies=[],
            entry_points={},
        )

        # Should sanitize the name for tool_name property (dashes are preserved)
        self.assertEqual(wheel_info.tool_name, "test-tool-with-dashes")


if __name__ == "__main__":
    unittest.main(verbosity=2)

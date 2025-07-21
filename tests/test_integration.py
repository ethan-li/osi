#!/usr/bin/env python3
"""
Integration tests for OSI system

Tests the complete OSI system functionality including wheel-only validation,
CLI commands, and end-to-end workflows.
"""

import subprocess
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from osi.config_manager import ConfigManager
from osi.launcher import Launcher
from osi.utils import setup_logging
from osi.wheel_manager import WheelManager


class TestWheelOnlySystem(unittest.TestCase):
    """Test that OSI only supports wheel-based tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        setup_logging("WARNING")

    def test_no_directory_based_support(self):
        """Test that directory-based tool support has been removed."""
        config_manager = ConfigManager()

        # Check that get_tools_dir function no longer exists
        with self.assertRaises(ImportError):
            from osi.utils import get_tools_dir

        # Check that directory-based methods are removed
        methods_to_check = [
            "get_tool_directory",
            "get_tool_config_file",
            "get_tool_requirements_file",
            "save_tool_config",
            "create_tool_template",
        ]

        for method_name in methods_to_check:
            self.assertFalse(
                hasattr(config_manager, method_name),
                f"Method {method_name} should be removed",
            )

    def test_wheel_only_functionality(self):
        """Test that only wheel-based tools are supported."""
        config_manager = ConfigManager()
        wheel_manager = WheelManager()

        # Test that only wheel-based tools are listed
        tools = config_manager.list_tools()
        self.assertIsInstance(tools, list)

        for tool_name in tools:
            # Each tool should have a corresponding wheel
            wheel_info = wheel_manager.find_wheel_by_name(tool_name)
            self.assertIsNotNone(
                wheel_info, f"Tool {tool_name} should have corresponding wheel"
            )

    def test_no_tools_directory(self):
        """Test that tools directory no longer exists."""
        project_root = Path(__file__).parent.parent
        tools_dir = project_root / "tools"

        self.assertFalse(
            tools_dir.exists(), "Tools directory should not exist in wheel-only system"
        )


class TestCLICommands(unittest.TestCase):
    """Test CLI command functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.osi_script = self.project_root / "scripts" / "osi.py"

    def _run_osi_command(self, command: str) -> tuple[int, str]:
        """Run an OSI command and return exit code and output."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.osi_script)] + command.split(),
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30,
            )
            return result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return 1, "Command timed out"
        except Exception as e:
            return 1, str(e)

    def test_help_command(self):
        """Test help command."""
        exit_code, output = self._run_osi_command("--help")
        self.assertEqual(exit_code, 0, "Help command should succeed")
        self.assertIn("OSI", output, "Help should mention OSI")

    def test_list_command(self):
        """Test list command."""
        exit_code, output = self._run_osi_command("list")
        self.assertEqual(exit_code, 0, "List command should succeed")

    def test_list_kits_command(self):
        """Test list-kits command."""
        exit_code, output = self._run_osi_command("list-kits")
        self.assertEqual(exit_code, 0, "List-kits command should succeed")

    def test_doctor_command(self):
        """Test doctor command."""
        exit_code, output = self._run_osi_command("doctor")
        self.assertEqual(exit_code, 0, "Doctor command should succeed")

    def test_invalid_command(self):
        """Test invalid command handling."""
        exit_code, output = self._run_osi_command("invalid_command_12345")
        self.assertNotEqual(exit_code, 0, "Invalid command should fail")


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager()
        self.launcher = Launcher()

    def test_tool_discovery_workflow(self):
        """Test complete tool discovery workflow."""
        # List available tools
        tools = self.config_manager.list_tools()
        self.assertIsInstance(tools, list)

        if tools:
            tool_name = tools[0]

            # Check tool exists
            self.assertTrue(self.config_manager.tool_exists(tool_name))

            # Load configuration
            config = self.config_manager.load_tool_config(tool_name)
            self.assertIsNotNone(config)

            # Validate configuration
            is_valid = self.config_manager.validate_tool_config(tool_name)
            self.assertTrue(is_valid)

            # Get dependencies
            deps = self.config_manager.get_tool_dependencies(tool_name)
            self.assertIsInstance(deps, list)

            # Get wheel info
            wheel_info = self.config_manager.get_wheel_info(tool_name)
            self.assertIsNotNone(wheel_info)
        else:
            self.skipTest("No tools available for workflow testing")

    def test_kit_management_workflow(self):
        """Test complete kit management workflow."""
        wheel_manager = WheelManager()

        # List kits
        kits = wheel_manager.list_kits()
        self.assertIsInstance(kits, list)

        if kits:
            kit_name = kits[0]

            # Get kit tools
            kit_tools = wheel_manager.get_kit_tools(kit_name)
            self.assertIsInstance(kit_tools, list)

            # Each tool should be valid
            for tool in kit_tools:
                self.assertIsNotNone(tool.name)
                self.assertIsNotNone(tool.version)
                self.assertTrue(tool.path.exists())
        else:
            self.skipTest("No kits available for workflow testing")


class TestSystemValidation(unittest.TestCase):
    """Test overall system validation."""

    def test_all_imports_work(self):
        """Test that all OSI modules can be imported."""
        try:
            from osi import (
                config_manager,
                dependency_resolver,
                environment_manager,
                launcher,
                pyproject_parser,
                tool_config,
                utils,
                wheel_manager,
            )
        except ImportError as e:
            self.fail(f"Failed to import OSI modules: {e}")

    def test_core_functionality_available(self):
        """Test that core functionality is available."""
        # Test ConfigManager
        config_manager = ConfigManager()
        self.assertTrue(hasattr(config_manager, "list_tools"))
        self.assertTrue(hasattr(config_manager, "load_tool_config"))

        # Test WheelManager
        wheel_manager = WheelManager()
        self.assertTrue(hasattr(wheel_manager, "discover_wheels"))
        self.assertTrue(hasattr(wheel_manager, "list_kits"))

        # Test Launcher
        launcher = Launcher()
        self.assertTrue(hasattr(launcher, "install_tool"))
        self.assertTrue(hasattr(launcher, "run_tool"))

    def test_system_consistency(self):
        """Test that the system components work together consistently."""
        config_manager = ConfigManager()
        wheel_manager = WheelManager()

        # Tools from config manager should match wheels from wheel manager
        config_tools = set(config_manager.list_tools())
        wheel_tools = set(
            wheel.tool_name for wheel in wheel_manager.list_available_tools()
        )

        # All config tools should have corresponding wheels
        for tool in config_tools:
            self.assertIn(
                tool,
                wheel_tools,
                f"Tool {tool} from config manager should have corresponding wheel",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

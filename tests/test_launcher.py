#!/usr/bin/env python3
"""
Unit tests for OSI Launcher

Tests the main launcher functionality including tool installation,
execution, and kit management.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import subprocess

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from osi.launcher import Launcher
from osi.config_manager import ConfigManager
from osi.environment_manager import EnvironmentManager
from osi.utils import setup_logging


class TestLauncher(unittest.TestCase):
    """Test cases for Launcher class."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        setup_logging("WARNING")
        
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.launcher = Launcher()
        self.test_data_dir = Path(__file__).parent / "data"
        
    def test_initialization(self):
        """Test Launcher initialization."""
        self.assertIsInstance(self.launcher, Launcher)
        self.assertIsInstance(self.launcher.config_manager, ConfigManager)
        self.assertIsInstance(self.launcher.env_manager, EnvironmentManager)
        self.assertIsNotNone(self.launcher.logger)
        
    def test_list_tools(self):
        """Test listing available tools."""
        # This should not raise an exception
        try:
            self.launcher.list_tools()
        except Exception as e:
            self.fail(f"list_tools() raised an exception: {e}")
            
    def test_list_kits(self):
        """Test listing available kits."""
        try:
            self.launcher.list_kits()
        except Exception as e:
            self.fail(f"list_kits() raised an exception: {e}")
            
    def test_show_kit_info(self):
        """Test showing kit information."""
        kits = self.launcher.config_manager.wheel_manager.list_kits()
        
        if kits:
            kit_name = kits[0]
            try:
                self.launcher.show_kit_info(kit_name)
            except Exception as e:
                self.fail(f"show_kit_info() raised an exception: {e}")
        else:
            self.skipTest("No kits available for testing")
            
    def test_show_tool_info(self):
        """Test showing tool information."""
        tools = self.launcher.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            try:
                self.launcher.show_tool_info(tool_name)
            except Exception as e:
                self.fail(f"show_tool_info() raised an exception: {e}")
        else:
            self.skipTest("No tools available for testing")
            
    def test_doctor(self):
        """Test system diagnostics."""
        try:
            self.launcher.doctor()
        except Exception as e:
            self.fail(f"doctor() raised an exception: {e}")


class TestLauncherToolManagement(unittest.TestCase):
    """Test cases for tool management in Launcher."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.launcher = Launcher()
        
    def test_install_nonexistent_tool(self):
        """Test installing a non-existent tool."""
        result = self.launcher.install_tool("non_existent_tool_12345")
        self.assertFalse(result, "Installing non-existent tool should return False")
        
    def test_run_nonexistent_tool(self):
        """Test running a non-existent tool."""
        result = self.launcher.run_tool("non_existent_tool_12345", [])
        self.assertNotEqual(result, 0, "Running non-existent tool should return non-zero exit code")


class TestLauncherKitManagement(unittest.TestCase):
    """Test cases for kit management in Launcher."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.launcher = Launcher()
        
    def test_install_kit_nonexistent_path(self):
        """Test installing kit from non-existent path."""
        result = self.launcher.install_kit("/non/existent/path")
        self.assertFalse(result, "Installing from non-existent path should return False")
        
    def test_install_kit_invalid_path(self):
        """Test installing kit with invalid path format."""
        result = self.launcher.install_kit("")
        self.assertFalse(result, "Installing with empty path should return False")


class TestLauncherCommandBuilding(unittest.TestCase):
    """Test cases for command building functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.launcher = Launcher()
        
    def test_build_run_command_with_wheel_tool(self):
        """Test building run command for wheel-based tools."""
        tools = self.launcher.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            config = self.launcher.config_manager.load_tool_config(tool_name)
            
            if config:
                command = self.launcher._build_run_command(config, ["--help"])
                
                self.assertIsInstance(command, list, "Command should be a list")
                self.assertGreater(len(command), 0, "Command should not be empty")
                self.assertIn("--help", command, "Arguments should be included in command")
        else:
            self.skipTest("No tools available for testing")
            
    def test_build_run_command_no_entry_point(self):
        """Test building run command when no entry point is available."""
        # Create a mock config without entry points
        from osi.tool_config import ToolConfig
        
        config = ToolConfig(
            name="test_tool",
            version="1.0.0",
            description="Test tool",
            dependencies=[],
            entry_point=None,
            module=None,
            script=None,
            command=None
        )
        
        command = self.launcher._build_run_command(config, ["--help"])
        self.assertIsNone(command, "Should return None when no entry point available")


class TestLauncherIntegration(unittest.TestCase):
    """Integration tests for Launcher functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.launcher = Launcher()
        
    def test_full_workflow_with_available_tools(self):
        """Test complete workflow with available tools."""
        # List tools
        tools = self.launcher.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            
            # Check if tool exists
            exists = self.launcher.config_manager.tool_exists(tool_name)
            self.assertTrue(exists, f"Tool {tool_name} should exist")
            
            # Load config
            config = self.launcher.config_manager.load_tool_config(tool_name)
            self.assertIsNotNone(config, f"Should load config for {tool_name}")
            
            # Validate config
            is_valid = self.launcher.config_manager.validate_tool_config(tool_name)
            self.assertTrue(is_valid, f"Config for {tool_name} should be valid")
            
            # Get dependencies
            deps = self.launcher.config_manager.get_tool_dependencies(tool_name)
            self.assertIsInstance(deps, list, "Dependencies should be a list")
        else:
            self.skipTest("No tools available for integration testing")


if __name__ == '__main__':
    unittest.main(verbosity=2)

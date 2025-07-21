#!/usr/bin/env python3
"""
Unit tests for OSI ConfigManager

Tests the configuration management functionality including tool discovery,
configuration loading, and validation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from osi.config_manager import ConfigManager
from osi.wheel_manager import WheelManager
from osi.utils import setup_logging


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Set up logging to reduce noise during tests
        setup_logging("WARNING")
        
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config_manager = ConfigManager()
        self.test_data_dir = Path(__file__).parent / "data"
        self.test_kits_dir = Path(__file__).parent / "kits"
        
    def test_initialization(self):
        """Test ConfigManager initialization."""
        self.assertIsInstance(self.config_manager, ConfigManager)
        self.assertIsInstance(self.config_manager.wheel_manager, WheelManager)
        self.assertIsNotNone(self.config_manager.logger)
        
    def test_list_tools(self):
        """Test listing available tools."""
        tools = self.config_manager.list_tools()
        self.assertIsInstance(tools, list)
        
        # Should find at least the test tool if test kit is available
        if (self.test_kits_dir / "test_kit").exists():
            self.assertGreater(len(tools), 0, "Should find at least one tool from test kit")
            
    def test_tool_exists(self):
        """Test checking if tools exist."""
        tools = self.config_manager.list_tools()
        
        if tools:
            # Test with existing tool
            existing_tool = tools[0]
            self.assertTrue(
                self.config_manager.tool_exists(existing_tool),
                f"Tool {existing_tool} should exist"
            )
            
        # Test with non-existing tool
        self.assertFalse(
            self.config_manager.tool_exists("non_existent_tool_12345"),
            "Non-existent tool should return False"
        )
        
    def test_load_tool_config(self):
        """Test loading tool configuration."""
        tools = self.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            config = self.config_manager.load_tool_config(tool_name)
            
            self.assertIsNotNone(config, f"Should load config for {tool_name}")
            self.assertEqual(config.name, tool_name, "Config name should match tool name")
            self.assertIsInstance(config.version, str, "Version should be a string")
            self.assertIsInstance(config.description, str, "Description should be a string")
        else:
            self.skipTest("No tools available for testing")
            
    def test_load_nonexistent_tool_config(self):
        """Test loading configuration for non-existent tool."""
        config = self.config_manager.load_tool_config("non_existent_tool_12345")
        self.assertIsNone(config, "Should return None for non-existent tool")
        
    def test_validate_tool_config(self):
        """Test tool configuration validation."""
        tools = self.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            is_valid = self.config_manager.validate_tool_config(tool_name)
            self.assertTrue(is_valid, f"Tool {tool_name} should have valid configuration")
        else:
            self.skipTest("No tools available for testing")
            
        # Test validation of non-existent tool
        is_valid = self.config_manager.validate_tool_config("non_existent_tool_12345")
        self.assertFalse(is_valid, "Non-existent tool should have invalid configuration")
        
    def test_get_tool_dependencies(self):
        """Test getting tool dependencies."""
        tools = self.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            dependencies = self.config_manager.get_tool_dependencies(tool_name)
            self.assertIsInstance(dependencies, list, "Dependencies should be a list")
            
            # All dependencies should be strings
            for dep in dependencies:
                self.assertIsInstance(dep, str, f"Dependency {dep} should be a string")
        else:
            self.skipTest("No tools available for testing")
            
    def test_get_wheel_info(self):
        """Test getting wheel information for tools."""
        tools = self.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            wheel_info = self.config_manager.get_wheel_info(tool_name)
            
            if wheel_info:  # Wheel-based tool
                self.assertIsNotNone(wheel_info.name, "Wheel should have a name")
                self.assertIsNotNone(wheel_info.version, "Wheel should have a version")
                self.assertTrue(wheel_info.path.exists(), "Wheel file should exist")
        else:
            self.skipTest("No tools available for testing")


class TestConfigManagerCaching(unittest.TestCase):
    """Test cases for ConfigManager caching functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager()
        
    def test_config_caching(self):
        """Test that configuration caching works correctly."""
        tools = self.config_manager.list_tools()
        
        if tools:
            tool_name = tools[0]
            
            # Load config first time
            config1 = self.config_manager.load_tool_config(tool_name, use_cache=True)
            
            # Load config second time (should use cache)
            config2 = self.config_manager.load_tool_config(tool_name, use_cache=True)
            
            # Should be the same object (cached)
            self.assertIs(config1, config2, "Second load should return cached config")
            
            # Load without cache should create new object
            config3 = self.config_manager.load_tool_config(tool_name, use_cache=False)
            
            # Should be different objects but same content
            self.assertIsNot(config1, config3, "Non-cached load should return new object")
            if config1 and config3:
                self.assertEqual(config1.name, config3.name, "Configs should have same content")
        else:
            self.skipTest("No tools available for testing")


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""
Configuration Manager for OSI

Handles wheel-based tool configuration and metadata extraction.
Tools are distributed as Python wheels with standard pyproject.toml configuration.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .wheel_manager import WheelManager, WheelInfo
from .pyproject_parser import PyProjectParser
from .tool_config import ToolConfig


class ConfigManager:
    """
    Manages wheel-based tool configurations and metadata.

    Handles loading, validating, and managing tool configuration from wheels.
    All tools are distributed as Python wheels with pyproject.toml configuration.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._config_cache: Dict[str, ToolConfig] = {}
        self.wheel_manager = WheelManager()
        self.pyproject_parser = PyProjectParser()
    

    
    def tool_exists(self, tool_name: str) -> bool:
        """
        Check if a wheel-based tool exists.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool exists, False otherwise
        """
        # Check for wheel-based tool
        wheel_info = self.wheel_manager.find_wheel_by_name(tool_name)
        return wheel_info is not None
    
    def load_tool_config(self, tool_name: str, use_cache: bool = True) -> Optional[ToolConfig]:
        """
        Load a wheel-based tool's configuration.

        Args:
            tool_name: Name of the tool
            use_cache: Whether to use cached configuration

        Returns:
            ToolConfig object or None if not found
        """
        try:
            # Check cache first
            if use_cache and tool_name in self._config_cache:
                return self._config_cache[tool_name]

            # Load from wheel
            tool_config = self._load_from_wheel(tool_name)
            if not tool_config:
                self.logger.error(f"Wheel-based tool configuration not found for {tool_name}")
                return None

            self.logger.info(f"Loaded configuration for {tool_name} from wheel")

            # Cache the configuration
            self._config_cache[tool_name] = tool_config

            return tool_config

        except Exception as e:
            self.logger.error(f"Failed to load configuration for {tool_name}: {e}")
            return None



    def _load_from_wheel(self, tool_name: str) -> Optional[ToolConfig]:
        """Load configuration from wheel metadata."""
        try:
            wheel_info = self.wheel_manager.find_wheel_by_name(tool_name)
            if not wheel_info:
                return None

            pyproject_config = self.pyproject_parser.parse_from_wheel(wheel_info)
            if pyproject_config:
                return pyproject_config.to_tool_config()
            return None

        except Exception as e:
            self.logger.error(f"Failed to load from wheel: {e}")
            return None



    def list_tools(self) -> List[str]:
        """
        List all available wheel-based tools.

        Returns:
            List of tool names
        """
        try:
            tools = set()

            # Add wheel-based tools
            wheel_tools = self.wheel_manager.list_available_tools()
            for wheel_info in wheel_tools:
                tools.add(wheel_info.tool_name)

            return sorted(list(tools))

        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            return []

    def validate_tool_config(self, tool_name: str) -> bool:
        """
        Validate a wheel-based tool's configuration.

        Args:
            tool_name: Name of the tool

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check if wheel exists and is valid
            wheel_info = self.wheel_manager.find_wheel_by_name(tool_name)
            if not wheel_info:
                self.logger.error(f"Wheel for tool {tool_name} not found")
                return False

            # Validate wheel file
            if not self.wheel_manager.validate_wheel(wheel_info.path):
                self.logger.error(f"Invalid wheel file for {tool_name}")
                return False

            # Load and validate configuration
            config = self.load_tool_config(tool_name)
            if not config:
                self.logger.error(f"Failed to load configuration for {tool_name}")
                return False

            # Check that at least one entry point is specified
            if not any([config.entry_point, config.module, config.script, config.command]):
                self.logger.error(f"Tool {tool_name} has no entry point specified")
                return False

            self.logger.info(f"Configuration for {tool_name} is valid")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate configuration for {tool_name}: {e}")
            return False

    def get_tool_dependencies(self, tool_name: str) -> List[str]:
        """
        Get all dependencies for a wheel-based tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of dependency strings
        """
        try:
            dependencies = []

            # Get dependencies from wheel metadata
            wheel_info = self.get_wheel_info(tool_name)
            if wheel_info:
                wheel_deps = self.wheel_manager.get_wheel_dependencies(wheel_info)
                dependencies.extend(wheel_deps)
                self.logger.debug(f"Found {len(wheel_deps)} dependencies from wheel for {tool_name}")
            else:
                self.logger.warning(f"No wheel found for tool {tool_name}")

            # Remove duplicates while preserving order
            seen = set()
            unique_dependencies = []
            for dep in dependencies:
                if dep not in seen:
                    seen.add(dep)
                    unique_dependencies.append(dep)

            return unique_dependencies

        except Exception as e:
            self.logger.error(f"Failed to get dependencies for {tool_name}: {e}")
            return []



    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._config_cache.clear()
        self.wheel_manager.clear_cache()
        self.logger.info("Configuration cache cleared")

    def is_wheel_based_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is wheel-based.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool is wheel-based, False otherwise
        """
        wheel_info = self.wheel_manager.find_wheel_by_name(tool_name)
        return wheel_info is not None

    def get_wheel_info(self, tool_name: str) -> Optional[WheelInfo]:
        """
        Get wheel information for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            WheelInfo object or None if not a wheel-based tool
        """
        return self.wheel_manager.find_wheel_by_name(tool_name)

    def list_kits(self) -> List[str]:
        """
        List all available tool kits.

        Returns:
            List of kit names
        """
        return self.wheel_manager.list_kits()

    def get_kit_tools(self, kit_name: str) -> List[str]:
        """
        Get all tools in a specific kit.

        Args:
            kit_name: Name of the kit

        Returns:
            List of tool names in the kit
        """
        wheel_infos = self.wheel_manager.get_kit_tools(kit_name)
        return [wheel_info.tool_name for wheel_info in wheel_infos]

    def install_kit(self, kit_path: Path) -> bool:
        """
        Install a kit from a directory containing wheel files.

        Args:
            kit_path: Path to directory containing .whl files

        Returns:
            True if successful, False otherwise
        """
        try:
            if not kit_path.exists() or not kit_path.is_dir():
                self.logger.error(f"Kit path does not exist or is not a directory: {kit_path}")
                return False

            # Find all wheel files in the kit
            wheel_files = list(kit_path.glob("*.whl"))
            if not wheel_files:
                self.logger.error(f"No wheel files found in kit: {kit_path}")
                return False

            kit_name = kit_path.name
            success = self.wheel_manager.create_kit_from_wheels(kit_name, wheel_files)

            if success:
                self.logger.info(f"Successfully installed kit {kit_name} with {len(wheel_files)} tools")
                # Clear cache to pick up new tools
                self.clear_cache()

            return success

        except Exception as e:
            self.logger.error(f"Failed to install kit: {e}")
            return False

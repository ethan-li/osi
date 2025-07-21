"""
Launcher for OSI

Main entry point and command-line interface for the OSI system.
Handles tool execution, environment management, and user interactions.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, List, Optional

from .config_manager import ConfigManager
from .dependency_resolver import DependencyResolver
from .environment_manager import EnvironmentManager
from .utils import get_platform_info, setup_logging, validate_python_version


class Launcher:
    """
    Main launcher class for OSI.

    Provides command-line interface and coordinates between all components
    to manage tool execution and environment management.
    """

    def __init__(self) -> None:
        self.config_manager = ConfigManager()
        self.env_manager = EnvironmentManager()
        self.dependency_resolver = DependencyResolver()
        self.logger = logging.getLogger(__name__)

    def list_tools(self) -> None:
        """List all available tools."""
        tools = self.config_manager.list_tools()

        if not tools:
            print("No tools available.")
            return

        print("Available tools:")
        print("-" * 50)

        for tool_name in tools:
            config = self.config_manager.load_tool_config(tool_name)
            if config:
                status = "[OK]" if self.env_manager.environment_exists(tool_name) else "[!]"
                print(f"{status} {tool_name:<20} - {config.description}")
            else:
                print(f"[!] {tool_name:<20} - (configuration error)")

    def install_tool(self, tool_name: str) -> bool:
        """
        Install a wheel-based tool and its dependencies.

        Args:
            tool_name: Name of the tool to install

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Installing wheel-based tool: {tool_name}")

            # Check if tool exists
            if not self.config_manager.tool_exists(tool_name):
                print(f"Error: Tool '{tool_name}' not found.")
                return False

            # Get wheel info
            wheel_info = self.config_manager.get_wheel_info(tool_name)
            if not wheel_info:
                print(f"Error: No wheel found for tool '{tool_name}'.")
                return False

            return self._install_wheel_based_tool(tool_name, wheel_info)

        except Exception as e:
            self.logger.error(f"Failed to install tool {tool_name}: {e}")
            print(
                f"Error: Failed to install tool '{tool_name}'. Check logs for details."
            )
            return False

    def _install_wheel_based_tool(self, tool_name: str, wheel_info: Any) -> bool:
        """Install a wheel-based tool."""
        try:
            print(f"Installing wheel-based tool: {tool_name}")

            # Get dependencies from wheel
            dependencies = self.config_manager.get_tool_dependencies(tool_name)

            # Install wheel with dependencies
            print("Setting up environment and installing wheel...")
            success = self.env_manager.install_wheel_with_dependencies(
                tool_name, wheel_info.path, dependencies
            )

            if success:
                print(f"Successfully installed wheel-based tool: {tool_name}")
                return True
            else:
                print(f"Error: Failed to install wheel for '{tool_name}'.")
                return False

        except Exception as e:
            self.logger.error(f"Failed to install wheel-based tool {tool_name}: {e}")
            return False

    def run_tool(self, tool_name: str, args: Optional[List[str]] = None) -> int:
        """
        Run a tool with the given arguments.

        Args:
            tool_name: Name of the tool to run
            args: Arguments to pass to the tool

        Returns:
            Exit code from the tool
        """
        try:
            if args is None:
                args = []

            print(f"Running tool: {tool_name}")

            # Check if tool exists
            if not self.config_manager.tool_exists(tool_name):
                print(f"Error: Tool '{tool_name}' not found.")
                return 1

            # Load configuration
            config = self.config_manager.load_tool_config(tool_name)
            if not config:
                print(f"Error: Failed to load configuration for '{tool_name}'.")
                return 1

            # Ensure dependencies are satisfied
            print("Checking dependencies...")
            if not self.dependency_resolver.ensure_tool_dependencies(tool_name):
                print(f"Error: Failed to ensure dependencies for '{tool_name}'.")
                return 1

            # Determine how to run the tool
            command = self._build_run_command(config, args)
            if not command:
                print(f"Error: No valid entry point found for '{tool_name}'.")
                return 1

            print(f"Executing: {' '.join(command)}")

            # Run the tool in its environment
            result = self.env_manager.run_in_environment(
                tool_name, command, capture_output=False, check=False
            )

            return result.returncode

        except Exception as e:
            self.logger.error(f"Failed to run tool {tool_name}: {e}")
            print(f"Error: Failed to run tool '{tool_name}'. Check logs for details.")
            return 1

    def _build_run_command(self, config: Any, args: List[str]) -> Optional[List[str]]:
        """
        Build the command to run a wheel-based tool.

        Args:
            config: ToolConfig object
            args: Arguments to pass to the tool

        Returns:
            Command list or None if no valid entry point
        """
        # Get wheel info for the tool
        wheel_info = self.config_manager.get_wheel_info(config.name)

        if wheel_info and wheel_info.entry_points:
            # Use entry point from wheel
            entry_point_name = list(wheel_info.entry_points.keys())[0]
            return [entry_point_name] + args

        # Fallback to config entry point if available
        if config.entry_point:
            return [config.entry_point] + args

        # If no entry point found, this shouldn't happen for valid wheels
        self.logger.error(f"No entry point found for wheel-based tool {config.name}")
        return None

    def uninstall_tool(self, tool_name: str) -> bool:
        """
        Uninstall a tool by removing its environment.

        Args:
            tool_name: Name of the tool to uninstall

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Uninstalling tool: {tool_name}")

            if not self.env_manager.environment_exists(tool_name):
                print(f"Tool '{tool_name}' is not installed.")
                return True

            if self.env_manager.remove_environment(tool_name):
                print(f"Successfully uninstalled tool: {tool_name}")
                return True
            else:
                print(f"Error: Failed to uninstall tool '{tool_name}'.")
                return False

        except Exception as e:
            self.logger.error(f"Failed to uninstall tool {tool_name}: {e}")
            print(
                f"Error: Failed to uninstall tool '{tool_name}'. Check logs for details."
            )
            return False

    def show_tool_info(self, tool_name: str) -> None:
        """
        Show detailed information about a tool.

        Args:
            tool_name: Name of the tool
        """
        try:
            if not self.config_manager.tool_exists(tool_name):
                print(f"Error: Tool '{tool_name}' not found.")
                return

            config = self.config_manager.load_tool_config(tool_name)
            if not config:
                print(f"Error: Failed to load configuration for '{tool_name}'.")
                return

            # Basic info
            print(f"Tool: {config.name}")
            print(f"Version: {config.version}")
            print(f"Description: {config.description}")
            print(f"Author: {config.author}")
            print(f"License: {config.license}")
            print()

            # Environment status
            env_exists = self.env_manager.environment_exists(tool_name)
            print(f"Environment: {'Installed' if env_exists else 'Not installed'}")

            if env_exists:
                deps_satisfied = self.dependency_resolver.check_dependencies_satisfied(
                    tool_name
                )
                print(
                    f"Dependencies: {'Satisfied' if deps_satisfied else 'Missing/Outdated'}"
                )

            print()

            # Dependencies
            deps_info = self.dependency_resolver.get_dependency_info(tool_name)
            print("Dependencies:")
            required_deps = deps_info.get("required", [])
            missing_deps = deps_info.get("missing", [])

            if required_deps and isinstance(required_deps, list):
                for dep in required_deps:
                    status = (
                        "[OK]"
                        if isinstance(missing_deps, list) and dep not in missing_deps
                        else "[!]"
                    )
                    print(f"  {status} {dep}")
            else:
                print("  None")

        except Exception as e:
            self.logger.error(f"Failed to show info for tool {tool_name}: {e}")
            print(
                f"Error: Failed to get information for '{tool_name}'. Check logs for details."
            )

    def doctor(self) -> None:
        """Run diagnostic checks on the OSI system."""
        print("OSI System Diagnostics")
        print("=" * 50)

        # Python version check
        if validate_python_version():
            print("[OK] Python version is compatible")
        else:
            print("[!] Python version is too old (requires 3.11+)")

        # Platform info
        platform_info = get_platform_info()
        print(f"[OK] Platform: {platform_info['system']} {platform_info['machine']}")
        print(f"[OK] Python: {platform_info['python_version']}")

        # Check environments
        environments = self.env_manager.list_environments()
        print(f"[OK] Found {len(environments)} tool environments")

        # Check tools
        tools = self.config_manager.list_tools()
        print(f"[OK] Found {len(tools)} configured tools")

        # Check for issues
        issues = 0
        for tool_name in tools:
            if not self.config_manager.validate_tool_config(tool_name):
                print(f"[!] Tool '{tool_name}' has invalid configuration")
                issues += 1

        if issues == 0:
            print("[OK] All tool configurations are valid")

        print(f"\nDiagnostics complete. Found {issues} issues.")

    def clean(self) -> None:
        """Clean up all environments and caches."""
        print("Cleaning OSI system...")

        environments = self.env_manager.list_environments()
        for env_name in environments:
            print(f"Removing environment: {env_name}")
            self.env_manager.remove_environment(env_name)

        self.config_manager.clear_cache()
        print("Clean complete.")

    def list_kits(self) -> None:
        """List all available tool kits."""
        kits = self.config_manager.list_kits()

        if not kits:
            print("No kits available.")
            return

        print("Available kits:")
        print("-" * 50)

        for kit_name in kits:
            tools = self.config_manager.get_kit_tools(kit_name)
            print(f"{kit_name:<20} - {len(tools)} tools")
            for tool in tools[:3]:  # Show first 3 tools
                print(f"  • {tool}")
            if len(tools) > 3:
                print(f"  ... and {len(tools) - 3} more")

    def install_kit(self, kit_path: str) -> bool:
        """
        Install a kit from a directory containing wheel files.

        Args:
            kit_path: Path to directory containing .whl files

        Returns:
            True if successful, False otherwise
        """
        try:
            kit_path_obj = Path(kit_path)

            print(f"Installing kit from: {kit_path}")

            if not kit_path_obj.exists():
                print(f"Error: Kit path does not exist: {kit_path}")
                return False

            success = self.config_manager.install_kit(kit_path_obj)

            if success:
                print(f"Successfully installed kit from {kit_path}")
                return True
            else:
                print(f"Error: Failed to install kit from {kit_path}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to install kit: {e}")
            print(f"Error: Failed to install kit. Check logs for details.")
            return False

    def show_kit_info(self, kit_name: str) -> None:
        """
        Show detailed information about a kit.

        Args:
            kit_name: Name of the kit
        """
        try:
            tools = self.config_manager.get_kit_tools(kit_name)

            if not tools:
                print(f"Kit '{kit_name}' not found or contains no tools.")
                return

            print(f"Kit: {kit_name}")
            print(f"Tools: {len(tools)}")
            print("-" * 50)

            for tool_name in tools:
                config = self.config_manager.load_tool_config(tool_name)
                if config:
                    status = (
                        "[OK]" if self.env_manager.environment_exists(tool_name) else "[!]"
                    )
                    print(f"{status} {tool_name:<20} - {config.description}")
                else:
                    print(f"[!] {tool_name:<20} - (configuration error)")

        except Exception as e:
            self.logger.error(f"Failed to show kit info: {e}")
            print(f"Error: Failed to get kit information. Check logs for details.")


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="osi",
        description="OSI - Organized Software Installer for Python tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  osi list                    # List all available tools
  osi install my_tool         # Install a tool and its dependencies
  osi run my_tool --help      # Run a tool with arguments
  osi info my_tool            # Show detailed tool information
  osi doctor                  # Run system diagnostics
  osi clean                   # Clean all environments
        """,
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List all available tools")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a tool")
    install_parser.add_argument("tool", help="Name of the tool to install")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a tool")
    run_parser.add_argument("tool", help="Name of the tool to run")
    run_parser.add_argument("args", nargs="*", help="Arguments to pass to the tool")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a tool")
    uninstall_parser.add_argument("tool", help="Name of the tool to uninstall")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show tool information")
    info_parser.add_argument("tool", help="Name of the tool")

    # Doctor command
    subparsers.add_parser("doctor", help="Run system diagnostics")

    # Clean command
    subparsers.add_parser("clean", help="Clean all environments and caches")

    # Kit management commands
    subparsers.add_parser("list-kits", help="List all available tool kits")

    install_kit_parser = subparsers.add_parser(
        "install-kit", help="Install a kit from a directory"
    )
    install_kit_parser.add_argument(
        "kit_path", help="Path to directory containing .whl files"
    )

    kit_info_parser = subparsers.add_parser(
        "kit-info", help="Show information about a kit"
    )
    kit_info_parser.add_argument("kit", help="Name of the kit")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the OSI launcher.

    Args:
        argv: Command line arguments (defaults to sys.argv)

    Returns:
        Exit code
    """
    try:
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args(argv)

        # Set up logging
        log_level = "DEBUG" if args.verbose else args.log_level
        setup_logging(log_level)

        # Create launcher
        launcher = Launcher()

        # Handle commands
        if args.command == "list":
            launcher.list_tools()
            return 0

        elif args.command == "install":
            success = launcher.install_tool(args.tool)
            return 0 if success else 1

        elif args.command == "run":
            return launcher.run_tool(args.tool, args.args)

        elif args.command == "uninstall":
            success = launcher.uninstall_tool(args.tool)
            return 0 if success else 1

        elif args.command == "info":
            launcher.show_tool_info(args.tool)
            return 0

        elif args.command == "doctor":
            launcher.doctor()
            return 0

        elif args.command == "clean":
            launcher.clean()
            return 0

        elif args.command == "list-kits":
            launcher.list_kits()
            return 0

        elif args.command == "install-kit":
            success = launcher.install_kit(args.kit_path)
            return 0 if success else 1

        elif args.command == "kit-info":
            launcher.show_kit_info(args.kit)
            return 0

        else:
            # No command specified, show help
            parser.print_help()
            return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.getLogger(__name__).exception("Unexpected error in main")
        return 1


if __name__ == "__main__":
    sys.exit(main())

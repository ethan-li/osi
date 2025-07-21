"""
Dependency Resolver for OSI

Handles dependency resolution, version checking, and conflict detection
for tool installations.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from packaging import specifiers, version

from .config_manager import ConfigManager
from .environment_manager import EnvironmentManager


class DependencyResolver:
    """
    Resolves and manages dependencies for tools.

    Handles version checking, conflict detection, and dependency installation
    coordination between the configuration manager and environment manager.
    """

    def __init__(self) -> None:
        self.config_manager = ConfigManager()
        self.env_manager = EnvironmentManager()
        self.logger = logging.getLogger(__name__)

    def parse_requirement(self, requirement: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        Parse a requirement string into package name and version specifier.

        Args:
            requirement: Requirement string (e.g., "numpy>=1.20.0")

        Returns:
            Tuple of (package_name, version_specifier)
        """
        try:
            # Skip requirements with environment markers we don't want to install
            if "; extra ==" in requirement:
                self.logger.debug(f"Skipping conditional requirement: {requirement}")
                return None

            # Remove environment markers for platform-specific requirements
            if ";" in requirement:
                requirement = requirement.split(";")[0].strip()

            # Simple regex to parse package requirements
            match = re.match(r"^([a-zA-Z0-9_-]+)(.*)$", requirement.strip())
            if not match:
                return requirement.strip(), None

            package_name = match.group(1)
            version_spec = match.group(2).strip() if match.group(2) else None

            return package_name, version_spec

        except Exception as e:
            self.logger.warning(f"Failed to parse requirement '{requirement}': {e}")
            return requirement.strip(), None

    def check_version_compatibility(
        self, installed_version: str, required_spec: str
    ) -> bool:
        """
        Check if an installed version satisfies a requirement specification.

        Args:
            installed_version: Currently installed version
            required_spec: Required version specification (e.g., ">=1.20.0")

        Returns:
            True if compatible, False otherwise
        """
        try:
            if not required_spec:
                return True

            # Parse the version specifier
            spec = specifiers.SpecifierSet(required_spec)
            return version.parse(installed_version) in spec

        except Exception as e:
            self.logger.warning(f"Failed to check version compatibility: {e}")
            # If we can't parse, assume it's compatible
            return True

    def get_missing_dependencies(self, tool_name: str) -> List[str]:
        """
        Get a list of missing dependencies for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of missing dependency strings
        """
        try:
            # Get required dependencies
            required_deps = self.config_manager.get_tool_dependencies(tool_name)
            if not required_deps:
                return []

            # Get installed packages
            installed_packages = self.env_manager.get_installed_packages(tool_name)

            missing_deps = []

            for requirement in required_deps:
                parsed_req = self.parse_requirement(requirement)

                # Skip requirements that were filtered out (e.g., dev dependencies)
                if parsed_req is None:
                    continue

                package_name, version_spec = parsed_req

                if package_name not in installed_packages:
                    # Package not installed at all
                    missing_deps.append(requirement)
                elif version_spec:
                    # Check version compatibility
                    installed_version = installed_packages[package_name]
                    if not self.check_version_compatibility(
                        installed_version, version_spec
                    ):
                        missing_deps.append(requirement)

            return missing_deps

        except Exception as e:
            self.logger.error(
                f"Failed to check missing dependencies for {tool_name}: {e}"
            )
            return required_deps  # Return all as missing if we can't check

    def check_dependencies_satisfied(self, tool_name: str) -> bool:
        """
        Check if all dependencies for a tool are satisfied.

        Args:
            tool_name: Name of the tool

        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        missing_deps = self.get_missing_dependencies(tool_name)
        return len(missing_deps) == 0

    def install_missing_dependencies(self, tool_name: str) -> bool:
        """
        Install missing dependencies for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            True if successful, False otherwise
        """
        try:
            missing_deps = self.get_missing_dependencies(tool_name)

            if not missing_deps:
                self.logger.info(f"All dependencies satisfied for {tool_name}")
                return True

            self.logger.info(
                f"Installing missing dependencies for {tool_name}: {missing_deps}"
            )

            # Install missing dependencies
            success = self.env_manager.install_dependencies(tool_name, missing_deps)

            if success:
                self.logger.info(f"Successfully installed dependencies for {tool_name}")
            else:
                self.logger.error(f"Failed to install dependencies for {tool_name}")

            return success

        except Exception as e:
            self.logger.error(
                f"Failed to install missing dependencies for {tool_name}: {e}"
            )
            return False

    def detect_conflicts(self, tools: List[str]) -> Dict[str, List[str]]:
        """
        Detect potential dependency conflicts between tools.

        Args:
            tools: List of tool names to check

        Returns:
            Dictionary mapping package names to conflicting requirements
        """
        try:
            package_requirements: Dict[str, List[Dict[str, Any]]] = {}

            # Collect all requirements from all tools
            for tool_name in tools:
                requirements = self.config_manager.get_tool_dependencies(tool_name)

                for requirement in requirements:
                    parsed_req = self.parse_requirement(requirement)

                    if parsed_req is None:
                        continue

                    package_name, version_spec = parsed_req

                    if package_name not in package_requirements:
                        package_requirements[package_name] = []

                    package_requirements[package_name].append(
                        {
                            "tool": tool_name,
                            "requirement": requirement,
                            "version_spec": version_spec,
                        }
                    )

            # Check for conflicts
            conflicts: Dict[str, List[str]] = {}

            for package_name, req_list in package_requirements.items():
                if len(req_list) > 1:
                    # Multiple tools require this package, check for conflicts
                    version_specs = []
                    for req in req_list:
                        if req.get("version_spec"):
                            version_specs.append(req["version_spec"])

                    if len(set(version_specs)) > 1:
                        # Different version specifications - potential conflict
                        conflicts[package_name] = [req["requirement"] for req in req_list]

            return conflicts

        except Exception as e:
            self.logger.error(f"Failed to detect conflicts: {e}")
            return {}

    def ensure_tool_dependencies(self, tool_name: str) -> bool:
        """
        Ensure all dependencies for a tool are installed and up to date.

        This is the main method that should be called before running a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        try:
            self.logger.info(f"Ensuring dependencies for {tool_name}")

            # Check if environment exists
            if not self.env_manager.environment_exists(tool_name):
                self.logger.info(f"Creating environment for {tool_name}")
                if not self.env_manager.create_environment(tool_name):
                    return False

            # Validate environment
            if not self.env_manager.validate_environment(tool_name):
                self.logger.warning(
                    f"Environment for {tool_name} is invalid, recreating"
                )
                if not self.env_manager.create_environment(tool_name):
                    return False

            # Install missing dependencies
            if not self.install_missing_dependencies(tool_name):
                return False

            # Final validation
            if not self.check_dependencies_satisfied(tool_name):
                self.logger.error(f"Dependencies still not satisfied for {tool_name}")
                return False

            self.logger.info(f"All dependencies satisfied for {tool_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to ensure dependencies for {tool_name}: {e}")
            return False

    def get_dependency_info(self, tool_name: str) -> Dict[str, Union[List[str], Dict[str, str], bool]]:
        """
        Get detailed dependency information for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with dependency information
        """
        try:
            required_deps = self.config_manager.get_tool_dependencies(tool_name)
            installed_packages = self.env_manager.get_installed_packages(tool_name)
            missing_deps = self.get_missing_dependencies(tool_name)

            return {
                "required": required_deps,
                "installed": installed_packages,
                "missing": missing_deps,
                "satisfied": len(missing_deps) == 0,
            }

        except Exception as e:
            self.logger.error(f"Failed to get dependency info for {tool_name}: {e}")
            return {"required": [], "installed": {}, "missing": [], "satisfied": False}

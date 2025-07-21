"""
Environment Manager for OSI

Handles creation, management, and validation of isolated Python environments
for each tool to prevent dependency conflicts.
"""

import logging
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from packaging import version

from .utils import (
    ensure_directory,
    get_environments_dir,
    get_python_executable,
    is_windows,
    run_command,
    sanitize_name,
)


class EnvironmentManager:
    """
    Manages isolated Python environments for tools.

    Each tool gets its own virtual environment to prevent dependency conflicts.
    Environments are automatically created, validated, and maintained.
    """

    def __init__(self) -> None:
        self.environments_dir = get_environments_dir()
        self.logger = logging.getLogger(__name__)
        ensure_directory(self.environments_dir)

    def get_environment_path(self, tool_name: str) -> Path:
        """
        Get the path to a tool's environment directory.

        Args:
            tool_name: Name of the tool

        Returns:
            Path to the environment directory
        """
        sanitized_name = sanitize_name(tool_name)
        return self.environments_dir / sanitized_name

    def get_environment_python(self, tool_name: str) -> Path:
        """
        Get the path to the Python executable in a tool's environment.

        Args:
            tool_name: Name of the tool

        Returns:
            Path to the Python executable
        """
        env_path = self.get_environment_path(tool_name)

        if is_windows():
            return env_path / "Scripts" / "python.exe"
        else:
            return env_path / "bin" / "python"

    def get_environment_pip(self, tool_name: str) -> Path:
        """
        Get the path to the pip executable in a tool's environment.

        Args:
            tool_name: Name of the tool

        Returns:
            Path to the pip executable
        """
        env_path = self.get_environment_path(tool_name)

        if is_windows():
            return env_path / "Scripts" / "pip.exe"
        else:
            return env_path / "bin" / "pip"

    def environment_exists(self, tool_name: str) -> bool:
        """
        Check if an environment exists for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            True if environment exists, False otherwise
        """
        env_path = self.get_environment_path(tool_name)
        python_path = self.get_environment_python(tool_name)

        return env_path.exists() and python_path.exists()

    def create_environment(
        self, tool_name: str, python_version: Optional[str] = None
    ) -> bool:
        """
        Create a new virtual environment for a tool.

        Args:
            tool_name: Name of the tool
            python_version: Specific Python version to use (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            env_path = self.get_environment_path(tool_name)

            self.logger.info(f"Creating environment for {tool_name} at {env_path}")

            # Remove existing environment if it exists
            if env_path.exists():
                self.logger.info(f"Removing existing environment for {tool_name}")
                self.remove_environment(tool_name)

            # Create the environment
            venv.create(env_path, with_pip=True, clear=True)

            # Upgrade pip to latest version
            self.logger.info(f"Upgrading pip in {tool_name} environment")
            pip_path = self.get_environment_pip(tool_name)
            run_command([str(pip_path), "install", "--upgrade", "pip"])

            self.logger.info(f"Successfully created environment for {tool_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create environment for {tool_name}: {e}")
            return False

    def remove_environment(self, tool_name: str) -> bool:
        """
        Remove an environment for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            True if successful, False otherwise
        """
        try:
            env_path = self.get_environment_path(tool_name)

            if env_path.exists():
                self.logger.info(f"Removing environment for {tool_name}")
                shutil.rmtree(env_path)
                self.logger.info(f"Successfully removed environment for {tool_name}")
            else:
                self.logger.info(f"Environment for {tool_name} does not exist")

            return True

        except Exception as e:
            self.logger.error(f"Failed to remove environment for {tool_name}: {e}")
            return False

    def install_dependencies(self, tool_name: str, requirements: List[str]) -> bool:
        """
        Install dependencies in a tool's environment.

        Args:
            tool_name: Name of the tool
            requirements: List of requirement strings (e.g., ["numpy>=1.20", "requests"])

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.environment_exists(tool_name):
                self.logger.error(f"Environment for {tool_name} does not exist")
                return False

            pip_path = self.get_environment_pip(tool_name)

            self.logger.info(f"Installing dependencies for {tool_name}: {requirements}")

            # Install each requirement
            for requirement in requirements:
                self.logger.info(f"Installing {requirement}")
                run_command([str(pip_path), "install", requirement])

            self.logger.info(f"Successfully installed dependencies for {tool_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to install dependencies for {tool_name}: {e}")
            return False

    def install_from_requirements_file(
        self, tool_name: str, requirements_file: Path
    ) -> bool:
        """
        Install dependencies from a requirements.txt file.

        Args:
            tool_name: Name of the tool
            requirements_file: Path to requirements.txt file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.environment_exists(tool_name):
                self.logger.error(f"Environment for {tool_name} does not exist")
                return False

            if not requirements_file.exists():
                self.logger.error(f"Requirements file not found: {requirements_file}")
                return False

            pip_path = self.get_environment_pip(tool_name)

            self.logger.info(f"Installing dependencies from {requirements_file}")
            run_command([str(pip_path), "install", "-r", str(requirements_file)])

            self.logger.info(
                f"Successfully installed dependencies from {requirements_file}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to install from requirements file: {e}")
            return False

    def get_installed_packages(self, tool_name: str) -> Dict[str, str]:
        """
        Get a list of installed packages in a tool's environment.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary mapping package names to versions
        """
        try:
            if not self.environment_exists(tool_name):
                self.logger.error(f"Environment for {tool_name} does not exist")
                return {}

            pip_path = self.get_environment_pip(tool_name)
            result = run_command([str(pip_path), "list", "--format=freeze"])

            packages = {}
            for line in result.stdout.strip().split("\n"):
                if "==" in line:
                    name, version_str = line.split("==", 1)
                    packages[name] = version_str

            return packages

        except Exception as e:
            self.logger.error(f"Failed to get installed packages for {tool_name}: {e}")
            return {}

    def validate_environment(
        self, tool_name: str, required_packages: Optional[List[str]] = None
    ) -> bool:
        """
        Validate that an environment exists and has required packages.

        Args:
            tool_name: Name of the tool
            required_packages: List of required packages (optional)

        Returns:
            True if environment is valid, False otherwise
        """
        try:
            # Check if environment exists
            if not self.environment_exists(tool_name):
                self.logger.warning(f"Environment for {tool_name} does not exist")
                return False

            # Check if Python executable works
            python_path = self.get_environment_python(tool_name)
            try:
                run_command([str(python_path), "--version"], timeout=10)
            except Exception as e:
                self.logger.error(
                    f"Python executable not working in {tool_name} environment: {e}"
                )
                return False

            # Check required packages if specified
            if required_packages:
                installed_packages = self.get_installed_packages(tool_name)
                for package in required_packages:
                    # Simple package name check (could be enhanced for version checking)
                    package_name = (
                        package.split(">=")[0].split("==")[0].split("<")[0].strip()
                    )
                    if package_name not in installed_packages:
                        self.logger.warning(
                            f"Required package {package_name} not found in {tool_name} environment"
                        )
                        return False

            self.logger.info(f"Environment for {tool_name} is valid")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate environment for {tool_name}: {e}")
            return False

    def list_environments(self) -> List[str]:
        """
        List all existing tool environments.

        Returns:
            List of tool names that have environments
        """
        try:
            if not self.environments_dir.exists():
                return []

            environments = []
            for item in self.environments_dir.iterdir():
                if item.is_dir():
                    # Check if it's a valid environment
                    if self.environment_exists(item.name):
                        environments.append(item.name)

            return sorted(environments)

        except Exception as e:
            self.logger.error(f"Failed to list environments: {e}")
            return []

    def run_in_environment(
        self, tool_name: str, command: List[str], **kwargs: Any
    ) -> subprocess.CompletedProcess:
        """
        Run a command in a tool's environment.

        Args:
            tool_name: Name of the tool
            command: Command and arguments to run
            **kwargs: Additional arguments for run_command

        Returns:
            CompletedProcess object

        Raises:
            RuntimeError: If environment doesn't exist
            subprocess.CalledProcessError: If command fails
        """
        if not self.environment_exists(tool_name):
            raise RuntimeError(f"Environment for {tool_name} does not exist")

        python_path = self.get_environment_python(tool_name)
        env_path = self.get_environment_path(tool_name)

        # Set up environment variables to use the virtual environment
        env = kwargs.get("env", os.environ.copy())

        if is_windows():
            scripts_dir = env_path / "Scripts"
            env["PATH"] = f"{scripts_dir}{os.pathsep}{env.get('PATH', '')}"
        else:
            bin_dir = env_path / "bin"
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"

        # Set virtual environment variables
        env["VIRTUAL_ENV"] = str(env_path)
        env.pop("PYTHONHOME", None)  # Remove PYTHONHOME if set

        kwargs["env"] = env

        # If the command starts with 'python', replace it with the environment's python
        if command and command[0] in ["python", "python3"]:
            command[0] = str(python_path)

        return run_command(command, **kwargs)

    def install_wheel(self, tool_name: str, wheel_path: Path) -> bool:
        """
        Install a wheel file into a tool's environment.

        Args:
            tool_name: Name of the tool
            wheel_path: Path to the wheel file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.environment_exists(tool_name):
                self.logger.error(f"Environment for {tool_name} does not exist")
                return False

            if not wheel_path.exists():
                self.logger.error(f"Wheel file not found: {wheel_path}")
                return False

            pip_path = self.get_environment_pip(tool_name)

            self.logger.info(f"Installing wheel {wheel_path.name} for {tool_name}")
            run_command([str(pip_path), "install", str(wheel_path)])

            self.logger.info(f"Successfully installed wheel for {tool_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to install wheel for {tool_name}: {e}")
            return False

    def install_wheel_with_dependencies(
        self, tool_name: str, wheel_path: Path, dependencies: Optional[List[str]] = None
    ) -> bool:
        """
        Install a wheel file and its dependencies into a tool's environment.

        Args:
            tool_name: Name of the tool
            wheel_path: Path to the wheel file
            dependencies: Additional dependencies to install

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.environment_exists(tool_name):
                if not self.create_environment(tool_name):
                    return False

            # Install dependencies first if provided
            if dependencies:
                if not self.install_dependencies(tool_name, dependencies):
                    self.logger.error(f"Failed to install dependencies for {tool_name}")
                    return False

            # Install the wheel
            if not self.install_wheel(tool_name, wheel_path):
                return False

            self.logger.info(
                f"Successfully installed wheel and dependencies for {tool_name}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to install wheel with dependencies for {tool_name}: {e}"
            )
            return False

    def get_wheel_entry_points(self, tool_name: str) -> Dict[str, str]:
        """
        Get entry points for a wheel-based tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary of entry point names to targets
        """
        try:
            if not self.environment_exists(tool_name):
                return {}

            pip_path = self.get_environment_pip(tool_name)

            # Get installed package info
            result = run_command([str(pip_path), "show", tool_name])

            # This is a simplified approach - in practice, you might want to
            # parse the entry_points.txt file from the installed package
            return {}

        except Exception as e:
            self.logger.error(f"Failed to get entry points for {tool_name}: {e}")
            return {}

    def is_wheel_installed(self, tool_name: str, wheel_name: str) -> bool:
        """
        Check if a specific wheel is installed in a tool's environment.

        Args:
            tool_name: Name of the tool
            wheel_name: Name of the wheel package

        Returns:
            True if wheel is installed, False otherwise
        """
        try:
            if not self.environment_exists(tool_name):
                return False

            installed_packages = self.get_installed_packages(tool_name)
            return wheel_name in installed_packages

        except Exception as e:
            self.logger.error(f"Failed to check if wheel is installed: {e}")
            return False

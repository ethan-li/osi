"""
Utility functions for OSI
"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_platform_info() -> Dict[str, str]:
    """Get platform information for cross-platform compatibility."""
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system().lower() == "windows"


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system().lower() == "darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system().lower() == "linux"


def get_executable_extension() -> str:
    """Get the executable extension for the current platform."""
    return ".exe" if is_windows() else ""


def get_script_extension() -> str:
    """Get the script extension for the current platform."""
    return ".bat" if is_windows() else ".sh"


def get_osi_root() -> Path:
    """Get the root directory of the OSI installation."""
    if is_executable_mode():
        # In executable mode, use user's home directory for persistent data
        return Path.home() / ".osi"
    else:
        # Get the directory containing this file, then go up one level
        return Path(__file__).parent.parent.absolute()


def get_environments_dir() -> Path:
    """Get the environments directory."""
    if is_executable_mode():
        # In executable mode, use user's home directory to avoid temp directory issues
        return Path.home() / ".osi" / "environments"
    else:
        return get_osi_root() / "environments"


def get_logs_dir() -> Path:
    """Get the logs directory."""
    return get_osi_root() / "logs"


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def run_command(
    command: List[str],
    cwd: Optional[Path] = None,
    capture_output: bool = True,
    check: bool = True,
    timeout: Optional[int] = None,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    """
    Run a command with proper error handling.

    Args:
        command: Command and arguments as a list
        cwd: Working directory for the command
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise exception on non-zero exit
        timeout: Timeout in seconds
        env: Environment variables for the command

    Returns:
        CompletedProcess object

    Raises:
        subprocess.CalledProcessError: If command fails and check=True
        subprocess.TimeoutExpired: If command times out
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check,
            timeout=timeout,
            env=env,
        )
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(command)}")
        logging.error(f"Exit code: {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        raise
    except subprocess.TimeoutExpired as e:
        logging.error(f"Command timed out: {' '.join(command)}")
        raise


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    logs_dir = get_logs_dir()
    ensure_directory(logs_dir)

    log_file = logs_dir / "osi.log"

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


def validate_python_version(min_version: str = "3.11") -> bool:
    """
    Validate that the current Python version meets minimum requirements.

    Args:
        min_version: Minimum required Python version (e.g., "3.11")

    Returns:
        True if version is sufficient, False otherwise
    """
    current_version = sys.version_info
    min_parts = [int(x) for x in min_version.split(".")]

    # Compare major.minor version
    current_major_minor = (current_version.major, current_version.minor)
    min_major_minor = tuple(min_parts[:2])

    return current_major_minor >= min_major_minor


def get_python_executable() -> str:
    """Get the path to the current Python executable."""
    return sys.executable


def sanitize_name(name: str) -> str:
    """
    Sanitize a name for use as a directory or environment name.

    Args:
        name: The name to sanitize

    Returns:
        Sanitized name safe for filesystem use
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    sanitized = name
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(". ")

    # Ensure it's not empty
    if not sanitized:
        sanitized = "unnamed_tool"

    return sanitized


def is_executable_mode() -> bool:
    """Check if OSI is running as a PyInstaller executable."""
    return getattr(sys, "frozen", False) or os.environ.get("OSI_EXECUTABLE_MODE") == "1"


def get_resource_path(relative_path: str = "") -> Path:
    """Get absolute path to resource, works for dev and PyInstaller executable."""
    if is_executable_mode():
        # Running as PyInstaller executable
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller temp directory
            base_path = Path(sys._MEIPASS)
        else:
            # Fallback to environment variable
            base_path = Path(
                os.environ.get(
                    "OSI_RESOURCE_PATH", os.path.dirname(os.path.abspath(__file__))
                )
            )
    else:
        # Running in development mode
        base_path = Path(__file__).parent.parent

    if relative_path:
        return base_path / relative_path
    return base_path


def get_default_kits_paths() -> List[Path]:
    """Get default paths to search for kits, handling executable mode."""
    paths = []

    if is_executable_mode():
        # In executable mode, check environment variable first
        env_kits_path = os.environ.get("OSI_KITS_PATH")
        if env_kits_path:
            paths.append(Path(env_kits_path))

        # Also check resource path
        resource_kits = get_resource_path("kits")
        if resource_kits.exists():
            paths.append(resource_kits)
    else:
        # Development mode - use standard paths
        project_root = Path(__file__).parent.parent
        paths.append(project_root / "kits")

    # Always include user's home directory
    home_kits = Path.home() / ".osi" / "kits"
    if home_kits not in paths:
        paths.append(home_kits)

    return [p for p in paths if p.exists()]


def get_default_wheels_paths() -> List[Path]:
    """Get default paths to search for wheels, handling executable mode."""
    paths = []

    if is_executable_mode():
        # In executable mode, check environment variable first
        env_wheels_path = os.environ.get("OSI_WHEELS_PATH")
        if env_wheels_path:
            paths.append(Path(env_wheels_path))

        # Also check resource path
        resource_wheels = get_resource_path("wheels")
        if resource_wheels.exists():
            paths.append(resource_wheels)
    else:
        # Development mode - use standard paths
        project_root = Path(__file__).parent.parent
        paths.append(project_root / "wheels")

    # Always include user's home directory
    home_wheels = Path.home() / ".osi" / "wheels"
    if home_wheels not in paths:
        paths.append(home_wheels)

    return [p for p in paths if p.exists()]

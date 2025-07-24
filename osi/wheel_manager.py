"""
Wheel Manager for OSI

Handles discovery, validation, and management of .whl files for tool distribution.
Supports kit-based distribution where multiple tools are packaged together.
"""

import email.message
import email.parser
import logging
import os
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Optional dependency handling
pkginfo: Any = None
try:
    import pkginfo
except ImportError:
    pass

from .utils import (
    ensure_directory,
    get_default_kits_paths,
    get_default_wheels_paths,
    get_osi_root,
    sanitize_name,
)


@dataclass
class WheelInfo:
    """Information about a wheel file."""

    name: str
    version: str
    filename: str
    path: Path
    metadata: Dict[str, Any]
    dependencies: List[str]
    entry_points: Dict[str, str]
    python_requires: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None

    @property
    def tool_name(self) -> str:
        """Get the tool name (sanitized package name)."""
        return sanitize_name(self.name)


class WheelManager:
    """
    Manages wheel files for OSI tool distribution.

    Handles discovery, validation, and metadata extraction from .whl files.
    Supports both individual wheels and kit-based distributions.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.osi_root = get_osi_root()

        # Use new resource path functions for executable compatibility
        self.wheels_paths = get_default_wheels_paths()
        self.kits_paths = get_default_kits_paths()

        # Maintain backward compatibility
        self.wheels_dir = self.osi_root / "wheels"
        self.kits_dir = self.osi_root / "kits"

        self._wheel_cache: Dict[str, WheelInfo] = {}

        # Ensure directories exist
        ensure_directory(self.wheels_dir)
        ensure_directory(self.kits_dir)

    def discover_wheels(
        self, search_paths: Optional[List[Path]] = None
    ) -> List[WheelInfo]:
        """
        Discover all wheel files in the specified paths.

        Args:
            search_paths: List of paths to search for wheels. If None, uses default paths.

        Returns:
            List of WheelInfo objects for discovered wheels
        """
        if search_paths is None:
            # Use new resource-aware paths for executable compatibility
            search_paths = self.wheels_paths + self.kits_paths

        wheels = []

        for search_path in search_paths:
            if not search_path.exists():
                continue

            self.logger.info(f"Searching for wheels in {search_path}")

            # Find all .whl files recursively
            for wheel_path in search_path.rglob("*.whl"):
                try:
                    wheel_info = self.get_wheel_info(wheel_path)
                    if wheel_info:
                        wheels.append(wheel_info)
                        self.logger.debug(
                            f"Found wheel: {wheel_info.name} v{wheel_info.version}"
                        )
                except Exception as e:
                    self.logger.warning(f"Failed to process wheel {wheel_path}: {e}")

        self.logger.info(f"Discovered {len(wheels)} wheels")
        return wheels

    def get_wheel_info(
        self, wheel_path: Path, use_cache: bool = True
    ) -> Optional[WheelInfo]:
        """
        Extract information from a wheel file.

        Args:
            wheel_path: Path to the wheel file
            use_cache: Whether to use cached information

        Returns:
            WheelInfo object or None if extraction fails
        """
        wheel_key = str(wheel_path.absolute())

        # Check cache first
        if use_cache and wheel_key in self._wheel_cache:
            return self._wheel_cache[wheel_key]

        try:
            if not wheel_path.exists() or not wheel_path.name.endswith(".whl"):
                return None

            # Use pkginfo if available for better metadata extraction
            # Note: pkginfo doesn't handle entry points well, so we'll use manual extraction
            # but keep pkginfo for other metadata if needed
            # Temporarily disable pkginfo due to entry points handling issues
            use_pkginfo = False
            if use_pkginfo and pkginfo:
                self.logger.debug(
                    f"Using pkginfo to extract metadata from {wheel_path}"
                )
                wheel_metadata = pkginfo.Wheel(str(wheel_path))
                if wheel_metadata:
                    wheel_info = self._create_wheel_info_from_pkginfo(
                        wheel_path, wheel_metadata
                    )
                    self.logger.debug(
                        f"pkginfo extracted entry points: {wheel_info.entry_points}"
                    )
                    self._wheel_cache[wheel_key] = wheel_info
                    return wheel_info
                else:
                    self.logger.debug(
                        f"pkginfo failed to extract metadata from {wheel_path}"
                    )

            # Fallback to manual extraction
            self.logger.debug(f"Falling back to manual extraction for {wheel_path}")
            manual_wheel_info = self._extract_wheel_info_manually(wheel_path)
            if manual_wheel_info:
                self.logger.debug(
                    f"Manual extraction entry points: {manual_wheel_info.entry_points}"
                )
                self._wheel_cache[wheel_key] = manual_wheel_info

            return manual_wheel_info

        except Exception as e:
            self.logger.error(f"Failed to extract wheel info from {wheel_path}: {e}")
            return None

    def _create_wheel_info_from_pkginfo(
        self, wheel_path: Path, metadata: Any
    ) -> WheelInfo:
        """Create WheelInfo from pkginfo metadata."""
        # Extract entry points
        entry_points = {}
        if hasattr(metadata, "entry_points") and metadata.entry_points:
            entry_points = self._parse_entry_points(metadata.entry_points)

        # Extract dependencies
        dependencies = []
        if hasattr(metadata, "requires_dist") and metadata.requires_dist:
            dependencies = list(metadata.requires_dist)

        return WheelInfo(
            name=metadata.name,
            version=metadata.version,
            filename=wheel_path.name,
            path=wheel_path,
            metadata={
                "name": metadata.name,
                "version": metadata.version,
                "summary": metadata.summary,
                "author": metadata.author,
                "license": metadata.license,
                "home_page": metadata.home_page,
            },
            dependencies=dependencies,
            entry_points=entry_points,
            python_requires=getattr(metadata, "requires_python", None),
            summary=metadata.summary,
            author=metadata.author,
            license=metadata.license,
            homepage=metadata.home_page,
        )

    def _extract_wheel_info_manually(self, wheel_path: Path) -> Optional[WheelInfo]:
        """Manually extract wheel information from the wheel file."""
        try:
            with zipfile.ZipFile(wheel_path, "r") as wheel_zip:
                # Find METADATA file
                metadata_files = [
                    f for f in wheel_zip.namelist() if f.endswith("/METADATA")
                ]
                if not metadata_files:
                    self.logger.warning(f"No METADATA file found in {wheel_path}")
                    return None

                # Read metadata
                metadata_content = wheel_zip.read(metadata_files[0]).decode("utf-8")
                metadata = self._parse_metadata(metadata_content)

                # Find entry_points.txt if it exists
                entry_points = {}
                entry_points_files = [
                    f for f in wheel_zip.namelist() if f.endswith("/entry_points.txt")
                ]
                if entry_points_files:
                    entry_points_content = wheel_zip.read(entry_points_files[0]).decode(
                        "utf-8"
                    )
                    self.logger.debug(f"Entry points content: {entry_points_content}")
                    entry_points = self._parse_entry_points(entry_points_content)
                    self.logger.debug(f"Parsed entry points: {entry_points}")
                else:
                    self.logger.debug(f"No entry_points.txt found in {wheel_path}")

                # Extract basic info from filename
                filename_parts = wheel_path.stem.split("-")
                if len(filename_parts) >= 2:
                    name = filename_parts[0]
                    version = filename_parts[1]
                else:
                    name = metadata.get("Name", wheel_path.stem)
                    version = metadata.get("Version", "0.0.0")

                return WheelInfo(
                    name=name,
                    version=version,
                    filename=wheel_path.name,
                    path=wheel_path,
                    metadata=metadata,
                    dependencies=metadata.get("Requires-Dist", []),
                    entry_points=entry_points,
                    python_requires=metadata.get("Requires-Python"),
                    summary=metadata.get("Summary"),
                    author=metadata.get("Author"),
                    license=metadata.get("License"),
                    homepage=metadata.get("Home-page"),
                )

        except Exception as e:
            self.logger.error(f"Failed to manually extract wheel info: {e}")
            return None

    def _parse_metadata(self, metadata_content: str) -> Dict[str, Any]:
        """Parse wheel METADATA file content."""
        try:
            # Parse as email message format
            parser = email.parser.Parser()
            msg = parser.parsestr(metadata_content)

            metadata: Dict[str, Union[str, List[str]]] = {}
            for key, value in msg.items():
                if key in metadata:
                    # Handle multiple values (like Requires-Dist)
                    existing_value = metadata[key]
                    if not isinstance(existing_value, list):
                        metadata[key] = [existing_value, value]
                    else:
                        existing_value.append(value)
                else:
                    metadata[key] = value

            return metadata

        except Exception as e:
            self.logger.warning(f"Failed to parse metadata: {e}")
            return {}

    def _parse_entry_points(self, entry_points_content: str) -> Dict[str, str]:
        """Parse entry points from entry_points.txt or metadata."""
        entry_points = {}

        try:
            current_section = None
            for line in entry_points_content.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                    continue

                if current_section == "console_scripts" and "=" in line:
                    name, target = line.split("=", 1)
                    entry_points[name.strip()] = target.strip()

        except Exception as e:
            self.logger.warning(f"Failed to parse entry points: {e}")

        return entry_points

    def find_wheel_by_name(
        self, tool_name: str, search_paths: Optional[List[Path]] = None
    ) -> Optional[WheelInfo]:
        """
        Find a wheel by tool name.

        Args:
            tool_name: Name of the tool to find
            search_paths: Paths to search in

        Returns:
            WheelInfo object or None if not found
        """
        wheels = self.discover_wheels(search_paths)

        for wheel in wheels:
            # Check by tool name (sanitized package name)
            if wheel.tool_name == sanitize_name(tool_name):
                return wheel
            # Check by package name
            if wheel.name == tool_name:
                return wheel
            # Check by entry point names
            if wheel.entry_points and tool_name in wheel.entry_points:
                return wheel

        return None

    def list_available_tools(
        self, search_paths: Optional[List[Path]] = None
    ) -> List[WheelInfo]:
        """
        List all available tools from wheels.

        Args:
            search_paths: Paths to search in

        Returns:
            List of WheelInfo objects for available tools
        """
        return self.discover_wheels(search_paths)

    def validate_wheel(self, wheel_path: Path) -> bool:
        """
        Validate that a wheel file is properly formatted and readable.

        Args:
            wheel_path: Path to the wheel file

        Returns:
            True if wheel is valid, False otherwise
        """
        try:
            if not wheel_path.exists() or not wheel_path.name.endswith(".whl"):
                return False

            # Try to extract basic info
            wheel_info = self.get_wheel_info(wheel_path, use_cache=False)
            return wheel_info is not None

        except Exception as e:
            self.logger.error(f"Wheel validation failed for {wheel_path}: {e}")
            return False

    def install_wheel_to_kit(self, wheel_path: Path, kit_name: str) -> bool:
        """
        Install a wheel file to a specific kit directory.

        Args:
            wheel_path: Path to the wheel file
            kit_name: Name of the kit to install to

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.validate_wheel(wheel_path):
                self.logger.error(f"Invalid wheel file: {wheel_path}")
                return False

            kit_dir = self.kits_dir / sanitize_name(kit_name)
            ensure_directory(kit_dir)

            dest_path = kit_dir / wheel_path.name

            if dest_path.exists():
                self.logger.warning(f"Wheel already exists in kit: {dest_path}")
                return True

            shutil.copy2(wheel_path, dest_path)
            self.logger.info(f"Installed wheel {wheel_path.name} to kit {kit_name}")

            # Clear cache for this wheel
            wheel_key = str(dest_path.absolute())
            if wheel_key in self._wheel_cache:
                del self._wheel_cache[wheel_key]

            return True

        except Exception as e:
            self.logger.error(f"Failed to install wheel to kit: {e}")
            return False

    def list_kits(self) -> List[str]:
        """
        List all available kits.

        Returns:
            List of kit names
        """
        try:
            if not self.kits_dir.exists():
                return []

            kits = []
            for item in self.kits_dir.iterdir():
                if item.is_dir():
                    # Check if kit contains any wheels
                    wheels = list(item.glob("*.whl"))
                    if wheels:
                        kits.append(item.name)

            return sorted(kits)

        except Exception as e:
            self.logger.error(f"Failed to list kits: {e}")
            return []

    def get_kit_tools(self, kit_name: str) -> List[WheelInfo]:
        """
        Get all tools in a specific kit.

        Args:
            kit_name: Name of the kit

        Returns:
            List of WheelInfo objects for tools in the kit
        """
        kit_dir = self.kits_dir / sanitize_name(kit_name)
        if not kit_dir.exists():
            return []

        return self.discover_wheels([kit_dir])

    def create_kit_from_wheels(self, kit_name: str, wheel_paths: List[Path]) -> bool:
        """
        Create a new kit from a list of wheel files.

        Args:
            kit_name: Name of the new kit
            wheel_paths: List of paths to wheel files

        Returns:
            True if successful, False otherwise
        """
        try:
            kit_dir = self.kits_dir / sanitize_name(kit_name)
            ensure_directory(kit_dir)

            success_count = 0
            for wheel_path in wheel_paths:
                if self.install_wheel_to_kit(wheel_path, kit_name):
                    success_count += 1

            self.logger.info(
                f"Created kit {kit_name} with {success_count}/{len(wheel_paths)} wheels"
            )
            return success_count > 0

        except Exception as e:
            self.logger.error(f"Failed to create kit: {e}")
            return False

    def remove_kit(self, kit_name: str) -> bool:
        """
        Remove a kit and all its wheels.

        Args:
            kit_name: Name of the kit to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            kit_dir = self.kits_dir / sanitize_name(kit_name)
            if kit_dir.exists():
                shutil.rmtree(kit_dir)
                self.logger.info(f"Removed kit {kit_name}")

                # Clear cache for wheels in this kit
                for key in list(self._wheel_cache.keys()):
                    if str(kit_dir) in key:
                        del self._wheel_cache[key]

                return True
            else:
                self.logger.warning(f"Kit {kit_name} does not exist")
                return False

        except Exception as e:
            self.logger.error(f"Failed to remove kit {kit_name}: {e}")
            return False

    def clear_cache(self) -> None:
        """Clear the wheel information cache."""
        self._wheel_cache.clear()
        self.logger.info("Wheel cache cleared")

    def get_wheel_dependencies(self, wheel_info: WheelInfo) -> List[str]:
        """
        Get the dependencies for a wheel.

        Args:
            wheel_info: WheelInfo object

        Returns:
            List of dependency strings
        """
        return wheel_info.dependencies if wheel_info.dependencies else []

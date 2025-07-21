"""
Tool Configuration Classes for OSI

Contains the ToolConfig dataclass and related configuration structures.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolConfig:
    """
    Configuration for a single tool.
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = ""

    # Python requirements
    python_version: str = ">=3.11"
    dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)

    # Entry points and execution
    entry_point: Optional[str] = None
    module: Optional[str] = None
    script: Optional[str] = None
    command: Optional[List[str]] = None

    # Platform-specific settings
    windows_only: bool = False
    linux_only: bool = False
    macos_only: bool = False

    # Additional metadata
    homepage: str = ""
    repository: str = ""
    documentation: str = ""
    keywords: List[str] = field(default_factory=list)

    # Installation settings
    pre_install_commands: List[str] = field(default_factory=list)
    post_install_commands: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolConfig":
        """Create ToolConfig from dictionary data."""
        # Extract main tool info
        tool_info = data.get("tool", {})

        # Extract dependencies
        dependencies_info = data.get("dependencies", {})

        # Extract entry points
        entry_points = data.get("entry_points", {})

        # Extract platform info
        platform_info = data.get("platform", {})

        # Extract installation info
        install_info = data.get("install", {})

        return cls(
            name=tool_info.get("name", ""),
            version=tool_info.get("version", "1.0.0"),
            description=tool_info.get("description", ""),
            author=tool_info.get("author", ""),
            license=tool_info.get("license", ""),
            python_version=dependencies_info.get("python", ">=3.11"),
            dependencies=dependencies_info.get("packages", []),
            dev_dependencies=dependencies_info.get("dev_packages", []),
            entry_point=entry_points.get("console_script"),
            module=entry_points.get("module"),
            script=entry_points.get("script"),
            command=entry_points.get("command"),
            windows_only=platform_info.get("windows_only", False),
            linux_only=platform_info.get("linux_only", False),
            macos_only=platform_info.get("macos_only", False),
            homepage=tool_info.get("homepage", ""),
            repository=tool_info.get("repository", ""),
            documentation=tool_info.get("documentation", ""),
            keywords=tool_info.get("keywords", []),
            pre_install_commands=install_info.get("pre_install", []),
            post_install_commands=install_info.get("post_install", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ToolConfig to dictionary."""
        return {
            "tool": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "author": self.author,
                "license": self.license,
                "homepage": self.homepage,
                "repository": self.repository,
                "documentation": self.documentation,
                "keywords": self.keywords,
            },
            "dependencies": {
                "python": self.python_version,
                "packages": self.dependencies,
                "dev_packages": self.dev_dependencies,
            },
            "entry_points": {
                "console_script": self.entry_point,
                "module": self.module,
                "script": self.script,
                "command": self.command,
            },
            "platform": {
                "windows_only": self.windows_only,
                "linux_only": self.linux_only,
                "macos_only": self.macos_only,
            },
            "install": {
                "pre_install": self.pre_install_commands,
                "post_install": self.post_install_commands,
            },
        }

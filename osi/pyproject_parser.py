"""
PyProject.toml Parser for OSI

Handles parsing of standard pyproject.toml files to extract tool metadata
and configuration for OSI tool management.
"""

import logging
import toml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from .tool_config import ToolConfig
from .wheel_manager import WheelInfo


@dataclass
class PyProjectConfig:
    """
    Configuration extracted from pyproject.toml file.
    """
    # Project metadata
    name: str
    version: str = "1.0.0"
    description: str = ""
    authors: List[str] = field(default_factory=list)
    license: str = ""
    readme: str = ""
    homepage: str = ""
    repository: str = ""
    documentation: str = ""
    keywords: List[str] = field(default_factory=list)
    classifiers: List[str] = field(default_factory=list)
    
    # Dependencies
    python_requires: str = ">=3.11"
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    # Entry points
    console_scripts: Dict[str, str] = field(default_factory=dict)
    gui_scripts: Dict[str, str] = field(default_factory=dict)
    
    # OSI-specific configuration
    osi_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_tool_config(self) -> ToolConfig:
        """Convert PyProjectConfig to ToolConfig for backward compatibility."""
        # Determine entry point method
        entry_point = None
        module = None
        script = None
        command = None
        
        # Check for console scripts first
        if self.console_scripts:
            # Use the first console script as the entry point
            entry_point = list(self.console_scripts.keys())[0]
        
        # Check OSI-specific configuration for other entry point types
        if self.osi_config:
            entry_points = self.osi_config.get('entry_points', {})
            module = entry_points.get('module')
            script = entry_points.get('script')
            command = entry_points.get('command')
        
        # Extract author information
        author = ""
        if self.authors:
            if isinstance(self.authors[0], dict):
                author = self.authors[0].get('name', '')
            else:
                author = str(self.authors[0])
        
        # Get platform restrictions from OSI config
        platform_config = self.osi_config.get('platform', {})
        
        # Get installation commands from OSI config
        install_config = self.osi_config.get('install', {})
        
        return ToolConfig(
            name=self.name,
            version=self.version,
            description=self.description,
            author=author,
            license=self.license,
            python_version=self.python_requires,
            dependencies=self.dependencies,
            dev_dependencies=self.optional_dependencies.get('dev', []),
            entry_point=entry_point,
            module=module,
            script=script,
            command=command,
            windows_only=platform_config.get('windows_only', False),
            linux_only=platform_config.get('linux_only', False),
            macos_only=platform_config.get('macos_only', False),
            homepage=self.homepage,
            repository=self.repository,
            documentation=self.documentation,
            keywords=self.keywords,
            pre_install_commands=install_config.get('pre_install', []),
            post_install_commands=install_config.get('post_install', []),
        )


class PyProjectParser:
    """
    Parser for pyproject.toml files.
    
    Extracts tool metadata and configuration from standard Python project files
    and converts them to OSI-compatible format.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_file(self, pyproject_path: Path) -> Optional[PyProjectConfig]:
        """
        Parse a pyproject.toml file.
        
        Args:
            pyproject_path: Path to the pyproject.toml file
            
        Returns:
            PyProjectConfig object or None if parsing fails
        """
        try:
            if not pyproject_path.exists():
                self.logger.error(f"pyproject.toml not found: {pyproject_path}")
                return None
            
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            return self.parse_data(data)
            
        except Exception as e:
            self.logger.error(f"Failed to parse pyproject.toml {pyproject_path}: {e}")
            return None
    
    def parse_data(self, data: Dict[str, Any]) -> Optional[PyProjectConfig]:
        """
        Parse pyproject.toml data dictionary.
        
        Args:
            data: Parsed TOML data
            
        Returns:
            PyProjectConfig object or None if parsing fails
        """
        try:
            # Extract project metadata
            project = data.get('project', {})
            
            if not project:
                self.logger.error("No [project] section found in pyproject.toml")
                return None
            
            name = project.get('name')
            if not name:
                self.logger.error("Project name is required in pyproject.toml")
                return None
            
            # Parse version
            version = project.get('version', '1.0.0')
            if isinstance(version, dict) and 'attr' in version:
                # Dynamic version - use default for now
                version = '1.0.0'
            
            # Parse authors
            authors = []
            if 'authors' in project:
                authors = project['authors']
            elif 'author' in project:
                # Handle legacy author field
                authors = [project['author']]
            
            # Parse dependencies
            dependencies = project.get('dependencies', [])
            optional_dependencies = project.get('optional-dependencies', {})
            
            # Parse entry points
            console_scripts = {}
            gui_scripts = {}
            
            if 'scripts' in project:
                console_scripts = project['scripts']
            
            if 'gui-scripts' in project:
                gui_scripts = project['gui-scripts']
            
            # Check for entry-points section
            if 'entry-points' in project:
                entry_points = project['entry-points']
                if 'console_scripts' in entry_points:
                    console_scripts.update(entry_points['console_scripts'])
                if 'gui_scripts' in entry_points:
                    gui_scripts.update(entry_points['gui_scripts'])
            
            # Parse URLs
            urls = project.get('urls', {})
            homepage = urls.get('Homepage', project.get('homepage', ''))
            repository = urls.get('Repository', urls.get('Source', ''))
            documentation = urls.get('Documentation', '')
            
            # Parse license
            license_info = project.get('license', {})
            if isinstance(license_info, dict):
                license_str = license_info.get('text', license_info.get('file', ''))
            else:
                license_str = str(license_info)
            
            # Extract OSI-specific configuration
            osi_config = data.get('tool', {}).get('osi', {})
            
            return PyProjectConfig(
                name=name,
                version=str(version),
                description=project.get('description', ''),
                authors=authors,
                license=license_str,
                readme=project.get('readme', ''),
                homepage=homepage,
                repository=repository,
                documentation=documentation,
                keywords=project.get('keywords', []),
                classifiers=project.get('classifiers', []),
                python_requires=project.get('requires-python', '>=3.11'),
                dependencies=dependencies,
                optional_dependencies=optional_dependencies,
                console_scripts=console_scripts,
                gui_scripts=gui_scripts,
                osi_config=osi_config,
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse pyproject.toml data: {e}")
            return None
    
    def parse_from_wheel(self, wheel_info: WheelInfo) -> Optional[PyProjectConfig]:
        """
        Create PyProjectConfig from wheel metadata.
        
        Args:
            wheel_info: WheelInfo object
            
        Returns:
            PyProjectConfig object or None if conversion fails
        """
        try:
            # Convert wheel metadata to pyproject format
            authors = []
            if wheel_info.author:
                authors = [wheel_info.author]
            
            # Convert entry points
            console_scripts = {}
            if wheel_info.entry_points:
                console_scripts = wheel_info.entry_points
            
            return PyProjectConfig(
                name=wheel_info.name,
                version=wheel_info.version,
                description=wheel_info.summary or "",
                authors=authors,
                license=wheel_info.license or "",
                homepage=wheel_info.homepage or "",
                python_requires=wheel_info.python_requires or ">=3.11",
                dependencies=wheel_info.dependencies,
                console_scripts=console_scripts,
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert wheel info to pyproject config: {e}")
            return None
    
    def validate_config(self, config: PyProjectConfig) -> bool:
        """
        Validate a PyProjectConfig object.
        
        Args:
            config: PyProjectConfig to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not config.name:
                self.logger.error("Tool name is required")
                return False
            
            if not config.version:
                self.logger.error("Tool version is required")
                return False
            
            # Check that at least one entry point is defined
            has_entry_point = (
                config.console_scripts or
                config.gui_scripts or
                (config.osi_config and config.osi_config.get('entry_points'))
            )
            
            if not has_entry_point:
                self.logger.warning(f"No entry points defined for {config.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Config validation failed: {e}")
            return False

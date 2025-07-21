"""
OSI - Organized Software Installer

A comprehensive Python environment management solution for distributing
PyWheel applications with automatic dependency isolation.
"""

__version__ = "1.0.0"
__author__ = "Ethan Li"
__description__ = "Python environment management for PyWheel applications"

from .config_manager import ConfigManager
from .dependency_resolver import DependencyResolver
from .environment_manager import EnvironmentManager
from .launcher import Launcher
from .pyproject_parser import PyProjectParser
from .wheel_manager import WheelManager

__all__ = [
    "EnvironmentManager",
    "DependencyResolver",
    "Launcher",
    "ConfigManager",
    "WheelManager",
    "PyProjectParser",
]

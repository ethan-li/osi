"""
OSI - Organized Software Installer

A comprehensive Python environment management solution for distributing 
PyWheel applications with automatic dependency isolation.
"""

__version__ = "1.0.0"
__author__ = "Zheng Li"
__description__ = "Python environment management for PyWheel applications"

from .environment_manager import EnvironmentManager
from .dependency_resolver import DependencyResolver
from .launcher import Launcher
from .config_manager import ConfigManager
from .wheel_manager import WheelManager
from .pyproject_parser import PyProjectParser

__all__ = [
    "EnvironmentManager",
    "DependencyResolver",
    "Launcher",
    "ConfigManager",
    "WheelManager",
    "PyProjectParser"
]

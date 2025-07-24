# OSI: Organized Software Installer

A modern Python tool management system that simplifies the installation, management, and execution of Python-based tools through wheel packages. OSI provides a unified interface for managing multiple tools with automatic dependency resolution and virtual environment isolation.

## Overview

OSI (Organized Software Installer) is designed for users who prefer simplified setup and need to run multiple Python tools distributed as wheels without dealing with dependency conflicts or complex virtual environment management.

## Key Features

- **Wheel-based Distribution**: Tools are distributed as standard Python wheels
- **Isolated Environments**: Each tool runs in its own virtual environment
- **One-Step Installation**: Single command installs tools with all dependencies
- **Kit-based Distribution**: Multiple tools can be bundled together in kits
- **Automatic Management**: Environments are created and maintained automatically
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **User-Friendly**: Simple interface for users who want streamlined installation
- **Standard Configuration**: Uses pyproject.toml for tool configuration
- **Multiple Distribution Methods**: Standalone executables, quick start, source installation

## Distribution Methods

OSI offers multiple ways to install and distribute tools:

1. **Standalone Executables**: Single-file executables with no Python dependency required
2. **Quick Start Script**: One-command installation directly from GitHub
3. **Source Installation**: Full development setup with all features and testing

## Requirements

- **Python**: 3.11 or higher (3.11, 3.12, 3.13 supported)
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for downloading dependencies

## Quick Start

### Installation

#### Option 1: Standalone Executable (Recommended for End Users)

Download the pre-built executable for your platform:
- **Windows**: Download `osi-windows-x86_64.zip` from releases
- **macOS**: Download `osi-darwin-arm64.zip` from releases
- **Linux**: Download `osi-linux-x86_64.zip` from releases

Extract and run directly - no Python installation required!

#### Option 2: From Source

1. Download or clone this repository
2. Verify your system meets requirements:
   - **Windows**: `scripts\osi.bat doctor`
   - **macOS/Linux**: `scripts/osi.sh doctor`

### Running Tools

```bash
# List available tools
osi list

# Run a specific tool
osi run tool_name

# Install a new tool
osi install tool_name

# Show tool information
osi info tool_name

# Get help
osi --help
```

## Architecture

OSI consists of several core components:

- **Wheel Manager**: Discovers and manages Python wheel files
- **Environment Manager**: Creates and manages isolated Python environments
- **Dependency Resolver**: Handles wheel-based dependency requirements
- **Launcher System**: Cross-platform execution scripts
- **Configuration Manager**: Extracts configuration from wheel metadata
- **Kit Manager**: Manages collections of related tools

## Tool Configuration

Each tool is distributed as a Python wheel with standard `pyproject.toml` configuration that specifies:

- Tool metadata (name, version, description)
- Python dependencies and versions
- Console script entry points
- Platform-specific requirements

## Example Usage

```bash
# List available tools
osi list

# List available kits
osi list-kits

# Install a kit containing multiple tools
osi install-kit /path/to/kit/directory

# Install a specific tool (automatically sets up environment and dependencies)
osi install text_processor

# Run a tool with arguments
osi run text_processor count myfile.txt

# Get help for a tool
osi run text_processor --help

# Show kit information
osi kit-info test_kit

# Check system status
osi doctor

# Clean up all environments
osi clean
```

## Directory Structure

```
osi/
├── osi/                    # Core package
├── wheels/                 # Individual wheel files
├── kits/                   # Kit-based wheel collections
├── environments/           # Virtual environments (auto-created)
├── scripts/               # Platform launchers
└── logs/                  # Log files (auto-created)
```

## For Developers

### Creating Wheel-based Tools

1. Create a Python project with `pyproject.toml`
2. Build the wheel: `python -m build`
3. Place the wheel in a kit directory
4. Install the kit: `osi install-kit /path/to/kit`

### Configuration Format

Use standard `pyproject.toml` format with console script entry points.

## Troubleshooting

- Check `logs/osi.log` for detailed error information
- Use `osi doctor` to diagnose common issues
- Run `osi clean` to reset environments if needed

## Project Structure

```
osi/
├── osi/                    # Core Python package
│   ├── __init__.py        # Package initialization
│   ├── launcher.py        # Main launcher and CLI
│   ├── config_manager.py  # Configuration management
│   ├── wheel_manager.py   # Wheel discovery and management
│   └── ...               # Other core modules
├── scripts/               # Cross-platform launcher scripts
├── tests/                 # Comprehensive test suite
├── docs/                  # Documentation
├── kits/                  # Kit-based tool collections
├── build_scripts/         # Distribution builders
├── quick_start.py         # Quick installation script
├── install_osi.py         # Self-contained installer
└── README.md              # This file
```

## Links

- **GitHub**: [https://github.com/ethan-li/osi](https://github.com/ethan-li/osi)
- **Documentation**: [docs/](docs/)
- **Issues**: [https://github.com/ethan-li/osi/issues](https://github.com/ethan-li/osi/issues)

## Author

- **Ethan Li** - *Initial work and maintenance*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

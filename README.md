# OSI - Organized Software Installer

A comprehensive Python environment management solution for distributing Python wheel applications with automatic dependency isolation and one-step installation.

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

## Requirements

- **Python**: 3.11 or higher (3.11, 3.12, 3.13 supported)
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for downloading dependencies

## Quick Start

### Installation

1. Download or clone this repository
2. Run the installer for your platform:
   - **Windows**: `scripts\osi.bat install`
   - **macOS/Linux**: `scripts/osi.sh install`

### Running Tools

```bash
# List available tools
osi list

# Run a specific tool
osi run tool_name

# Install a new tool
osi install tool_name

# Get help
osi help
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
osi install text-processor

# Run a tool with arguments
osi run text-processor count myfile.txt

# Get help for a tool
osi run text-processor --help

# Show kit information
osi kit-info my_kit

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

## License

[Add your license information here]

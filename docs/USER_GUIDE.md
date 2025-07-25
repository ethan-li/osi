# OSI User Guide

This guide explains how to use OSI (Organized Software Installer) to manage and run Python tools.

## Overview

OSI automatically manages Python environments for different tools, ensuring that each tool runs in isolation without dependency conflicts. You don't need to worry about virtual environments, pip installations, or Python path issues.

## Basic Commands

### Listing Available Tools

```bash
# Show all available tools
osi list
```

This displays all configured tools with their installation status:
```
Available tools:
--------------------------------------------------
✓ text_processor     - A simple text processing tool for OSI demonstration
```

- ✓ = Tool is installed and ready to use
- ✗ = Tool is not installed

### Installing Tools

```bash
# Install a specific tool
osi install text_processor
```

This will:
1. Create a dedicated Python environment for the tool
2. Install all required dependencies
3. Verify the installation

### Running Tools

```bash
# Run a tool with arguments
osi run text_processor count tests/data/test_text.txt

# Get help for a tool
osi run text_processor --help

# Run without arguments (if the tool supports it)
osi run text_processor
```

OSI automatically:
- Checks if the tool is installed
- Verifies all dependencies are satisfied
- Updates dependencies if needed
- Runs the tool in its isolated environment

### Getting Tool Information

```bash
# Show detailed information about a tool
osi info text_processor
```

This displays:
- Tool metadata (version, description, author)
- Installation status
- Dependency information
- Entry point details

### Uninstalling Tools

```bash
# Remove a tool and its environment
osi uninstall text_processor
```

This removes the tool's virtual environment and all its dependencies.

## Example Workflows

### Text Processing Workflow

1. **Install the text processor**
   ```bash
   osi install text_processor
   ```

2. **Process a text file**
   ```bash
   osi run text_processor count tests/data/test_text.txt
   ```

3. **View the results**
   The tool will display word count and other text statistics.

### Advanced Text Processing

1. **Check tool information**
   ```bash
   osi info text_processor
   ```

2. **Process multiple files**
   ```bash
   osi run text_processor count tests/data/test_text.txt
   osi run text_processor count tests/data/sample_data.csv
   ```

3. **Get help for available commands**
   ```bash
   osi run text_processor --help
   ```

### Kit Management Workflow

1. **List available kits**
   ```bash
   osi list-kits
   ```

2. **Get kit information**
   ```bash
   osi kit-info test_kit
   ```

3. **Install a kit from a directory**
   ```bash
   osi install-kit /path/to/kit/directory
   ```

4. **Verify kit installation**
   ```bash
   osi list
   ```

## Advanced Usage

### Verbose Output

```bash
# Enable detailed logging
osi --verbose install data_analyzer
osi --verbose run web_scraper https://example.com
```

### System Diagnostics

```bash
# Check system health
osi doctor
```

This command:
- Verifies Python installation
- Checks platform compatibility
- Validates tool configurations
- Reports any issues

### Cleaning Up

```bash
# Remove all environments and start fresh
osi clean
```

Use this if you encounter persistent issues or want to free up disk space.

## Understanding Tool Configurations

Each tool is defined by a `tool.toml` file that specifies:

- **Metadata**: Name, version, description, author
- **Dependencies**: Required Python packages and versions
- **Entry Points**: How to run the tool (script, module, or command)
- **Platform Requirements**: OS-specific constraints

Example `tool.toml`:
```toml
[tool]
name = "my_tool"
version = "1.0.0"
description = "My awesome tool"

[dependencies]
python = ">=3.7"
packages = ["requests>=2.25.0", "click>=7.0"]

[entry_points]
script = "main.py"
```

## Troubleshooting

### Tool Won't Install

1. **Check your internet connection**
   ```bash
   osi doctor
   ```

2. **Try installing with verbose output**
   ```bash
   osi --verbose install tool_name
   ```

3. **Check the logs**
   ```bash
   tail -f logs/osi.log
   ```

### Tool Won't Run

1. **Verify the tool is installed**
   ```bash
   osi list
   osi info tool_name
   ```

2. **Try reinstalling**
   ```bash
   osi uninstall tool_name
   osi install tool_name
   ```

3. **Check for dependency conflicts**
   ```bash
   osi --verbose run tool_name
   ```

### Environment Issues

1. **Clean and reinstall**
   ```bash
   osi clean
   osi install tool_name
   ```

2. **Check Python version**
   ```bash
   python --version
   osi doctor
   ```

### Common Error Messages

**"Tool 'xyz' not found"**
- The tool configuration doesn't exist
- Check `osi list` for available tools

**"Environment for 'xyz' does not exist"**
- The tool isn't installed
- Run `osi install xyz`

**"Failed to install dependencies"**
- Network connectivity issues
- Incompatible Python version
- Check logs for specific error details

**"Python 3.7 or later is required"**
- Your Python version is too old
- Install a newer Python version

## Tips for Users

1. **Always run `osi doctor` first** when troubleshooting
2. **Use `--verbose` flag** to see detailed output
3. **Check logs** in the `logs/` directory for error details
4. **Clean environments** if you encounter persistent issues
5. **Verify tool configurations** with `osi info tool_name`

## Getting Help

- **Command help**: `osi --help` or `osi command --help`
- **Tool help**: `osi run tool_name --help`
- **System diagnostics**: `osi doctor`
- **Log files**: Check `logs/osi.log` for detailed error information

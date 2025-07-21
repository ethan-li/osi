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
✓ data_analyzer      - A data analysis tool for CSV files
✗ web_scraper        - A simple web scraping tool
✓ file_organizer     - Organize files in directories by type
```

- ✓ = Tool is installed and ready to use
- ✗ = Tool is not installed

### Installing Tools

```bash
# Install a specific tool
osi install data_analyzer
```

This will:
1. Create a dedicated Python environment for the tool
2. Install all required dependencies
3. Verify the installation

### Running Tools

```bash
# Run a tool with arguments
osi run data_analyzer mydata.csv --output ./results

# Get help for a tool
osi run data_analyzer --help

# Run without arguments (if the tool supports it)
osi run file_organizer
```

OSI automatically:
- Checks if the tool is installed
- Verifies all dependencies are satisfied
- Updates dependencies if needed
- Runs the tool in its isolated environment

### Getting Tool Information

```bash
# Show detailed information about a tool
osi info data_analyzer
```

This displays:
- Tool metadata (version, description, author)
- Installation status
- Dependency information
- Entry point details

### Uninstalling Tools

```bash
# Remove a tool and its environment
osi uninstall web_scraper
```

This removes the tool's virtual environment and all its dependencies.

## Example Workflows

### Data Analysis Workflow

1. **Install the data analyzer**
   ```bash
   osi install data_analyzer
   ```

2. **Analyze a CSV file**
   ```bash
   osi run data_analyzer sales_data.csv --output ./analysis_results
   ```

3. **View the results**
   The tool will generate statistics and plots in the output directory.

### Web Scraping Workflow

1. **Install the web scraper**
   ```bash
   osi install web_scraper
   ```

2. **Scrape links from a website**
   ```bash
   osi run web_scraper https://example.com --mode links --output links.json
   ```

3. **Extract text content**
   ```bash
   osi run web_scraper https://example.com --mode text --output content.txt
   ```

### File Organization Workflow

1. **Install the file organizer**
   ```bash
   osi install file_organizer
   ```

2. **Analyze a directory**
   ```bash
   osi run file_organizer analyze ~/Downloads
   ```

3. **Organize files by type**
   ```bash
   osi run file_organizer organize-by-type ~/Downloads --create-folders
   ```

4. **Clean up temporary files**
   ```bash
   osi run file_organizer clean ~/Downloads --pattern "*.tmp"
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

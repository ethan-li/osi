# OSI Developer Guide

This guide explains how to create and package wheel-based tools for the OSI (Organized Software Installer) system.

## Overview

OSI tools are Python applications distributed as standard Python wheels with pyproject.toml configuration. Each tool runs in its own isolated environment to prevent dependency conflicts.

## Tool Structure

A typical OSI wheel-based tool has this structure:

```
my_tool/
├── pyproject.toml      # Standard Python project configuration (required)
├── my_tool/           # Package directory
│   ├── __init__.py
│   └── main.py
└── README.md          # Documentation
```

After building, the tool is distributed as a `.whl` file.

## Configuration File (pyproject.toml)

The `pyproject.toml` file defines your tool's metadata and requirements using standard Python packaging format:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "my-awesome-tool"
version = "1.0.0"
description = "A tool that does awesome things"
authors = [
    {name = "Zheng Li", email = "aeon.zheng.li@gmail.com"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
keywords = ["utility", "automation", "awesome"]
dependencies = [
    "requests>=2.25.0",
    "click>=7.0",
    "pandas>=1.3.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "black>=21.0"
]

[project.urls]
Homepage = "https://github.com/zheng-li/my-awesome-tool"
Repository = "https://github.com/zheng-li/my-awesome-tool"
Documentation = "https://my-awesome-tool.readthedocs.io"
"Bug Tracker" = "https://github.com/zheng-li/my-awesome-tool/issues"

[project.scripts]
my-tool = "my_tool.main:cli"

[tool.setuptools.packages.find]
where = ["."]
include = ["my_tool*"]

# OSI-specific configuration (optional)
[tool.osi]
[tool.osi.platform]
windows_only = false
linux_only = false
macos_only = false

[tool.osi.install]
pre_install = []
post_install = ["echo 'Installation complete!'"]
```

### Configuration Sections

#### [tool]
- **name**: Tool identifier (used for installation/running)
- **version**: Tool version
- **description**: Brief description shown in listings
- **author**: Tool author
- **license**: License type
- **homepage/repository**: URLs for documentation/source
- **keywords**: Search keywords

#### [dependencies]
- **python**: Minimum Python version requirement
- **packages**: List of required Python packages with version specs
- **dev_packages**: Development dependencies (not installed by default)

#### [entry_points]
Choose ONE method for running your tool:

1. **console_script**: For tools installed as console commands
2. **module**: For tools run with `python -m module_name`
3. **script**: For direct script execution
4. **command**: For custom command arrays

#### [platform]
Specify platform restrictions if needed.

#### [install]
Commands to run before/after installation.

## Entry Point Methods

### Method 1: Console Script (Recommended for Complex Tools)

Best for tools with multiple commands or complex CLI interfaces.

1. **Create a package structure**:
   ```
   tools/my_tool/
   ├── tool.toml
   ├── setup.py
   └── my_tool/
       ├── __init__.py
       └── main.py
   ```

2. **Configure tool.toml**:
   ```toml
   [entry_points]
   console_script = "my-tool"
   ```

3. **Create setup.py**:
   ```python
   from setuptools import setup, find_packages
   
   setup(
       name="my-tool",
       version="1.0.0",
       packages=find_packages(),
       entry_points={
           "console_scripts": [
               "my-tool=my_tool.main:cli",
           ],
       },
   )
   ```

4. **Create main.py with CLI**:
   ```python
   import click
   
   @click.command()
   @click.argument('input_file')
   @click.option('--output', '-o', help='Output file')
   def cli(input_file, output):
       """My awesome tool CLI."""
       # Your tool logic here
       pass
   
   if __name__ == '__main__':
       cli()
   ```

### Method 2: Python Module

Good for tools that work well with `python -m module_name`.

1. **Configure tool.toml**:
   ```toml
   [entry_points]
   module = "my_tool.main"
   ```

2. **Create package with __main__.py**:
   ```
   tools/my_tool/
   ├── tool.toml
   └── my_tool/
       ├── __init__.py
       ├── __main__.py
       └── main.py
   ```

3. **Create __main__.py**:
   ```python
   from .main import main
   
   if __name__ == '__main__':
       main()
   ```

### Method 3: Direct Script

Simplest method for basic tools.

1. **Configure tool.toml**:
   ```toml
   [entry_points]
   script = "my_script.py"
   ```

2. **Create the script**:
   ```python
   #!/usr/bin/env python3
   import argparse
   
   def main():
       parser = argparse.ArgumentParser(description='My tool')
       parser.add_argument('input', help='Input file')
       args = parser.parse_args()
       
       # Your tool logic here
       print(f"Processing {args.input}")
   
   if __name__ == '__main__':
       main()
   ```

### Method 4: Custom Command

For tools with special execution requirements.

```toml
[entry_points]
command = ["python", "run.py", "--special-flag"]
```

## Dependency Management

### Using tool.toml packages

```toml
[dependencies]
packages = [
    "requests>=2.25.0",
    "pandas>=1.3.0,<2.0.0",
    "click~=7.0"
]
```

### Using requirements.txt

For complex dependency specifications:

```
# requirements.txt
requests>=2.25.0
pandas>=1.3.0,<2.0.0
click~=7.0
# Optional dependencies
matplotlib>=3.3.0; extra == "plotting"
```

### Version Specifiers

- `>=1.0.0`: Minimum version
- `<2.0.0`: Maximum version (exclusive)
- `~=1.4.0`: Compatible release (>=1.4.0, <1.5.0)
- `==1.4.2`: Exact version
- `!=1.4.1`: Exclude specific version

## Best Practices

### Tool Design

1. **Single Responsibility**: Each tool should have a clear, focused purpose
2. **CLI Interface**: Provide helpful command-line interfaces
3. **Error Handling**: Handle errors gracefully with clear messages
4. **Documentation**: Include help text and examples
5. **Cross-Platform**: Test on Windows, macOS, and Linux

### Dependencies

1. **Pin Major Versions**: Use `package>=1.0,<2.0` to avoid breaking changes
2. **Minimal Dependencies**: Only include what you actually need
3. **Popular Packages**: Prefer well-maintained, popular packages
4. **Version Compatibility**: Test with different dependency versions

### Configuration

1. **Descriptive Names**: Use clear, descriptive tool names
2. **Semantic Versioning**: Follow semver for version numbers
3. **Complete Metadata**: Fill in all relevant metadata fields
4. **Platform Testing**: Test platform restrictions if used

## Testing Your Tool

### Local Testing

1. **Create the tool structure**
2. **Test configuration loading**:
   ```bash
   osi info my_tool
   ```

3. **Test installation**:
   ```bash
   osi install my_tool
   ```

4. **Test execution**:
   ```bash
   osi run my_tool --help
   osi run my_tool test_input
   ```

### Validation

```bash
# Validate configuration
osi info my_tool

# Check dependencies
osi --verbose install my_tool

# Test in clean environment
osi clean
osi install my_tool
osi run my_tool
```

## Example: Creating a Simple Tool

Let's create a "hello world" tool:

1. **Create directory structure**:
   ```bash
   mkdir -p tools/hello_world
   cd tools/hello_world
   ```

2. **Create tool.toml**:
   ```toml
   [tool]
   name = "hello_world"
   version = "1.0.0"
   description = "A simple hello world tool"
   author = "Zheng Li"
   
   [dependencies]
   python = ">=3.11"
   packages = ["click>=7.0"]
   
   [entry_points]
   script = "hello.py"
   ```

3. **Create hello.py**:
   ```python
   #!/usr/bin/env python3
   import click
   
   @click.command()
   @click.option('--name', default='World', help='Name to greet')
   @click.option('--count', default=1, help='Number of greetings')
   def hello(name, count):
       """Simple program that greets NAME for a total of COUNT times."""
       for _ in range(count):
           click.echo(f'Hello {name}!')
   
   if __name__ == '__main__':
       hello()
   ```

4. **Test the tool**:
   ```bash
   osi install hello_world
   osi run hello_world --name Alice --count 3
   ```

## Packaging for Distribution

### Creating Tool Packages

1. **Zip the tool directory**:
   ```bash
   cd tools
   zip -r my_tool.zip my_tool/
   ```

2. **Share the package**:
   - Users extract to their `tools/` directory
   - Run `osi install my_tool`

### Git Repository

1. **Create a repository** with your tool
2. **Users clone** into their `tools/` directory
3. **Install** with `osi install tool_name`

## Troubleshooting

### Common Issues

**"Tool configuration not found"**
- Check `tool.toml` exists and is valid TOML
- Verify tool name matches directory name

**"No valid entry point found"**
- Ensure exactly one entry point method is specified
- Check that referenced files exist

**"Failed to install dependencies"**
- Verify package names and versions are correct
- Check for typos in requirements

**"Module not found" when running**
- Check Python path and package structure
- Verify entry point references correct module

### Debugging

1. **Use verbose mode**: `osi --verbose install my_tool`
2. **Check logs**: `tail -f logs/osi.log`
3. **Validate config**: `osi info my_tool`
4. **Test manually**: Activate environment and test directly

## Advanced Topics

### Custom Installation Commands

```toml
[install]
pre_install = [
    "pip install --upgrade pip",
    "echo 'Preparing installation'"
]
post_install = [
    "python -c 'import my_tool; my_tool.setup()'",
    "echo 'Setup complete'"
]
```

### Platform-Specific Tools

```toml
[platform]
windows_only = true  # Only install on Windows

[dependencies]
packages = [
    "pywin32>=227; sys_platform=='win32'",
    "unix-specific-package>=1.0; sys_platform!='win32'"
]
```

### Development Dependencies

```toml
[dependencies]
dev_packages = [
    "pytest>=6.0",
    "black>=21.0",
    "mypy>=0.812"
]
```

These are not installed by default but can be useful for tool development.

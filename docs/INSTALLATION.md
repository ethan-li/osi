# OSI Installation Guide

This guide will help you install and set up OSI (Organized Software Installer) on your system.

## System Requirements

- **Python**: 3.11 or later (3.11, 3.12, 3.13 supported)
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **Disk Space**: At least 100MB for OSI itself, plus space for tool environments
- **Internet Connection**: Required for downloading dependencies

## Installation

### Using Git (Recommended)

```bash
git clone https://github.com/ethan-li/osi.git
cd osi
```

### From Source

1. **Download OSI**
   ```bash
   # Clone or download the OSI repository
   git clone https://github.com/ethan-li/osi.git
   cd osi
   ```

2. **Run the installer for your platform**
   
   **Windows:**
   ```cmd
   scripts\osi.bat doctor
   ```
   
   **macOS/Linux:**
   ```bash
   scripts/osi.sh doctor
   ```

3. **Verify installation**
   The `doctor` command will check your system and report any issues.

### Option 2: Python Package Installation

If you're familiar with Python, you can install OSI as a package:

```bash
# Install OSI and its dependencies
pip install -e .

# Verify installation
osi doctor
```

## Platform-Specific Instructions

### Windows

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Download OSI**
   - Download the ZIP file and extract it
   - Or use Git: `git clone https://github.com/ethan-li/osi.git`

3. **Run OSI**
   ```cmd
   cd osi
   scripts\osi.bat list
   ```

### macOS

1. **Install Python** (if not already installed)
   ```bash
   # Using Homebrew (recommended)
   brew install python3
   
   # Or download from python.org
   ```

2. **Download OSI**
   ```bash
   git clone https://github.com/ethan-li/osi.git
   cd osi
   ```

3. **Run OSI**
   ```bash
   scripts/osi.sh list
   ```

### Linux (Ubuntu/Debian)

1. **Install Python**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Download OSI**
   ```bash
   git clone https://github.com/ethan-li/osi.git
   cd osi
   ```

3. **Run OSI**
   ```bash
   scripts/osi.sh list
   ```

### Linux (CentOS/RHEL/Fedora)

1. **Install Python**
   ```bash
   # CentOS/RHEL
   sudo yum install python3 python3-pip
   
   # Fedora
   sudo dnf install python3 python3-pip
   ```

2. **Download and run OSI** (same as Ubuntu)

## Verification

After installation, verify that OSI is working correctly:

```bash
# Check system status
osi doctor

# List available tools
osi list

# Get help
osi --help
```

## Setting Up PATH (Optional)

To use OSI from anywhere on your system, you can add it to your PATH:

### Windows
1. Add the OSI `scripts` directory to your PATH environment variable
2. Or create a batch file in a directory that's already in PATH

### macOS/Linux
Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="/path/to/osi/scripts:$PATH"
alias osi="/path/to/osi/scripts/osi.sh"
```

## Troubleshooting Installation

### Common Issues

**"Python not found"**
- Make sure Python 3.11+ is installed and in your PATH
- Try `python3` instead of `python`
- On Windows, try the `py` launcher

**"Permission denied" (Linux/macOS)**
- Make sure the script is executable: `chmod +x scripts/osi.sh`
- Don't run with `sudo` unless necessary

**"Module not found" errors**
- Make sure you're in the OSI directory
- Try installing dependencies: `pip install -r requirements.txt`

**Virtual environment issues**
- OSI creates its own virtual environments
- If you have issues, try: `osi clean` to reset everything

### Getting Help

1. **Check the logs**
   ```bash
   # View recent log entries
   tail -f logs/osi.log
   ```

2. **Run diagnostics**
   ```bash
   osi doctor
   ```

3. **Enable verbose logging**
   ```bash
   osi --verbose list
   ```

4. **Reset everything**
   ```bash
   osi clean
   ```

## Next Steps

Once OSI is installed:

1. **Explore available tools**: `osi list`
2. **Install a tool**: `osi install data_analyzer`
3. **Run a tool**: `osi run data_analyzer --help`
4. **Read the User Guide**: See `docs/USER_GUIDE.md`

## Uninstallation

To remove OSI:

1. **Clean up environments**
   ```bash
   osi clean
   ```

2. **Remove OSI directory**
   ```bash
   rm -rf /path/to/osi
   ```

3. **Remove from PATH** (if you added it)
   - Edit your shell configuration file to remove OSI references

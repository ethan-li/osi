# OSI Deployment Guide for Users

## 🎯 Overview

OSI (Organized Software Installer) now provides multiple "download and run" options that require **no manual dependency installation**. Users can choose the method that best fits their environment.

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Setup Script
**Best for: Most users**

1. **Download**: `quick_start.py` (single file, ~15KB)
2. **Run**: `python quick_start.py`
3. **Done**: Follow the prompts, OSI will be ready in 2-3 minutes

```bash
# Download and run (example)
curl -O https://your-server.com/osi/quick_start.py
python quick_start.py
```

**What it does:**
- ✅ Automatically creates isolated environment
- ✅ Downloads and installs all dependencies
- ✅ Sets up OSI with launcher scripts
- ✅ Tests the installation
- ✅ Provides usage instructions

**Requirements:** Only Python 3.11+ (may need installation)

## 📦 Alternative Distribution Methods

### Option 2: Self-contained Installer
**Best for: Automated deployments**

1. **Download**: `install_osi.py` (~50KB)
2. **Run**: `python install_osi.py`
3. **Use**: OSI installed to `~/.osi/`

### Option 3: Portable Executable (Windows)
**Best for: No Python environments**

1. **Download**: `osi.exe` (~50-100MB)
2. **Run**: Direct execution, no installation needed
3. **Use**: `osi.exe list`, `osi.exe install tool-name`

### Option 4: Portable Python Bundle
**Best for: Offline/air-gapped environments**

1. **Download**: `osi-portable-windows.zip` (~100-200MB)
2. **Extract**: Anywhere on the system
3. **Run**: `osi.bat list` or `./osi.sh list`

### Option 5: Docker Container
**Best for: Enterprise environments with Docker**

```bash
# Pull and run
docker run --rm -v "$(pwd):/workspace" osi:latest list

# Or use wrapper scripts
./docker_wrappers/osi.sh list
```

## 🎯 Deployment Scenarios

### Scenario 1: Individual User Workstation
**Recommended**: Quick Start Script (`quick_start.py`)

```bash
# One command setup
python quick_start.py

# Then use OSI
~/.osi/bin/osi list
~/.osi/bin/osi install text-processor
```

### Scenario 2: Multiple Workstations (Network Deployment)
**Recommended**: Self-contained Installer + Network Share

```bash
# Place installer on network share
\\server\tools\osi\install_osi.py

# Each workstation runs
python \\server\tools\osi\install_osi.py
```

### Scenario 3: Air-gapped Environment
**Recommended**: Portable Python Bundle

1. Download `osi-portable-windows.zip` on internet-connected machine
2. Transfer to air-gapped environment
3. Extract and run `osi.bat`

### Scenario 4: Enterprise with Docker
**Recommended**: Docker Container

```bash
# Deploy container
docker pull your-registry/osi:latest

# Use with wrapper scripts
./osi.sh list
./osi.sh install tool-name
```

## 📋 Step-by-Step for Users

### Method 1: Quick Start (Easiest)

1. **Download** the quick start script:
   ```bash
   # Windows (PowerShell)
   Invoke-WebRequest -Uri "https://your-server.com/osi/quick_start.py" -OutFile "quick_start.py"
   
   # Linux/macOS
   curl -O https://your-server.com/osi/quick_start.py
   
   # Or just save the file from your browser
   ```

2. **Run** the script:
   ```bash
   python quick_start.py
   ```

3. **Follow prompts** - the script will:
   - Check your system
   - Download OSI automatically
   - Set up everything needed
   - Test the installation
   - Show you how to use it

4. **Start using OSI**:
   ```bash
   ~/.osi/bin/osi list              # See available tools
   ~/.osi/bin/osi install my-tool   # Install a tool
   ~/.osi/bin/osi run my-tool       # Run a tool
   ```

### Method 2: Portable Executable (Windows Only)

1. **Download** `osi.exe` from your distribution source
2. **Place** it anywhere (e.g., `C:\Tools\osi.exe`)
3. **Use directly**:
   ```cmd
   C:\Tools\osi.exe list
   C:\Tools\osi.exe install text-processor
   C:\Tools\osi.exe run text-processor count myfile.txt
   ```

## 🔧 Adding Tools

### Installing Tool Kits

1. **Get kit directory** (contains .whl files)
2. **Install kit**:
   ```bash
   osi install-kit /path/to/kit/directory
   ```

### Installing Individual Tools

1. **Place .whl file** in `~/.osi/wheels/` directory
2. **Install tool**:
   ```bash
   osi install tool-name
   ```

## 🆘 Troubleshooting

### Common Issues

**"Python not found"**
- Install Python 3.11+ from python.org
- Or use the portable executable option

**"Permission denied"**
- Run as administrator (Windows) or with sudo (Linux/macOS)
- Or install to user directory (default behavior)

**"Internet connection required"**
- Use portable distribution for offline environments
- Or download dependencies separately

**"Tool not found"**
- Check that .whl files are in the correct directory
- Run `osi list` to see available tools
- Run `osi doctor` to check system status

### Getting Help

```bash
osi --help           # General help
osi doctor           # System diagnostics
osi info tool-name   # Tool information
```

## 📊 Comparison of Methods

| Method | Size | Requirements | Setup Time | Best For |
|--------|------|--------------|------------|----------|
| Quick Start | 15KB | Python 3.11+ | 2-3 min | Most users |
| Installer | 50KB | Python 3.11+ | 1-2 min | Automation |
| Executable | 50-100MB | None | Instant | No Python |
| Portable | 100-200MB | None | Instant | Offline |
| Docker | Variable | Docker | 1-2 min | Enterprise |

## 🎉 Success Criteria

After deployment, users should be able to:

1. ✅ Run `osi list` to see available tools
2. ✅ Run `osi doctor` to verify system health
3. ✅ Install tools with `osi install tool-name`
4. ✅ Run tools with `osi run tool-name`
5. ✅ Get help with `osi --help`

## 📞 Support

If users encounter issues:

1. **First**: Run `osi doctor` for diagnostics
2. **Check**: This deployment guide
3. **Logs**: Check `~/.osi/logs/` for detailed error information
4. **Contact**: Your IT support team with the log files

---

**Remember**: The goal is "download and run" - users should never need to manually install dependencies or configure Python environments!

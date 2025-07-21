#!/usr/bin/env python3
"""
Build script to create Docker-based OSI distribution

This script builds a Docker container with OSI and all dependencies,
allowing users to run OSI without any local installation.
"""

import subprocess
import sys
from pathlib import Path


def build_docker_image():
    """Build the OSI Docker image."""
    print("Building OSI Docker image...")

    try:
        # Build the image
        result = subprocess.run(
            ["docker", "build", "-t", "osi:latest", "-t", "osi:wheel-only", "."],
            check=True,
            capture_output=True,
            text=True,
        )

        print("✅ Docker image built successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker first.")
        return False


def test_docker_image():
    """Test the Docker image."""
    print("Testing Docker image...")

    tests = [
        (["docker", "run", "--rm", "osi:latest", "--help"], "Help command"),
        (["docker", "run", "--rm", "osi:latest", "list"], "List command"),
        (["docker", "run", "--rm", "osi:latest", "doctor"], "Doctor command"),
    ]

    for cmd, description in tests:
        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, timeout=30
            )
            print(f"✅ {description} works")
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            print(f"❌ {description} timed out")
            return False

    return True


def create_docker_wrapper_scripts():
    """Create wrapper scripts for easy Docker usage."""
    print("Creating Docker wrapper scripts...")

    # Windows batch file
    windows_wrapper = """@echo off
REM OSI Docker Wrapper for Windows
REM This script runs OSI in a Docker container

set CURRENT_DIR=%cd%

docker run --rm -it ^
    -v "%CURRENT_DIR%":/workspace ^
    -v osi-environments:/app/environments ^
    -v osi-logs:/app/logs ^
    osi:latest %*
"""

    with open("docker_wrappers/osi.bat", "w") as f:
        f.write(windows_wrapper)

    # PowerShell script
    powershell_wrapper = """# OSI Docker Wrapper for PowerShell
# This script runs OSI in a Docker container

$CurrentDir = Get-Location

docker run --rm -it `
    -v "${CurrentDir}:/workspace" `
    -v "osi-environments:/app/environments" `
    -v "osi-logs:/app/logs" `
    osi:latest @args
"""

    with open("docker_wrappers/osi.ps1", "w") as f:
        f.write(powershell_wrapper)

    # Unix shell script
    unix_wrapper = """#!/bin/bash
# OSI Docker Wrapper for Linux/macOS
# This script runs OSI in a Docker container

CURRENT_DIR="$(pwd)"

docker run --rm -it \\
    -v "$CURRENT_DIR:/workspace" \\
    -v "osi-environments:/app/environments" \\
    -v "osi-logs:/app/logs" \\
    osi:latest "$@"
"""

    Path("docker_wrappers").mkdir(exist_ok=True)

    unix_script = Path("docker_wrappers/osi.sh")
    with open(unix_script, "w") as f:
        f.write(unix_wrapper)
    unix_script.chmod(0o755)

    print("Created wrapper scripts in docker_wrappers/")


def create_docker_compose():
    """Create docker-compose.yml for easier management."""
    compose_content = """version: '3.8'

services:
  osi:
    image: osi:latest
    container_name: osi-container
    volumes:
      - ./:/workspace
      - osi-environments:/app/environments
      - osi-logs:/app/logs
    working_dir: /workspace
    stdin_open: true
    tty: true
    command: ["--help"]

volumes:
  osi-environments:
    driver: local
  osi-logs:
    driver: local
"""

    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)

    print("Created docker-compose.yml")


def create_docker_readme():
    """Create README for Docker distribution."""
    readme_content = """# OSI Docker Distribution

This Docker-based distribution allows you to run OSI without installing Python or any dependencies locally.

## Prerequisites

- Docker installed on your system
- No Python installation required

## Quick Start

### Option 1: Direct Docker Commands

```bash
# Run OSI commands directly
docker run --rm -v "$(pwd):/workspace" osi:latest list
docker run --rm -v "$(pwd):/workspace" osi:latest install text-processor
docker run --rm -v "$(pwd):/workspace" osi:latest run text-processor --help
```

### Option 2: Using Wrapper Scripts

#### Windows
```cmd
# Use batch file
osi.bat list
osi.bat install text-processor

# Or PowerShell
.\\osi.ps1 list
.\\osi.ps1 install text-processor
```

#### Linux/macOS
```bash
# Make script executable (first time only)
chmod +x docker_wrappers/osi.sh

# Use wrapper script
./docker_wrappers/osi.sh list
./docker_wrappers/osi.sh install text-processor
```

### Option 3: Using Docker Compose

```bash
# Run commands with docker-compose
docker-compose run --rm osi list
docker-compose run --rm osi install text-processor
```

## Volume Mounts

The Docker container uses these volume mounts:

- `$(pwd):/workspace` - Your current directory (for accessing files)
- `osi-environments:/app/environments` - Persistent tool environments
- `osi-logs:/app/logs` - Persistent logs

## Building the Image

If you need to rebuild the image:

```bash
docker build -t osi:latest .
```

## Advantages

- ✅ No local Python installation required
- ✅ All dependencies included in container
- ✅ Consistent environment across different machines
- ✅ Easy to update (just pull new image)
- ✅ Isolated from host system

## File Access

The container can access files in your current directory. Place your wheel files, kits, and data files in the directory where you run the OSI commands.

## Troubleshooting

### Permission Issues (Linux/macOS)
If you encounter permission issues, you may need to run with user mapping:

```bash
docker run --rm -it \\
    -v "$(pwd):/workspace" \\
    -u "$(id -u):$(id -g)" \\
    osi:latest list
```

### Windows Path Issues
On Windows, if you have issues with path mounting, try using PowerShell or ensure Docker Desktop is properly configured for drive sharing.

### Container Cleanup
To clean up Docker resources:

```bash
# Remove OSI image
docker rmi osi:latest

# Remove volumes (this will delete environments and logs)
docker volume rm osi-environments osi-logs
```
"""

    with open("DOCKER_README.md", "w") as f:
        f.write(readme_content)


def main():
    """Main build process."""
    print("OSI Docker Distribution Builder")
    print("=" * 50)

    try:
        # Step 1: Build Docker image
        if not build_docker_image():
            return 1

        # Step 2: Test Docker image
        if not test_docker_image():
            print("❌ Docker image failed testing")
            return 1

        # Step 3: Create wrapper scripts
        create_docker_wrapper_scripts()

        # Step 4: Create docker-compose
        create_docker_compose()

        # Step 5: Create documentation
        create_docker_readme()

        print("\n🎉 Success! Docker-based OSI distribution created.")
        print("\n📋 Usage options:")
        print(
            '1. Direct Docker: docker run --rm -v "$(pwd):/workspace" osi:latest list'
        )
        print("2. Wrapper scripts: ./docker_wrappers/osi.sh list")
        print("3. Docker Compose: docker-compose run --rm osi list")
        print("\n📁 Files created:")
        print("- Dockerfile (Docker image definition)")
        print("- docker-compose.yml (Docker Compose configuration)")
        print("- docker_wrappers/ (Convenience scripts)")
        print("- DOCKER_README.md (Usage documentation)")

        return 0

    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

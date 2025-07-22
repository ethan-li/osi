#!/usr/bin/env python3
"""
Self-contained OSI installer

This script automatically sets up OSI with all dependencies in an isolated environment.
Users only need to run this script - no manual dependency installation required.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# Import Unicode utilities for cross-platform compatibility
try:
    from build_scripts.unicode_utils import (
        print_error,
        print_info,
        print_success,
        print_warning,
        safe_print,
    )
except ImportError:
    # Fallback if unicode_utils is not available
    def print_success(msg, **kwargs):
        print(f"[OK] {msg}", **kwargs)

    def print_error(msg, **kwargs):
        print(f"[ERROR] {msg}", **kwargs)

    def print_warning(msg, **kwargs):
        print(f"[WARNING] {msg}", **kwargs)

    def print_info(msg, **kwargs):
        print(f"[INFO] {msg}", **kwargs)

    def safe_print(msg, **kwargs):
        print(msg, **kwargs)


class OSIInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.install_dir = Path.home() / ".osi"
        self.venv_dir = self.install_dir / "venv"
        self.osi_dir = self.install_dir / "osi"

    def check_python(self):
        """Check if Python is available and compatible."""
        print("Checking Python installation...")

        if sys.version_info < (3, 11):
            print_error("Python 3.11 or higher is required")
            safe_print(f"Current version: {sys.version}")
            return False

        print_success(f"Python {sys.version.split()[0]} found")
        return True

    def create_virtual_environment(self):
        """Create a virtual environment for OSI."""
        print("Creating isolated environment for OSI...")

        try:
            # Remove existing installation
            if self.install_dir.exists():
                print("Removing existing OSI installation...")
                shutil.rmtree(self.install_dir)

            # Create install directory
            self.install_dir.mkdir(parents=True, exist_ok=True)

            # Create virtual environment
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_dir)], check=True
            )

            print_success("Virtual environment created")
            return True

        except subprocess.CalledProcessError as e:
            print_error(f"Failed to create virtual environment: {e}")
            return False

    def get_venv_python(self):
        """Get the Python executable from the virtual environment."""
        if self.system == "windows":
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"

    def get_venv_pip(self):
        """Get the pip executable from the virtual environment."""
        if self.system == "windows":
            return self.venv_dir / "Scripts" / "pip.exe"
        else:
            return self.venv_dir / "bin" / "pip"

    def install_dependencies(self):
        """Install OSI dependencies in the virtual environment."""
        print("Installing OSI dependencies...")

        python_exe = self.get_venv_python()

        # Upgrade pip first
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True
        )

        # Install dependencies
        dependencies = [
            "toml>=0.10.2",
            "packaging>=21.0",
            "virtualenv>=20.0.0",
            "pip>=21.0.0",
            "setuptools>=50.0.0",
            "wheel>=0.36.0",
            "pkginfo>=1.8.0",
        ]

        for dep in dependencies:
            print(f"Installing {dep}...")
            subprocess.run([str(python_exe), "-m", "pip", "install", dep], check=True)

        print_success("Dependencies installed")
        return True

    def download_osi_source(self):
        """Download or copy OSI source code."""
        print("Setting up OSI source code...")

        # If running from OSI directory, copy current source
        current_dir = Path(__file__).parent
        if (current_dir / "osi").exists():
            print("Copying OSI source from current directory...")
            shutil.copytree(current_dir / "osi", self.osi_dir / "osi")
            shutil.copytree(current_dir / "scripts", self.osi_dir / "scripts")

            # Copy other files
            for file in ["requirements.txt", "README.md"]:
                src = current_dir / file
                if src.exists():
                    shutil.copy(src, self.osi_dir)
        else:
            print_error("OSI source code not found in current directory")
            safe_print("Please run this installer from the OSI source directory")
            return False

        print_success("OSI source code set up")
        return True

    def create_launcher_scripts(self):
        """Create launcher scripts for easy OSI access."""
        print("Creating launcher scripts...")

        python_exe = self.get_venv_python()
        osi_script = self.osi_dir / "scripts" / "osi.py"

        # Create bin directory for launchers
        bin_dir = self.install_dir / "bin"
        bin_dir.mkdir(exist_ok=True)

        if self.system == "windows":
            # Windows batch file
            batch_content = f"""@echo off
"{python_exe}" "{osi_script}" %*
"""
            launcher = bin_dir / "osi.bat"
            with open(launcher, "w") as f:
                f.write(batch_content)

            # PowerShell script
            ps1_content = f"""& "{python_exe}" "{osi_script}" @args
"""
            ps1_launcher = bin_dir / "osi.ps1"
            with open(ps1_launcher, "w") as f:
                f.write(ps1_content)

        else:
            # Unix shell script
            shell_content = f"""#!/bin/bash
"{python_exe}" "{osi_script}" "$@"
"""
            launcher = bin_dir / "osi"
            with open(launcher, "w") as f:
                f.write(shell_content)
            launcher.chmod(0o755)

        print_success("Launcher scripts created")
        return launcher

    def test_installation(self):
        """Test the OSI installation."""
        print("Testing OSI installation...")

        python_exe = self.get_venv_python()
        osi_script = self.osi_dir / "scripts" / "osi.py"

        try:
            # Test help command
            result = subprocess.run(
                [str(python_exe), str(osi_script), "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print_success("OSI installation test passed")
                return True
            else:
                print_error(f"OSI test failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print_error("OSI test timed out")
            return False
        except Exception as e:
            print_error(f"OSI test failed: {e}")
            return False

    def add_to_path(self, launcher):
        """Provide instructions for adding OSI to PATH."""
        bin_dir = launcher.parent

        print_info("Installation Complete!")
        safe_print(f"OSI installed to: {self.install_dir}")
        safe_print(f"Launcher script: {launcher}")

        safe_print("\n[TOOL] To use OSI from anywhere, add it to your PATH:")

        if self.system == "windows":
            print(f"Add this directory to your PATH: {bin_dir}")
            print("Or run OSI using the full path:")
            print(f"  {launcher} list")
        else:
            print(f"Add this line to your ~/.bashrc or ~/.zshrc:")
            print(f'  export PATH="{bin_dir}:$PATH"')
            print("Or create a symlink:")
            print(f"  sudo ln -s {launcher} /usr/local/bin/osi")
            print("Or run OSI using the full path:")
            print(f"  {launcher} list")

    def install(self):
        """Run the complete installation process."""
        print("OSI Self-contained Installer")
        print("=" * 50)

        try:
            # Step 1: Check Python
            if not self.check_python():
                return 1

            # Step 2: Create virtual environment
            if not self.create_virtual_environment():
                return 1

            # Step 3: Install dependencies
            if not self.install_dependencies():
                return 1

            # Step 4: Set up OSI source
            if not self.download_osi_source():
                return 1

            # Step 5: Create launchers
            launcher = self.create_launcher_scripts()

            # Step 6: Test installation
            if not self.test_installation():
                return 1

            # Step 7: Provide usage instructions
            self.add_to_path(launcher)

            print("\n🎉 OSI installation completed successfully!")
            print("\nQuick start:")
            print(f"  {launcher} list")
            print(f"  {launcher} doctor")

            return 0

        except KeyboardInterrupt:
            print_error("Installation cancelled by user")
            return 1
        except Exception as e:
            print_error(f"Installation failed: {e}")
            return 1


def main():
    """Main installer entry point."""
    installer = OSIInstaller()
    return installer.install()


if __name__ == "__main__":
    sys.exit(main())

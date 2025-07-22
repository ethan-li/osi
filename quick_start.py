#!/usr/bin/env python3
"""
OSI Quick Start Script

This is the simplest way to get OSI running. Just download this file and run it.
It will automatically set up everything needed to run OSI tools.

For users: Just run "python quick_start.py" and follow the prompts.
"""

import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║                    OSI Quick Start                           ║
║              Organized Software Installer                   ║
║                                                              ║
║  This script will automatically set up OSI with all         ║
║  dependencies. No manual installation required!             ║
╚══════════════════════════════════════════════════════════════╝
"""
    )


def check_requirements():
    """Check if basic requirements are met."""
    print("🔍 Checking system requirements...")

    # Check Python version
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required. Current: {sys.version.split()[0]}")
        print("Please install a newer version of Python and try again.")
        return False

    print(f"✅ Python {sys.version.split()[0]} - OK")

    # Check internet connection
    try:
        urllib.request.urlopen("https://www.google.com", timeout=5)
        print("✅ Internet connection - OK")
    except:
        print("⚠️  Internet connection not available")
        print("   Some features may not work without internet access")

    return True


def download_osi():
    """Download OSI source code from GitHub."""
    print("\n📥 Downloading OSI from GitHub...")

    import shutil
    import tempfile
    import zipfile

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Download OSI source from GitHub
        github_url = "https://github.com/ethan-li/osi/archive/refs/heads/main.zip"
        zip_path = temp_dir / "osi.zip"

        print("Downloading OSI source code...")
        urllib.request.urlretrieve(github_url, zip_path)

        # Extract the zip file
        print("Extracting files...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find the extracted directory (should be osi-main)
        extracted_dir = temp_dir / "osi-main"
        if not extracted_dir.exists():
            # Try alternative names
            for item in temp_dir.iterdir():
                if item.is_dir() and "osi" in item.name.lower():
                    extracted_dir = item
                    break

        if extracted_dir.exists():
            print("✅ OSI source downloaded successfully")
            return extracted_dir
        else:
            print("❌ Failed to find OSI source in downloaded archive")
            return None

    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("Please check your internet connection and try again")
        return None


def setup_osi(source_dir):
    """Set up OSI in user's home directory."""
    print("\n🔧 Setting up OSI...")

    # Create OSI directory in user's home
    osi_home = Path.home() / ".osi"

    if osi_home.exists():
        print("Removing existing OSI installation...")
        import shutil

        shutil.rmtree(osi_home)

    osi_home.mkdir(parents=True)

    # Create virtual environment
    venv_dir = osi_home / "venv"
    print("Creating isolated environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # Get Python executable
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"

    # Install dependencies
    print("Installing dependencies...")
    deps = ["toml", "packaging", "virtualenv", "pkginfo"]
    for dep in deps:
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", dep],
            check=True,
            capture_output=True,
        )

    # Copy OSI source
    print("Installing OSI...")
    import shutil

    shutil.copytree(source_dir / "osi", osi_home / "osi")
    shutil.copytree(source_dir / "scripts", osi_home / "scripts")

    # Copy kits and wheels if they exist
    for dir_name in ["kits", "wheels"]:
        src_dir = source_dir / dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, osi_home / dir_name)

    return osi_home, python_exe


def create_launcher(osi_home, python_exe):
    """Create easy-to-use launcher."""
    print("\n🚀 Creating launcher...")

    launcher_dir = osi_home / "bin"
    launcher_dir.mkdir(exist_ok=True)

    osi_script = osi_home / "scripts" / "osi.py"

    if sys.platform == "win32":
        # Windows batch file
        launcher = launcher_dir / "osi.bat"
        with open(launcher, "w") as f:
            f.write(f'@echo off\n"{python_exe}" "{osi_script}" %*\n')
    else:
        # Unix shell script
        launcher = launcher_dir / "osi"
        with open(launcher, "w") as f:
            f.write(f'#!/bin/bash\n"{python_exe}" "{osi_script}" "$@"\n')
        launcher.chmod(0o755)

    return launcher


def test_installation(launcher):
    """Test the OSI installation."""
    print("\n🧪 Testing installation...")

    try:
        result = subprocess.run(
            [str(launcher), "--help"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ OSI installation successful!")
            return True
        else:
            print(f"❌ Test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_usage_instructions(launcher):
    """Show how to use OSI."""
    print(
        f"""
🎉 OSI is ready to use!

📍 Installation location: {launcher.parent.parent}
🔧 Launcher script: {launcher}

📋 Quick commands to try:

  {launcher} list              # List available tools
  {launcher} list-kits         # List available tool kits
  {launcher} doctor            # Check system status
  {launcher} --help            # Show all commands

📦 To install and run tools:

  {launcher} install text-processor    # Install a tool
  {launcher} run text-processor --help # Run a tool

🔗 To use OSI from anywhere, add this to your PATH:
  {launcher.parent}

💡 Tips:
  - Place your .whl files in: {launcher.parent.parent}/wheels/
  - Place your kits in: {launcher.parent.parent}/kits/
  - Logs are saved in: {launcher.parent.parent}/logs/

🆘 Need help? Run: {launcher} --help
"""
    )


def main():
    """Main quick start process."""
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="OSI Quick Start - Automated setup for Organized Software Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script will:
1. Check system requirements (Python 3.11+)
2. Download the latest OSI source code
3. Set up OSI in an isolated environment
4. Create launcher scripts for easy access
5. Test the installation
6. Show usage instructions

No manual configuration required - just run and follow the prompts!
        """
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Run in quiet mode with minimal output"
    )

    parser.add_argument(
        "--install-dir",
        help="Custom installation directory (default: ~/.osi)"
    )

    args = parser.parse_args()

    print_banner()

    try:
        # Step 1: Check requirements
        if not check_requirements():
            if not args.quiet:
                input("\nPress Enter to exit...")
            return 1

        # Step 2: Download OSI
        source_dir = download_osi()
        if not source_dir:
            if not args.quiet:
                input("\nPress Enter to exit...")
            return 1

        # Step 3: Set up OSI (use custom install dir if provided)
        if args.install_dir:
            # Custom installation directory logic would go here
            # For now, use the default behavior
            osi_home, python_exe = setup_osi(source_dir)
        else:
            osi_home, python_exe = setup_osi(source_dir)

        # Step 4: Create launcher
        launcher = create_launcher(osi_home, python_exe)

        # Step 5: Test installation
        if not test_installation(launcher):
            if not args.quiet:
                input("\nPress Enter to exit...")
            return 1

        # Step 6: Show usage instructions
        show_usage_instructions(launcher)

        print("\n" + "=" * 60)
        print("✅ OSI Quick Start completed successfully!")
        print("You can now close this window and start using OSI.")

        # Ask if user wants to try a command (only in interactive mode)
        if not args.quiet:
            try:
                response = input("\nWould you like to try 'osi list' now? (y/n): ")
                if response.lower().startswith("y"):
                    print(f"\nRunning: {launcher} list")
                    subprocess.run([str(launcher), "list"])
            except KeyboardInterrupt:
                pass

        return 0

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nIf you continue to have problems, please:")
        print("1. Check your internet connection")
        print("2. Ensure you have Python 3.11+ installed")
        print("3. Try running as administrator (Windows) or with sudo (Linux/macOS)")
        if not args.quiet:
            input("\nPress Enter to exit...")
        return 1


if __name__ == "__main__":
    sys.exit(main())

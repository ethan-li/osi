#!/usr/bin/env python3
"""
PyInstaller Build Script for OSI

This script builds OSI into standalone executables for different platforms
using PyInstaller. It handles platform-specific configurations and creates
optimized builds for distribution.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class OSIPyInstallerBuilder:
    """Builder class for creating OSI executables with PyInstaller"""

    def __init__(self, project_root=None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).parent.parent
        )
        self.build_dir = self.project_root / "dist"
        self.spec_file = self.project_root / "build_scripts" / "osi.spec"
        self.platform = platform.system().lower()

    def check_dependencies(self):
        """Check if PyInstaller and other build dependencies are available"""
        print("🔍 Checking build dependencies...")

        try:
            import PyInstaller

            print(f"✅ PyInstaller {PyInstaller.__version__} found")
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"],
                check=True,
            )
            print("✅ PyInstaller installed")

        # Check for UPX (optional, for compression)
        try:
            subprocess.run(["upx", "--version"], capture_output=True, check=True)
            print("✅ UPX found (will be used for compression)")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  UPX not found (optional, executable will be larger)")
            return False

    def clean_build_directory(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning build directory...")

        # Remove dist directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)

        # Remove build directory
        build_temp = self.project_root / "build"
        if build_temp.exists():
            shutil.rmtree(build_temp)

        print("✅ Build directory cleaned")

    def prepare_resources(self):
        """Prepare resource files for bundling"""
        print("📦 Preparing resources...")

        # Ensure kits directory exists with at least test kit
        kits_dir = self.project_root / "kits"
        if not kits_dir.exists():
            kits_dir.mkdir()
            print("📁 Created kits directory")

        # Ensure wheels directory exists
        wheels_dir = self.project_root / "wheels"
        if not wheels_dir.exists():
            wheels_dir.mkdir()
            print("📁 Created wheels directory")

        print("✅ Resources prepared")

    def build_executable(self, debug=False, onefile=True):
        """Build the executable using PyInstaller"""
        print(f"🔨 Building OSI executable for {self.platform}...")

        # Prepare PyInstaller command
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            str(self.spec_file),
            "--clean",
            "--noconfirm",
        ]

        if debug:
            cmd.append("--debug=all")

        # Note: Platform-specific options are handled in the .spec file
        # Don't add --console here when using a spec file

        # Run PyInstaller
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=self.project_root)

        if result.returncode != 0:
            raise RuntimeError(
                f"PyInstaller build failed with code {result.returncode}"
            )

        print("✅ Executable built successfully")

    def get_executable_path(self):
        """Get the path to the built executable"""
        if self.platform == "windows":
            return self.build_dir / "osi.exe"
        elif self.platform == "darwin":
            # Check for both .app bundle and standalone binary
            app_path = self.build_dir / "OSI.app"
            binary_path = self.build_dir / "osi"
            return app_path if app_path.exists() else binary_path
        else:  # Linux
            return self.build_dir / "osi"

    def test_executable(self):
        """Test the built executable"""
        print("🧪 Testing executable...")

        exe_path = self.get_executable_path()
        if not exe_path.exists():
            raise RuntimeError(f"Executable not found at {exe_path}")

        # Test basic functionality
        if self.platform == "darwin" and exe_path.suffix == ".app":
            # For .app bundles, test the binary inside
            test_cmd = [str(exe_path / "Contents" / "MacOS" / "osi"), "--help"]
        else:
            test_cmd = [str(exe_path), "--help"]

        try:
            result = subprocess.run(
                test_cmd, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print("✅ Executable test passed")
                return True
            else:
                print(f"❌ Executable test failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Executable test timed out")
            return False
        except Exception as e:
            print(f"❌ Executable test error: {e}")
            return False

    def create_distribution_package(self):
        """Create a distribution package with the executable"""
        print("📦 Creating distribution package...")

        exe_path = self.get_executable_path()
        if not exe_path.exists():
            raise RuntimeError("Executable not found")

        # Create distribution directory
        dist_name = f"osi-{self.platform}-{platform.machine().lower()}"
        dist_dir = self.build_dir / dist_name
        dist_dir.mkdir(exist_ok=True)

        # Copy executable
        if self.platform == "darwin" and exe_path.suffix == ".app":
            # Copy .app bundle
            shutil.copytree(exe_path, dist_dir / exe_path.name)
        else:
            # Copy binary
            shutil.copy2(exe_path, dist_dir)

        # Create README for distribution
        readme_content = f"""# OSI - Organized Software Installer

This is a standalone executable version of OSI for {self.platform}.

## Usage

Run the executable directly:
- Windows: osi.exe --help
- macOS: ./osi --help (or double-click OSI.app)
- Linux: ./osi --help

## Features

- No Python installation required
- Complete OSI functionality
- Tool management and execution
- Cross-platform compatibility

## Getting Started

1. Run `osi doctor` to check system status
2. Run `osi list` to see available tools
3. Run `osi --help` for all commands

For more information, visit: https://github.com/ethan-li/osi
"""

        (dist_dir / "README.txt").write_text(readme_content)

        # Create archive
        archive_path = self.build_dir / f"{dist_name}.zip"
        shutil.make_archive(str(archive_path.with_suffix("")), "zip", str(dist_dir))

        print(f"✅ Distribution package created: {archive_path}")
        return archive_path

    def build(self, debug=False, test=True, package=True):
        """Complete build process"""
        print(f"🚀 Starting OSI PyInstaller build for {self.platform}")

        try:
            # Check dependencies
            self.check_dependencies()

            # Clean previous builds
            self.clean_build_directory()

            # Prepare resources
            self.prepare_resources()

            # Build executable
            self.build_executable(debug=debug)

            # Test executable
            if test:
                if not self.test_executable():
                    print("⚠️  Executable test failed, but build completed")

            # Create distribution package
            if package:
                archive_path = self.create_distribution_package()
                print(f"🎉 Build completed successfully!")
                print(f"📦 Distribution package: {archive_path}")
            else:
                exe_path = self.get_executable_path()
                print(f"🎉 Build completed successfully!")
                print(f"🔧 Executable: {exe_path}")

            return True

        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Build OSI with PyInstaller")
    parser.add_argument(
        "--debug", action="store_true", help="Build with debug information"
    )
    parser.add_argument(
        "--no-test", action="store_true", help="Skip executable testing"
    )
    parser.add_argument(
        "--no-package", action="store_true", help="Skip creating distribution package"
    )
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    builder = OSIPyInstallerBuilder(args.project_root)
    success = builder.build(
        debug=args.debug, test=not args.no_test, package=not args.no_package
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

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

# Import Unicode utilities for cross-platform compatibility
from unicode_utils import (
    print_build,
    print_error,
    print_package,
    print_search,
    print_success,
    print_warning,
    safe_print,
)


class OSIPyInstallerBuilder:
    """Builder class for creating OSI executables with PyInstaller"""

    def __init__(self, project_root=None):
        # Try to find the project root in multiple ways
        if project_root:
            self.project_root = Path(project_root)
        elif os.environ.get("OSI_PROJECT_ROOT"):
            # Allow override via environment variable (useful for CI)
            self.project_root = Path(os.environ["OSI_PROJECT_ROOT"])
            safe_print(
                f"[INFO] Using project root from OSI_PROJECT_ROOT: {self.project_root}"
            )
        else:
            # Default: parent of the directory containing this script
            self.project_root = Path(__file__).parent.parent

        # Verify project root by checking for key files
        self._verify_project_root()

        self.build_dir = self.project_root / "dist"
        self.spec_file = self.project_root / "build_scripts" / "osi.spec"
        self.platform = platform.system().lower()

    def _verify_project_root(self):
        """Verify and potentially correct the project root by checking for key files."""
        # Check if key files exist in the project root
        key_files = ["osi_main.py", "setup.py", "requirements.txt"]

        # Debug info
        safe_print(f"[DEBUG] Initial project_root: {self.project_root}")
        for file in key_files:
            file_path = self.project_root / file
            exists = file_path.exists()
            safe_print(f"[DEBUG] {file} exists: {exists}")

        # If key files are missing, try to find the correct project root
        if not all((self.project_root / file).exists() for file in key_files):
            safe_print(
                "[WARNING] Project root may be incorrect, searching for correct location..."
            )

            # Try common locations
            potential_roots = [
                Path.cwd(),  # Current working directory
                Path.cwd().parent,  # Parent of current working directory
                Path(
                    __file__
                ).parent.parent,  # Parent of the directory containing this script
                Path(
                    __file__
                ).parent.parent.parent,  # Grandparent of the directory containing this script
            ]

            for potential_root in potential_roots:
                safe_print(f"[DEBUG] Checking potential root: {potential_root}")
                if all((potential_root / file).exists() for file in key_files):
                    safe_print(
                        f"[SUCCESS] Found correct project root: {potential_root}"
                    )
                    self.project_root = potential_root
                    return

            # If we get here, we couldn't find a valid project root
            safe_print(
                "[ERROR] Could not find valid project root with all required files"
            )
            safe_print("[DEBUG] Will continue with best guess, but build may fail")

    def check_dependencies(self):
        """Check if PyInstaller and other build dependencies are available"""
        print_search("Checking build dependencies...")

        try:
            import PyInstaller

            print_success(f"PyInstaller {PyInstaller.__version__} found")
        except ImportError:
            print_error("PyInstaller not found. Installing...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"],
                check=True,
            )
            print_success("PyInstaller installed")

        # Check for UPX (optional, for compression)
        try:
            subprocess.run(["upx", "--version"], capture_output=True, check=True)
            print_success("UPX found (will be used for compression)")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_warning("UPX not found (optional, executable will be larger)")
            return False

    def clean_build_directory(self):
        """Clean previous build artifacts"""
        safe_print("[CLEAN] Cleaning build directory...")

        # Remove dist directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)

        # Remove build directory
        build_temp = self.project_root / "build"
        if build_temp.exists():
            shutil.rmtree(build_temp)

        print_success("Build directory cleaned")

    def prepare_resources(self):
        """Prepare resource files for bundling"""
        print_package("Preparing resources...")

        # Ensure kits directory exists with at least test kit
        kits_dir = self.project_root / "kits"
        if not kits_dir.exists():
            kits_dir.mkdir()
            safe_print("[FOLDER] Created kits directory")

        # Ensure wheels directory exists
        wheels_dir = self.project_root / "wheels"
        if not wheels_dir.exists():
            wheels_dir.mkdir()
            safe_print("[FOLDER] Created wheels directory")

        print_success("Resources prepared")

    def build_executable(self, debug=False, onefile=True):
        """Build the executable using PyInstaller"""
        print_build(f"Building OSI executable for {self.platform}...")

        # Debug information for CI troubleshooting
        safe_print(f"[DEBUG] Project root: {self.project_root}")
        safe_print(f"[DEBUG] Spec file: {self.spec_file}")
        safe_print(f"[DEBUG] Spec file exists: {self.spec_file.exists()}")
        safe_print(f"[DEBUG] Current working directory: {os.getcwd()}")

        # Check for main entry point
        main_script = self.project_root / "osi_main.py"
        safe_print(f"[DEBUG] Main script: {main_script}")
        safe_print(f"[DEBUG] Main script exists: {main_script.exists()}")

        if not main_script.exists():
            print_error(f"Main script not found: {main_script}")
            # List files in project root for debugging
            safe_print("[DEBUG] Files in project root:")
            for file in self.project_root.glob("*.py"):
                safe_print(f"[DEBUG]   {file}")
            raise RuntimeError(f"Main script not found: {main_script}")

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
        safe_print(f"Running: {' '.join(cmd)}")
        safe_print(f"Working directory: {self.project_root}")

        result = subprocess.run(
            cmd, cwd=self.project_root, capture_output=True, text=True
        )

        if result.returncode != 0:
            print_error("PyInstaller build failed!")
            safe_print(f"Return code: {result.returncode}")
            safe_print(f"STDOUT:\n{result.stdout}")
            safe_print(f"STDERR:\n{result.stderr}")
            raise RuntimeError(
                f"PyInstaller build failed with code {result.returncode}"
            )

        print_success("Executable built successfully")

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
        safe_print("[TEST] Testing executable...")

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
                print_success("Executable test passed")
                return True
            else:
                print_error(f"Executable test failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print_error("Executable test timed out")
            return False
        except Exception as e:
            print_error(f"Executable test error: {e}")
            return False

    def create_distribution_package(self):
        """Create a distribution package with the executable"""
        print_package("Creating distribution package...")

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

        print_success(f"Distribution package created: {archive_path}")
        return archive_path

    def generate_license_report(self):
        """Generate license report for legal compliance"""
        safe_print("[LEGAL] Generating license report for third-party dependencies...")

        try:
            # Import the license reporter
            license_script = self.project_root / "build_scripts" / "generate_license_report.py"
            if not license_script.exists():
                print_warning("License report generator not found")
                return False

            # Generate license report (using legacy mode for backward compatibility)
            result = subprocess.run([
                sys.executable, str(license_script),
                "--legacy-mode", "--runtime-only",
                "--output", str(self.project_root / "THIRD_PARTY_LICENSES.txt")
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print_success("License report generated: THIRD_PARTY_LICENSES.txt")
                return True
            else:
                print_warning(f"License report generation failed: {result.stderr}")
                return False

        except Exception as e:
            print_warning(f"License report generation error: {e}")
            return False

    def build(self, debug=False, test=True, package=True):
        """Complete build process"""
        safe_print(f"[LAUNCH] Starting OSI PyInstaller build for {self.platform}")

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
                    print_warning("Executable test failed, but build completed")

            # Generate license report for legal compliance
            self.generate_license_report()

            # Create distribution package
            if package:
                archive_path = self.create_distribution_package()
                safe_print("[SUCCESS] Build completed successfully!")
                print_package(f"Distribution package: {archive_path}")
            else:
                exe_path = self.get_executable_path()
                safe_print("[SUCCESS] Build completed successfully!")
                safe_print(f"[TOOL] Executable: {exe_path}")

            return True

        except Exception as e:
            print_error(f"Build failed: {e}")
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
    parser.add_argument(
        "--package", action="store_true", help="Force creating distribution package"
    )
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    # Determine package flag: --package forces True, --no-package forces False, default True
    if args.package:
        package = True
    elif args.no_package:
        package = False
    else:
        package = True  # Default to creating package

    builder = OSIPyInstallerBuilder(args.project_root)
    success = builder.build(debug=args.debug, test=not args.no_test, package=package)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

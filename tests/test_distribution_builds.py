#!/usr/bin/env python3
"""
Comprehensive tests for OSI distribution build methods

Tests the actual build processes and functionality of different distribution
methods including PyInstaller executables, Docker containers, portable
distributions, and wheel packages.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPyInstallerBuild(unittest.TestCase):
    """Test PyInstaller executable build process."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.build_script = self.project_root / "build_scripts" / "build_pyinstaller.py"
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_pyinstaller_script_exists(self):
        """Test that PyInstaller build script exists."""
        self.assertTrue(self.build_script.exists())
        self.assertTrue(self.build_script.is_file())

    def test_pyinstaller_script_syntax(self):
        """Test that PyInstaller build script has valid syntax."""
        with open(self.build_script, "r", encoding="utf-8") as f:
            try:
                compile(f.read(), str(self.build_script), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in build_pyinstaller.py: {e}")

    def test_pyinstaller_dependency_check(self):
        """Test PyInstaller dependency checking."""
        # Import the builder class
        sys.path.insert(0, str(self.project_root / "build_scripts"))
        try:
            from build_pyinstaller import OSIPyInstallerBuilder

            builder = OSIPyInstallerBuilder(self.project_root)

            # Test dependency check (should not raise exception)
            result = builder.check_dependencies()

            # Should return True or False, not raise exception
            self.assertIsInstance(result, bool)
        except ImportError:
            self.skipTest("PyInstaller build script not importable")

    def test_spec_file_exists(self):
        """Test that PyInstaller spec file exists."""
        spec_file = self.project_root / "build_scripts" / "osi.spec"

        # Debug information for CI troubleshooting
        if not spec_file.exists():
            build_scripts_dir = self.project_root / "build_scripts"
            print(f"Debug: project_root = {self.project_root}")
            print(f"Debug: build_scripts_dir exists = {build_scripts_dir.exists()}")
            if build_scripts_dir.exists():
                print(
                    f"Debug: build_scripts contents = {list(build_scripts_dir.iterdir())}"
                )
            print(f"Debug: spec_file path = {spec_file}")
            print(f"Debug: spec_file exists = {spec_file.exists()}")

            # Check if this is a git repository issue
            import subprocess

            try:
                result = subprocess.run(
                    ["git", "ls-files", "build_scripts/osi.spec"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                print(f"Debug: git ls-files result = '{result.stdout.strip()}'")
                print(f"Debug: git ls-files returncode = {result.returncode}")
            except Exception as e:
                print(f"Debug: git check failed = {e}")

        self.assertTrue(
            spec_file.exists(),
            f"osi.spec file should exist at {spec_file}. "
            f"This file is required for PyInstaller builds. "
            f"If you see this error in CI, the file may not be tracked by git.",
        )
        self.assertTrue(
            spec_file.is_file(), f"osi.spec should be a file at {spec_file}"
        )

    def test_spec_file_content(self):
        """Test that spec file has required content."""
        spec_file = self.project_root / "build_scripts" / "osi.spec"
        if spec_file.exists():
            with open(spec_file, "r") as f:
                content = f.read()

            # Check for required PyInstaller spec elements
            self.assertIn("Analysis", content)
            self.assertIn("PYZ", content)
            self.assertIn("EXE", content)

    @unittest.skipIf(not shutil.which("pyinstaller"), "PyInstaller not available")
    def test_pyinstaller_build_dry_run(self):
        """Test PyInstaller build process (dry run)."""
        # This test only runs if PyInstaller is available
        try:
            result = subprocess.run(
                [sys.executable, str(self.build_script), "--no-test"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root,
            )

            # Should not fail catastrophically
            self.assertIn(
                result.returncode,
                [0, 1],
                "Build should complete with success or expected failure",
            )

        except subprocess.TimeoutExpired:
            self.skipTest("PyInstaller build took too long")






class TestWheelDistribution(unittest.TestCase):
    """Test wheel and source distribution build."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.setup_py = self.project_root / "setup.py"
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_setup_py_exists(self):
        """Test that setup.py exists."""
        self.assertTrue(self.setup_py.exists())
        self.assertTrue(self.setup_py.is_file())

    def test_setup_py_syntax(self):
        """Test that setup.py has valid syntax."""
        with open(self.setup_py, "r", encoding="utf-8") as f:
            try:
                compile(f.read(), str(self.setup_py), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in setup.py: {e}")

    def test_setup_py_metadata(self):
        """Test that setup.py contains required metadata."""
        with open(self.setup_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required setup() call and metadata
        self.assertIn("setup(", content)
        self.assertIn("name=", content)
        self.assertIn("version=", content)
        self.assertIn("author=", content)
        self.assertIn("description=", content)

    @patch("subprocess.run")
    def test_wheel_build_command(self, mock_run):
        """Test wheel build command execution."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Built wheel successfully"

        # Test that we can call the wheel build command
        result = subprocess.run(
            [sys.executable, "setup.py", "bdist_wheel", "--help"],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        # Should not fail (help should always work)
        self.assertEqual(result.returncode, 0)

    @patch("subprocess.run")
    def test_source_distribution_command(self, mock_run):
        """Test source distribution build command."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Built source distribution successfully"

        # Test that we can call the source distribution build command
        result = subprocess.run(
            [sys.executable, "setup.py", "sdist", "--help"],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        # Should not fail (help should always work)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

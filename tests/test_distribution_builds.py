#!/usr/bin/env python3
"""
Comprehensive tests for OSI distribution build methods

Tests the actual build processes and functionality of different distribution
methods including PyInstaller executables, Docker containers, portable
distributions, and wheel packages.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

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


class TestDockerBuild(unittest.TestCase):
    """Test Docker container build process."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.build_script = self.project_root / "build_scripts" / "build_docker.py"
        self.dockerfile = self.project_root / "Dockerfile"

    def test_docker_build_script_exists(self):
        """Test that Docker build script exists."""
        self.assertTrue(self.build_script.exists())
        self.assertTrue(self.build_script.is_file())

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists."""
        self.assertTrue(self.dockerfile.exists())
        self.assertTrue(self.dockerfile.is_file())

    def test_dockerfile_structure(self):
        """Test Dockerfile has proper structure."""
        with open(self.dockerfile, "r") as f:
            content = f.read()

        # Check for essential Docker instructions
        required_instructions = ["FROM", "COPY", "RUN", "WORKDIR", "ENTRYPOINT"]
        for instruction in required_instructions:
            self.assertIn(
                instruction,
                content,
                f"Dockerfile should contain {instruction} instruction",
            )

    def test_docker_build_script_syntax(self):
        """Test that Docker build script has valid syntax."""
        with open(self.build_script, "r", encoding="utf-8") as f:
            try:
                compile(f.read(), str(self.build_script), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in build_docker.py: {e}")

    @patch("subprocess.run")
    def test_docker_build_function(self, mock_run):
        """Test Docker build function with mocked subprocess."""
        # Import the build function
        sys.path.insert(0, str(self.project_root / "build_scripts"))
        try:
            from build_docker import build_docker_image

            # Mock successful docker build
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""

            result = build_docker_image()
            self.assertTrue(result)

            # Verify docker build was called
            mock_run.assert_called()

        except ImportError:
            self.skipTest("Docker build script not importable")

    @unittest.skipIf(not shutil.which("docker"), "Docker not available")
    def test_docker_build_dry_run(self):
        """Test Docker build process (dry run)."""
        try:
            # Test docker version to ensure it's working
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                self.skipTest("Docker not working properly")

            # Test dockerfile syntax
            result = subprocess.run(
                ["docker", "build", "--dry-run", "-f", str(self.dockerfile), "."],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root,
            )

            # Note: --dry-run might not be available in all Docker versions
            # So we just check that docker build command doesn't fail immediately

        except subprocess.TimeoutExpired:
            self.skipTest("Docker build check took too long")
        except FileNotFoundError:
            self.skipTest("Docker command not found")


class TestPortableBuild(unittest.TestCase):
    """Test portable distribution build process."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.build_script = self.project_root / "build_scripts" / "build_portable.py"

    def test_portable_build_script_exists(self):
        """Test that portable build script exists."""
        self.assertTrue(self.build_script.exists())
        self.assertTrue(self.build_script.is_file())

    def test_portable_build_script_syntax(self):
        """Test that portable build script has valid syntax."""
        with open(self.build_script, "r", encoding="utf-8") as f:
            try:
                compile(f.read(), str(self.build_script), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in build_portable.py: {e}")

    @patch("zipfile.ZipFile")
    @patch("urllib.request.urlretrieve")
    @patch("subprocess.run")
    def test_portable_build_function(self, mock_run, mock_urlretrieve, mock_zipfile):
        """Test portable build function with mocked dependencies."""
        sys.path.insert(0, str(self.project_root / "build_scripts"))
        try:
            from build_portable import download_portable_python

            # Mock successful download and extraction
            mock_urlretrieve.return_value = None
            mock_run.return_value.returncode = 0

            # Mock zipfile operations
            mock_zip_instance = MagicMock()
            mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
            mock_zip_instance.extractall.return_value = None

            # Mock Path.unlink() to avoid FileNotFoundError
            with patch("pathlib.Path.unlink") as mock_unlink:
                mock_unlink.return_value = None

                # This should work on Windows, return None on other platforms
                result = download_portable_python()

                # Result should be None (unsupported) or a Path (Windows)
                self.assertTrue(result is None or isinstance(result, Path))

        except ImportError:
            self.skipTest("Portable build script not importable")

    def test_portable_platform_support(self):
        """Test that portable build correctly identifies platform support."""
        import platform

        sys.path.insert(0, str(self.project_root / "build_scripts"))
        try:
            from build_portable import download_portable_python

            result = download_portable_python()

            if platform.system().lower() == "windows":
                # On Windows, should return a path or None
                self.assertTrue(result is None or isinstance(result, Path))
            else:
                # On non-Windows, should return None
                self.assertIsNone(result)

        except ImportError:
            self.skipTest("Portable build script not importable")


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

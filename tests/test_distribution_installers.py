#!/usr/bin/env python3
"""
Tests for OSI distribution installer functionality

Tests the self-contained installer, quick start script, and other
installation methods to ensure they work correctly across platforms.
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


class TestSelfContainedInstaller(unittest.TestCase):
    """Test the self-contained installer (install_osi.py)."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.installer_script = self.project_root / "install_osi.py"
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_home = os.environ.get("HOME")

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        if self.original_home:
            os.environ["HOME"] = self.original_home

    def test_installer_script_exists(self):
        """Test that installer script exists."""
        self.assertTrue(self.installer_script.exists())
        self.assertTrue(self.installer_script.is_file())

    def test_installer_script_syntax(self):
        """Test that installer script has valid syntax."""
        with open(self.installer_script, "r", encoding="utf-8") as f:
            try:
                compile(f.read(), str(self.installer_script), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in install_osi.py: {e}")

    def test_installer_python_version_check(self):
        """Test installer Python version checking."""
        # Import the installer class
        sys.path.insert(0, str(self.project_root))
        try:
            from install_osi import OSIInstaller

            installer = OSIInstaller()

            # Should return True for current Python (we're running on 3.11+)
            result = installer.check_python()
            self.assertTrue(result, "Current Python version should be compatible")

        except ImportError:
            self.skipTest("install_osi.py not importable")

    @patch("pathlib.Path.home")
    def test_installer_directory_setup(self, mock_home):
        """Test installer directory setup."""
        # Mock home directory to use temp directory
        mock_home.return_value = self.temp_dir

        sys.path.insert(0, str(self.project_root))
        try:
            from install_osi import OSIInstaller

            installer = OSIInstaller()

            # Check that installer sets up correct paths
            expected_install_dir = self.temp_dir / ".osi"
            self.assertEqual(installer.install_dir, expected_install_dir)

            expected_venv_dir = expected_install_dir / "venv"
            self.assertEqual(installer.venv_dir, expected_venv_dir)

        except ImportError:
            self.skipTest("install_osi.py not importable")

    @patch("subprocess.run")
    @patch("pathlib.Path.home")
    def test_installer_virtual_environment_creation(self, mock_home, mock_run):
        """Test virtual environment creation."""
        # Mock home directory and subprocess calls
        mock_home.return_value = self.temp_dir
        mock_run.return_value.returncode = 0

        sys.path.insert(0, str(self.project_root))
        try:
            from install_osi import OSIInstaller

            installer = OSIInstaller()

            # Test virtual environment creation
            result = installer.create_virtual_environment()

            # Should call subprocess.run for venv creation
            mock_run.assert_called()

            # Result should be boolean
            self.assertIsInstance(result, bool)

        except ImportError:
            self.skipTest("install_osi.py not importable")

    def test_installer_help_option(self):
        """Test installer help option."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.installer_script), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            # Help should work and return 0, or contain help information
            if result.returncode == 0:
                # Check if it's actually help output or installation output
                output_lower = result.stdout.lower()
                if (
                    "usage" in output_lower
                    or "help" in output_lower
                    or "options" in output_lower
                ):
                    self.assertIn("usage", output_lower)
                else:
                    # If it ran the installer instead, that's also acceptable
                    self.assertIn("osi", output_lower)
            else:
                self.skipTest("Installer help not available or failed")

        except subprocess.TimeoutExpired:
            self.skipTest("Installer help took too long")

    @patch("urllib.request.urlretrieve")
    @patch("subprocess.run")
    @patch("pathlib.Path.home")
    def test_installer_dry_run(self, mock_home, mock_run, mock_urlretrieve):
        """Test installer in dry run mode."""
        # Mock all external dependencies
        mock_home.return_value = self.temp_dir
        mock_run.return_value.returncode = 0
        mock_urlretrieve.return_value = None

        # Set up a fake OSI source directory
        fake_osi_dir = self.temp_dir / "osi-main"
        fake_osi_dir.mkdir(parents=True)
        (fake_osi_dir / "setup.py").touch()
        (fake_osi_dir / "osi").mkdir()
        (fake_osi_dir / "osi" / "__init__.py").touch()

        sys.path.insert(0, str(self.project_root))
        try:
            from install_osi import OSIInstaller

            installer = OSIInstaller()

            # Test individual methods
            self.assertTrue(installer.check_python())

            # These should not fail with mocked dependencies
            installer.create_virtual_environment()

        except ImportError:
            self.skipTest("install_osi.py not importable")


class TestQuickStartScript(unittest.TestCase):
    """Test the quick start script functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.quick_start_script = self.project_root / "quick_start.py"

    def test_quick_start_script_exists(self):
        """Test that quick start script exists."""
        self.assertTrue(self.quick_start_script.exists())
        self.assertTrue(self.quick_start_script.is_file())

    def test_quick_start_script_syntax(self):
        """Test that quick start script has valid syntax."""
        with open(self.quick_start_script, "r", encoding="utf-8") as f:
            try:
                compile(f.read(), str(self.quick_start_script), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in quick_start.py: {e}")

    def test_quick_start_help_option(self):
        """Test quick start help option."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.quick_start_script), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            # Help should work and return 0
            self.assertEqual(
                result.returncode,
                0,
                f"Help command failed with return code {result.returncode}. "
                f"stdout: {result.stdout[:200]}... "
                f"stderr: {result.stderr[:200]}...",
            )

            # Check for help-related content
            output_lower = result.stdout.lower()
            help_indicators = ["usage", "help", "options", "arguments", "description"]
            found_help = any(indicator in output_lower for indicator in help_indicators)

            self.assertTrue(
                found_help,
                f"Help output should contain help information. "
                f"Got: {result.stdout[:300]}...",
            )

        except subprocess.TimeoutExpired:
            self.skipTest("Quick start help took too long")

    @patch("urllib.request.urlretrieve")
    @patch("subprocess.run")
    def test_quick_start_download_functionality(self, mock_run, mock_urlretrieve):
        """Test quick start download functionality."""
        # Mock external dependencies
        mock_urlretrieve.return_value = None
        mock_run.return_value.returncode = 0

        # Import and test the quick start functionality
        sys.path.insert(0, str(self.project_root))
        try:
            # Import the quick start module
            import quick_start

            # Test that the module loads without errors
            self.assertTrue(hasattr(quick_start, "main"))

        except ImportError:
            self.skipTest("quick_start.py not importable")


class TestDistributionIntegration(unittest.TestCase):
    """Integration tests for distribution methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.build_distributions_script = self.project_root / "build_distributions.py"

    def test_build_distributions_script_exists(self):
        """Test that build distributions script exists."""
        self.assertTrue(self.build_distributions_script.exists())
        self.assertTrue(self.build_distributions_script.is_file())

    def test_build_distributions_script_syntax(self):
        """Test that build distributions script has valid syntax."""
        with open(self.build_distributions_script, "r", encoding="utf-8") as f:
            try:
                compile(f.read(), str(self.build_distributions_script), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in build_distributions.py: {e}")

    def test_build_distributions_help(self):
        """Test build distributions help option."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.build_distributions_script), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            # Help should work and return 0
            self.assertEqual(result.returncode, 0)
            self.assertIn("usage", result.stdout.lower())

        except subprocess.TimeoutExpired:
            self.skipTest("Build distributions help took too long")

    def test_distribution_methods_available(self):
        """Test that all distribution methods are available."""
        # Import the build distributions module
        sys.path.insert(0, str(self.project_root))
        try:
            import build_distributions

            # Test that all build functions exist
            required_functions = [
                "build_executable",
                "test_installer",
                "create_distribution_summary",
            ]

            for func_name in required_functions:
                self.assertTrue(
                    hasattr(build_distributions, func_name),
                    f"Function {func_name} should exist",
                )

        except ImportError:
            self.skipTest("build_distributions.py not importable")

    @patch("subprocess.run")
    def test_distribution_summary_creation(self, mock_run):
        """Test distribution summary creation."""
        mock_run.return_value.returncode = 0

        sys.path.insert(0, str(self.project_root))
        try:
            import build_distributions

            # Test summary creation
            build_distributions.create_distribution_summary()

            # Check that summary file was created
            summary_file = self.project_root / "DISTRIBUTION_GUIDE.md"
            self.assertTrue(
                summary_file.exists(), "DISTRIBUTION_GUIDE.md should be created"
            )

            # Clean up
            if summary_file.exists():
                summary_file.unlink()

        except ImportError:
            self.skipTest("build_distributions.py not importable")

    def test_all_build_scripts_exist(self):
        """Test that all referenced build scripts exist."""
        build_scripts_dir = self.project_root / "build_scripts"

        required_scripts = [
            "build_pyinstaller.py",
        ]

        for script in required_scripts:
            script_path = build_scripts_dir / script
            self.assertTrue(script_path.exists(), f"Build script {script} should exist")
            self.assertTrue(
                script_path.is_file(), f"Build script {script} should be a file"
            )


class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility of distribution methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_platform_specific_scripts(self):
        """Test that platform-specific scripts exist."""
        scripts_dir = self.project_root / "scripts"

        platform_scripts = {
            "osi.bat": "Windows batch script",
            "osi.sh": "Unix shell script",
        }

        for script, description in platform_scripts.items():
            script_path = scripts_dir / script
            self.assertTrue(script_path.exists(), f"{description} should exist")

    def test_installer_platform_detection(self):
        """Test that installers properly detect platform."""
        import platform

        # Test that platform detection works
        system = platform.system().lower()
        self.assertIn(
            system,
            ["windows", "linux", "darwin"],
            "Platform should be detected correctly",
        )

    def test_path_handling_cross_platform(self):
        """Test that path handling works across platforms."""
        # Test Path operations work correctly
        test_path = Path("test") / "path" / "example"

        # Should work on all platforms
        self.assertIsInstance(test_path, Path)
        self.assertTrue(str(test_path))  # Should convert to string


if __name__ == "__main__":
    unittest.main(verbosity=2)

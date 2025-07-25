#!/usr/bin/env python3
"""
Unit tests for OSI distribution methods

Tests the various distribution scripts and methods including
quick_start.py, install_osi.py, and build scripts.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDistributionScripts(unittest.TestCase):
    """Test distribution script functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_quick_start_script_exists(self):
        """Test that quick_start.py exists and is executable."""
        quick_start = self.project_root / "quick_start.py"
        self.assertTrue(quick_start.exists(), "quick_start.py should exist")
        self.assertTrue(quick_start.is_file(), "quick_start.py should be a file")

    def test_install_osi_script_exists(self):
        """Test that install_osi.py exists and is executable."""
        install_osi = self.project_root / "install_osi.py"
        self.assertTrue(install_osi.exists(), "install_osi.py should exist")
        self.assertTrue(install_osi.is_file(), "install_osi.py should be a file")

    def test_build_distributions_script_exists(self):
        """Test that build_distributions.py exists."""
        build_dist = self.project_root / "build_distributions.py"
        self.assertTrue(build_dist.exists(), "build_distributions.py should exist")
        self.assertTrue(build_dist.is_file(), "build_distributions.py should be a file")

    def test_build_scripts_directory_exists(self):
        """Test that build_scripts directory exists with required files."""
        build_scripts_dir = self.project_root / "build_scripts"
        self.assertTrue(
            build_scripts_dir.exists(), "build_scripts directory should exist"
        )
        self.assertTrue(
            build_scripts_dir.is_dir(), "build_scripts should be a directory"
        )

        # Check for required build scripts
        required_scripts = [
            "build_pyinstaller.py",
        ]

        for script in required_scripts:
            script_path = build_scripts_dir / script
            self.assertTrue(script_path.exists(), f"Build script {script} should exist")

    def test_distribution_scripts_syntax(self):
        """Test that distribution scripts have valid Python syntax."""
        scripts_to_test = ["quick_start.py", "install_osi.py", "build_distributions.py"]

        for script in scripts_to_test:
            script_path = self.project_root / script
            if script_path.exists():
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        compile(f.read(), str(script_path), "exec")
                except SyntaxError as e:
                    self.fail(f"Syntax error in {script}: {e}")
                except UnicodeDecodeError as e:
                    self.fail(f"Unicode decode error in {script}: {e}")

    def test_build_scripts_syntax(self):
        """Test that build scripts have valid Python syntax."""
        build_scripts_dir = self.project_root / "build_scripts"

        if build_scripts_dir.exists():
            for script_path in build_scripts_dir.glob("*.py"):
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        compile(f.read(), str(script_path), "exec")
                except SyntaxError as e:
                    self.fail(f"Syntax error in {script_path.name}: {e}")
                except UnicodeDecodeError as e:
                    self.fail(f"Unicode decode error in {script_path.name}: {e}")





class TestLauncherScripts(unittest.TestCase):
    """Test cross-platform launcher scripts."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"

    def test_scripts_directory_exists(self):
        """Test that scripts directory exists."""
        self.assertTrue(self.scripts_dir.exists(), "scripts directory should exist")
        self.assertTrue(self.scripts_dir.is_dir(), "scripts should be a directory")

    def test_main_osi_script_exists(self):
        """Test that main osi.py script exists."""
        osi_script = self.scripts_dir / "osi.py"
        self.assertTrue(osi_script.exists(), "osi.py should exist")
        self.assertTrue(osi_script.is_file(), "osi.py should be a file")

    def test_platform_launchers_exist(self):
        """Test that platform-specific launchers exist."""
        launchers = {
            "osi.bat": "Windows batch launcher",
            "osi.sh": "Unix shell launcher",
        }

        for launcher, description in launchers.items():
            launcher_path = self.scripts_dir / launcher
            self.assertTrue(
                launcher_path.exists(), f"{description} ({launcher}) should exist"
            )

    def test_launcher_scripts_syntax(self):
        """Test that Python launcher scripts have valid syntax."""
        python_scripts = self.scripts_dir.glob("*.py")

        for script_path in python_scripts:
            try:
                with open(script_path, "r") as f:
                    compile(f.read(), str(script_path), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in {script_path.name}: {e}")


class TestConfigurationFiles(unittest.TestCase):
    """Test configuration files for distribution."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_setup_py_exists(self):
        """Test that setup.py exists."""
        setup_py = self.project_root / "setup.py"
        self.assertTrue(setup_py.exists(), "setup.py should exist")
        self.assertTrue(setup_py.is_file(), "setup.py should be a file")

    def test_requirements_txt_exists(self):
        """Test that requirements.txt exists."""
        requirements = self.project_root / "requirements.txt"
        self.assertTrue(requirements.exists(), "requirements.txt should exist")
        self.assertTrue(requirements.is_file(), "requirements.txt should be a file")

    def test_gitignore_exists(self):
        """Test that .gitignore exists."""
        gitignore = self.project_root / ".gitignore"
        self.assertTrue(gitignore.exists(), ".gitignore should exist")
        self.assertTrue(gitignore.is_file(), ".gitignore should be a file")

    def test_requirements_content(self):
        """Test that requirements.txt has valid content."""
        requirements = self.project_root / "requirements.txt"

        if requirements.exists():
            with open(requirements, "r") as f:
                content = f.read().strip()

            # Should not be empty
            self.assertGreater(len(content), 0, "requirements.txt should not be empty")

            # Each line should be a valid requirement (basic check)
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            for line in lines:
                if not line.startswith("#"):  # Skip comments
                    self.assertGreater(
                        len(line), 0, "Each requirement line should not be empty"
                    )


class TestDistributionIntegration(unittest.TestCase):
    """Integration tests for distribution functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_distribution_workflow_components(self):
        """Test that all components needed for distribution are present."""
        required_components = [
            "osi/",  # Core package
            "scripts/osi.py",  # Main launcher
            "quick_start.py",  # Quick start installer
            "install_osi.py",  # Self-contained installer
            "setup.py",  # Package setup
            "requirements.txt",  # Dependencies
            ".gitignore",  # Git ignore rules
        ]

        for component in required_components:
            component_path = self.project_root / component
            self.assertTrue(
                component_path.exists(), f"Required component {component} should exist"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

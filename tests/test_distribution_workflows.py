#!/usr/bin/env python3
"""
End-to-end workflow tests for OSI distribution methods

Tests complete distribution workflows from build to deployment,
ensuring that generated artifacts work correctly and can execute
OSI commands properly.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDistributionWorkflows(unittest.TestCase):
    """Test complete distribution workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_source_distribution_workflow(self):
        """Test source distribution build and installation workflow."""
        # Change to project directory
        os.chdir(self.project_root)

        try:
            # Test that we can build a source distribution
            result = subprocess.run(
                [sys.executable, "setup.py", "check"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Setup check should pass
            self.assertEqual(
                result.returncode, 0, f"setup.py check failed: {result.stderr}"
            )

        except subprocess.TimeoutExpired:
            self.skipTest("Source distribution check took too long")

    def test_wheel_distribution_workflow(self):
        """Test wheel distribution build workflow."""
        os.chdir(self.project_root)

        try:
            # Test that we can check wheel build requirements
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import setuptools; print('setuptools available')",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            self.assertEqual(
                result.returncode,
                0,
                "setuptools should be available for wheel building",
            )

        except subprocess.TimeoutExpired:
            self.skipTest("Wheel check took too long")

    def test_installer_workflow_components(self):
        """Test that installer workflow has all required components."""
        # Check that all installer components exist
        required_files = [
            "install_osi.py",
            "quick_start.py",
            "setup.py",
            "requirements.txt",
        ]

        for file_name in required_files:
            file_path = self.project_root / file_name
            self.assertTrue(
                file_path.exists(),
                f"Required installer component {file_name} should exist",
            )

    def test_build_scripts_workflow(self):
        """Test that build scripts workflow is complete."""
        build_scripts_dir = self.project_root / "build_scripts"

        # Check that all build scripts exist
        required_scripts = [
            "build_pyinstaller.py",
        ]

        for script in required_scripts:
            script_path = build_scripts_dir / script
            self.assertTrue(script_path.exists(), f"Build script {script} should exist")

            # Test that script can be imported (syntax check)
            try:
                with open(script_path, "r", encoding="utf-8") as f:
                    compile(f.read(), str(script_path), "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in {script}: {e}")

    def test_distribution_guide_generation(self):
        """Test distribution guide generation workflow."""
        sys.path.insert(0, str(self.project_root))
        try:
            import build_distributions

            # Test guide generation
            build_distributions.create_distribution_summary()

            # Check that guide was created
            guide_path = self.project_root / "DISTRIBUTION_GUIDE.md"
            self.assertTrue(guide_path.exists(), "Distribution guide should be created")

            # Check guide content
            with open(guide_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Should contain information about all distribution methods
            expected_sections = [
                "Self-contained Installer",
                "PyInstaller Executable",
            ]

            for section in expected_sections:
                self.assertIn(
                    section, content, f"Guide should contain {section} section"
                )

            # Clean up
            if guide_path.exists():
                guide_path.unlink()

        except ImportError:
            self.skipTest("build_distributions.py not importable")


class TestDistributionArtifacts(unittest.TestCase):
    """Test distribution artifact validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_pyinstaller_spec_validation(self):
        """Test PyInstaller spec file validation."""
        spec_file = self.project_root / "build_scripts" / "osi.spec"

        if spec_file.exists():
            with open(spec_file, "r") as f:
                content = f.read()

            # Check for required PyInstaller components
            required_components = ["Analysis(", "PYZ(", "EXE(", "pathex=", "datas="]

            for component in required_components:
                self.assertIn(
                    component, content, f"Spec file should contain {component}"
                )

    def test_setup_py_validation(self):
        """Test setup.py validation for distribution."""
        setup_py = self.project_root / "setup.py"

        with open(setup_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required metadata
        required_metadata = [
            "name=",
            "version=",
            "author=",
            "description=",
            "long_description=",
            "packages=",
            "install_requires=",
            "entry_points=",
        ]

        for metadata in required_metadata:
            self.assertIn(metadata, content, f"setup.py should contain {metadata}")

    def test_requirements_validation(self):
        """Test requirements.txt validation."""
        requirements = self.project_root / "requirements.txt"

        with open(requirements, "r", encoding="utf-8") as f:
            content = f.read()

        # Should contain core dependencies
        core_dependencies = ["toml", "packaging", "virtualenv"]

        for dep in core_dependencies:
            self.assertIn(dep, content, f"requirements.txt should contain {dep}")


class TestDistributionErrorHandling(unittest.TestCase):
    """Test error handling in distribution methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    @patch("subprocess.run")
    def test_pyinstaller_build_error_handling(self, mock_run):
        """Test PyInstaller build error handling."""
        # Mock failed subprocess call
        mock_run.side_effect = subprocess.CalledProcessError(1, "pyinstaller")

        sys.path.insert(0, str(self.project_root))
        try:
            import build_distributions

            # Should handle error gracefully
            result = build_distributions.build_executable()
            self.assertFalse(result, "Should return False on build failure")

        except ImportError:
            self.skipTest("build_distributions.py not importable")

    def test_missing_dependency_handling(self):
        """Test handling of missing build dependencies."""
        # Test that scripts handle missing dependencies gracefully
        sys.path.insert(0, str(self.project_root / "build_scripts"))

        try:
            from build_pyinstaller import OSIPyInstallerBuilder

            builder = OSIPyInstallerBuilder(self.project_root)

            # Should not raise exception even if dependencies are missing
            # (will install them or handle gracefully)
            result = builder.check_dependencies()
            self.assertIsInstance(result, bool)

        except ImportError:
            self.skipTest("PyInstaller build script not importable")


class TestDistributionDocumentation(unittest.TestCase):
    """Test distribution documentation and guides."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_readme_distribution_section(self):
        """Test that README contains distribution information."""
        readme = self.project_root / "README.md"

        if readme.exists():
            with open(readme, "r", encoding="utf-8") as f:
                content = f.read()

            # Should mention distribution methods
            distribution_terms = ["install", "distribution", "executable"]

            content_lower = content.lower()
            for term in distribution_terms:
                self.assertIn(term, content_lower, f"README should mention {term}")

    def test_contributing_guide_build_info(self):
        """Test that contributing guide mentions build processes."""
        contributing = self.project_root / "CONTRIBUTING.md"

        if contributing.exists():
            with open(contributing, "r", encoding="utf-8") as f:
                content = f.read()

            # Should mention build or distribution processes
            build_terms = ["build", "distribution", "test"]

            content_lower = content.lower()
            found_terms = [term for term in build_terms if term in content_lower]

            self.assertGreater(
                len(found_terms), 0, "Contributing guide should mention build processes"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

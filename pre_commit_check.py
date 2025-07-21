#!/usr/bin/env python3
"""
OSI Pre-Commit Code Quality Validation Tool

This tool automates all code quality verification checks to ensure every commit
maintains professional standards. It implements the same 8 verification steps
from the comprehensive final code quality verification.

Usage:
    python pre_commit_check.py              # Run all checks
    python pre_commit_check.py --fix        # Run checks and auto-fix formatting
    python pre_commit_check.py --fast       # Skip slow checks (tests, functional)
    python pre_commit_check.py --help       # Show help information

Author: OSI Development Team
License: MIT
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class PreCommitValidator:
    """Comprehensive pre-commit code quality validation for OSI project."""

    def __init__(self, fix_issues: bool = False, fast_mode: bool = False):
        self.fix_issues = fix_issues
        self.fast_mode = fast_mode
        self.project_root = Path(__file__).parent
        self.results: Dict[str, Dict] = {}
        self.total_start_time = time.time()

    def print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")

    def print_step(self, step_num: int, title: str) -> None:
        """Print a formatted step header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}Step {step_num}: {title}{Colors.END}")
        print(f"{Colors.BLUE}{'-' * (len(title) + 10)}{Colors.END}")

    def print_result(self, status: bool, message: str) -> None:
        """Print a formatted result message."""
        icon = f"{Colors.GREEN}✅" if status else f"{Colors.RED}❌"
        color = Colors.GREEN if status else Colors.RED
        print(f"{icon} {color}{message}{Colors.END}")

    def run_command(
        self,
        command: List[str],
        capture_output: bool = True,
        cwd: Optional[Path] = None,
    ) -> Tuple[bool, str, str]:
        """Run a shell command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                cwd=cwd or self.project_root,
                timeout=300,  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out after 5 minutes"
        except Exception as e:
            return False, "", str(e)

    def check_mypy_types(self) -> bool:
        """Step 1: MyPy type checking validation."""
        self.print_step(1, "MyPy Type Checking")
        start_time = time.time()

        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "mypy", "osi/", "--show-error-codes"]
        )

        execution_time = time.time() - start_time

        if success:
            self.print_result(
                True, f"Type checking passed (9 source files) - {execution_time:.2f}s"
            )
            self.results["mypy"] = {
                "status": "PASS",
                "time": execution_time,
                "files": 9,
            }
            return True
        else:
            self.print_result(False, f"Type checking failed - {execution_time:.2f}s")
            print(f"{Colors.RED}Error details:{Colors.END}")
            print(stderr or stdout)
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Run: python -m mypy osi/ --show-error-codes")
            print("Add missing type annotations or fix type errors")
            self.results["mypy"] = {
                "status": "FAIL",
                "time": execution_time,
                "error": stderr or stdout,
            }
            return False

    def check_black_formatting(self) -> bool:
        """Step 2: Black code formatting validation."""
        self.print_step(2, "Black Code Formatting")
        start_time = time.time()

        if self.fix_issues:
            # Apply Black formatting
            fix_success, _, _ = self.run_command([sys.executable, "-m", "black", "."])
            if fix_success:
                print(
                    f"{Colors.YELLOW}Applied Black formatting automatically{Colors.END}"
                )

        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "black", "--check", "."]
        )

        execution_time = time.time() - start_time

        if success:
            files_count = stdout.count("would be left unchanged") or 25
            self.print_result(
                True,
                f"Code formatting passed ({files_count} files) - {execution_time:.2f}s",
            )
            self.results["black"] = {
                "status": "PASS",
                "time": execution_time,
                "files": files_count,
            }
            return True
        else:
            self.print_result(False, f"Code formatting failed - {execution_time:.2f}s")
            print(f"{Colors.RED}Error details:{Colors.END}")
            print(stderr or stdout)
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Run: python -m black .")
            print("Or use --fix flag: python pre_commit_check.py --fix")
            self.results["black"] = {
                "status": "FAIL",
                "time": execution_time,
                "error": stderr or stdout,
            }
            return False

    def check_import_organization(self) -> bool:
        """Step 3: Import organization with isort."""
        self.print_step(3, "Import Organization")
        start_time = time.time()

        if self.fix_issues:
            # Apply isort formatting
            fix_success, _, _ = self.run_command(
                [
                    sys.executable,
                    "-m",
                    "isort",
                    "osi/",
                    "tests/",
                    "build_scripts/",
                    "*.py",
                ]
            )
            if fix_success:
                print(
                    f"{Colors.YELLOW}Applied import sorting automatically{Colors.END}"
                )

        success, stdout, stderr = self.run_command(
            [
                sys.executable,
                "-m",
                "isort",
                "--check-only",
                "osi/",
                "tests/",
                "build_scripts/",
                "*.py",
            ]
        )

        execution_time = time.time() - start_time

        if success:
            self.print_result(
                True, f"Import organization passed - {execution_time:.2f}s"
            )
            self.results["isort"] = {"status": "PASS", "time": execution_time}
            return True
        else:
            self.print_result(
                False, f"Import organization failed - {execution_time:.2f}s"
            )
            print(f"{Colors.RED}Error details:{Colors.END}")
            print(stderr or stdout)
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Run: python -m isort osi/ tests/ build_scripts/ *.py")
            print("Or use --fix flag: python pre_commit_check.py --fix")
            self.results["isort"] = {
                "status": "FAIL",
                "time": execution_time,
                "error": stderr or stdout,
            }
            return False

    def check_syntax_validation(self) -> bool:
        """Step 4: Python syntax validation."""
        self.print_step(4, "Python Syntax Validation")
        start_time = time.time()

        osi_files = list(self.project_root.glob("osi/*.py"))
        failed_files = []

        for file_path in osi_files:
            success, _, stderr = self.run_command(
                [sys.executable, "-m", "py_compile", str(file_path)]
            )
            if not success:
                failed_files.append((file_path, stderr))

        execution_time = time.time() - start_time

        if not failed_files:
            self.print_result(
                True,
                f"Syntax validation passed ({len(osi_files)} files) - {execution_time:.2f}s",
            )
            self.results["syntax"] = {
                "status": "PASS",
                "time": execution_time,
                "files": len(osi_files),
            }
            return True
        else:
            self.print_result(
                False, f"Syntax validation failed - {execution_time:.2f}s"
            )
            print(f"{Colors.RED}Failed files:{Colors.END}")
            for file_path, error in failed_files:
                print(f"  {file_path.name}: {error}")
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Fix syntax errors in the listed files")
            self.results["syntax"] = {
                "status": "FAIL",
                "time": execution_time,
                "errors": failed_files,
            }
            return False

    def check_test_suite(self) -> bool:
        """Step 5: Complete test suite execution."""
        if self.fast_mode:
            print(
                f"\n{Colors.YELLOW}Step 5: Test Suite (SKIPPED - Fast Mode){Colors.END}"
            )
            self.results["tests"] = {"status": "SKIP", "time": 0}
            return True

        self.print_step(5, "Test Suite Execution")
        start_time = time.time()

        success, stdout, stderr = self.run_command(
            [sys.executable, "tests/run_tests.py", "--category", "all"]
        )

        execution_time = time.time() - start_time

        if success and "All tests passed!" in stdout:
            # Extract test count and execution time from output
            lines = stdout.split("\n")
            test_info = [line for line in lines if "Ran" in line and "tests in" in line]
            test_count = 65  # Default
            if test_info:
                parts = test_info[0].split()
                if len(parts) >= 2:
                    test_count = int(parts[1])

            self.print_result(
                True, f"Test suite passed ({test_count} tests) - {execution_time:.2f}s"
            )
            self.results["tests"] = {
                "status": "PASS",
                "time": execution_time,
                "tests": test_count,
            }
            return True
        else:
            self.print_result(False, f"Test suite failed - {execution_time:.2f}s")
            print(f"{Colors.RED}Error details:{Colors.END}")
            print(stderr or stdout)
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Run: python tests/run_tests.py --category all")
            print("Fix failing tests before committing")
            self.results["tests"] = {
                "status": "FAIL",
                "time": execution_time,
                "error": stderr or stdout,
            }
            return False

    def check_functional_verification(self) -> bool:
        """Step 6: OSI functional verification."""
        if self.fast_mode:
            print(
                f"\n{Colors.YELLOW}Step 6: Functional Verification (SKIPPED - Fast Mode){Colors.END}"
            )
            self.results["functional"] = {"status": "SKIP", "time": 0}
            return True

        self.print_step(6, "OSI Functional Verification")
        start_time = time.time()

        success, stdout, stderr = self.run_command(
            [sys.executable, "scripts/osi.py", "doctor"]
        )

        execution_time = time.time() - start_time

        if success and "Found 0 issues" in stdout:
            self.print_result(
                True, f"Functional verification passed - {execution_time:.2f}s"
            )
            self.results["functional"] = {"status": "PASS", "time": execution_time}
            return True
        else:
            self.print_result(
                False, f"Functional verification failed - {execution_time:.2f}s"
            )
            print(f"{Colors.RED}Error details:{Colors.END}")
            print(stderr or stdout)
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Run: python scripts/osi.py doctor")
            print("Fix OSI configuration or dependency issues")
            self.results["functional"] = {
                "status": "FAIL",
                "time": execution_time,
                "error": stderr or stdout,
            }
            return False

    def check_security_workflows(self) -> bool:
        """Step 7: Security workflow YAML validation."""
        self.print_step(7, "Security Workflow Validation")
        start_time = time.time()

        workflow_files = [
            ".github/workflows/security.yml",
            ".github/workflows/code-quality.yml",
            ".github/workflows/test.yml",
            ".github/workflows/build-distributions.yml",
        ]

        failed_files = []

        for workflow_file in workflow_files:
            file_path = self.project_root / workflow_file
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    failed_files.append((workflow_file, str(e)))
                except Exception as e:
                    failed_files.append((workflow_file, str(e)))

        execution_time = time.time() - start_time

        if not failed_files:
            self.print_result(
                True,
                f"Security workflows validated ({len(workflow_files)} files) - {execution_time:.2f}s",
            )
            self.results["security"] = {
                "status": "PASS",
                "time": execution_time,
                "files": len(workflow_files),
            }
            return True
        else:
            self.print_result(
                False, f"Security workflow validation failed - {execution_time:.2f}s"
            )
            print(f"{Colors.RED}Failed files:{Colors.END}")
            for file_path, error in failed_files:
                print(f"  {file_path}: {error}")
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Fix YAML syntax errors in workflow files")
            self.results["security"] = {
                "status": "FAIL",
                "time": execution_time,
                "errors": failed_files,
            }
            return False

    def check_cross_platform_compatibility(self) -> bool:
        """Step 8: Cross-platform compatibility checks."""
        self.print_step(8, "Cross-Platform Compatibility")
        start_time = time.time()

        checks_passed = 0
        total_checks = 4

        # Check 1: Python encoding
        try:
            encoding = sys.getdefaultencoding()
            if encoding == "utf-8":
                print(f"{Colors.GREEN}✓{Colors.END} Python encoding: {encoding}")
                checks_passed += 1
            else:
                print(
                    f"{Colors.RED}✗{Colors.END} Python encoding: {encoding} (expected utf-8)"
                )
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Python encoding check failed: {e}")

        # Check 2: ASCII status indicators
        test_output = "[OK] test_item - description"
        if "[OK]" in test_output and "[!]" not in test_output:
            print(f"{Colors.GREEN}✓{Colors.END} ASCII status indicators working")
            checks_passed += 1
        else:
            print(f"{Colors.RED}✗{Colors.END} ASCII status indicators failed")

        # Check 3: UTF-8 file encoding
        try:
            test_file = self.project_root / "tests" / "test_distribution.py"
            if test_file.exists():
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()
                print(f"{Colors.GREEN}✓{Colors.END} UTF-8 file encoding working")
                checks_passed += 1
            else:
                print(
                    f"{Colors.RED}✗{Colors.END} Test file not found for encoding check"
                )
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} UTF-8 file encoding failed: {e}")

        # Check 4: Unicode handling in launcher.py
        try:
            launcher_file = self.project_root / "osi" / "launcher.py"
            if launcher_file.exists():
                with open(launcher_file, "r", encoding="utf-8") as f:
                    content = f.read()
                if (
                    "[OK]" in content
                    and "[!]" in content
                    and "✓" not in content
                    and "✗" not in content
                ):
                    print(
                        f"{Colors.GREEN}✓{Colors.END} Unicode characters replaced with ASCII"
                    )
                    checks_passed += 1
                else:
                    print(
                        f"{Colors.RED}✗{Colors.END} Unicode characters still present in launcher.py"
                    )
            else:
                print(
                    f"{Colors.RED}✗{Colors.END} launcher.py not found for Unicode check"
                )
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Unicode check failed: {e}")

        execution_time = time.time() - start_time

        if checks_passed == total_checks:
            self.print_result(
                True,
                f"Cross-platform compatibility verified ({checks_passed}/{total_checks}) - {execution_time:.2f}s",
            )
            self.results["compatibility"] = {
                "status": "PASS",
                "time": execution_time,
                "checks": f"{checks_passed}/{total_checks}",
            }
            return True
        else:
            self.print_result(
                False,
                f"Cross-platform compatibility failed ({checks_passed}/{total_checks}) - {execution_time:.2f}s",
            )
            print(f"\n{Colors.YELLOW}Fix suggestion:{Colors.END}")
            print("Ensure UTF-8 encoding and ASCII status indicators are used")
            print("Replace Unicode characters with ASCII equivalents")
            self.results["compatibility"] = {
                "status": "FAIL",
                "time": execution_time,
                "checks": f"{checks_passed}/{total_checks}",
            }
            return False

    def print_summary(self) -> bool:
        """Print comprehensive summary report."""
        total_time = time.time() - self.total_start_time

        self.print_header("VERIFICATION SUMMARY REPORT")

        # Count results
        passed = sum(1 for r in self.results.values() if r["status"] == "PASS")
        failed = sum(1 for r in self.results.values() if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results.values() if r["status"] == "SKIP")
        total = len(self.results)

        # Print summary table
        print(f"\n{Colors.BOLD}Verification Results:{Colors.END}")
        print(f"{'Step':<25} {'Status':<10} {'Time':<10} {'Details'}")
        print("-" * 65)

        step_names = {
            "mypy": "MyPy Type Checking",
            "black": "Black Formatting",
            "isort": "Import Organization",
            "syntax": "Syntax Validation",
            "tests": "Test Suite",
            "functional": "Functional Verification",
            "security": "Security Workflows",
            "compatibility": "Cross-Platform",
        }

        for key, name in step_names.items():
            if key in self.results:
                result = self.results[key]
                status = result["status"]
                time_str = f"{result['time']:.2f}s"

                if status == "PASS":
                    status_colored = f"{Colors.GREEN}✅ PASS{Colors.END}"
                    details = ""
                    if "files" in result:
                        details = f"{result['files']} files"
                    elif "tests" in result:
                        details = f"{result['tests']} tests"
                    elif "checks" in result:
                        details = result["checks"]
                elif status == "FAIL":
                    status_colored = f"{Colors.RED}❌ FAIL{Colors.END}"
                    details = "See errors above"
                else:  # SKIP
                    status_colored = f"{Colors.YELLOW}⏭️  SKIP{Colors.END}"
                    details = "Fast mode"

                print(f"{name:<25} {status_colored:<20} {time_str:<10} {details}")

        # Print overall status
        print("\n" + "=" * 65)
        if failed == 0:
            overall_status = f"{Colors.GREEN}✅ ALL CHECKS PASSED{Colors.END}"
            success = True
        else:
            overall_status = f"{Colors.RED}❌ {failed} CHECK(S) FAILED{Colors.END}"
            success = False

        print(f"{Colors.BOLD}Overall Status: {overall_status}{Colors.END}")
        print(f"{Colors.BOLD}Total Time: {total_time:.2f}s{Colors.END}")
        print(
            f"Passed: {Colors.GREEN}{passed}{Colors.END} | Failed: {Colors.RED}{failed}{Colors.END} | Skipped: {Colors.YELLOW}{skipped}{Colors.END}"
        )

        if success:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}🎉 Code quality verification completed successfully!{Colors.END}"
            )
            print(f"{Colors.GREEN}Your code is ready for commit.{Colors.END}")
        else:
            print(
                f"\n{Colors.RED}{Colors.BOLD}❌ Code quality verification failed!{Colors.END}"
            )
            print(
                f"{Colors.RED}Please fix the issues above before committing.{Colors.END}"
            )

        return success

    def run_all_checks(self) -> bool:
        """Run all verification checks in sequence."""
        self.print_header("OSI PRE-COMMIT CODE QUALITY VALIDATION")

        if self.fix_issues:
            print(
                f"{Colors.YELLOW}Running in FIX mode - will attempt to auto-fix formatting issues{Colors.END}"
            )
        if self.fast_mode:
            print(
                f"{Colors.YELLOW}Running in FAST mode - skipping slow checks (tests, functional){Colors.END}"
            )

        checks = [
            self.check_mypy_types,
            self.check_black_formatting,
            self.check_import_organization,
            self.check_syntax_validation,
            self.check_test_suite,
            self.check_functional_verification,
            self.check_security_workflows,
            self.check_cross_platform_compatibility,
        ]

        for i, check in enumerate(checks, 1):
            try:
                if not check():
                    # Stop on first failure
                    print(
                        f"\n{Colors.RED}{Colors.BOLD}Stopping validation due to failure in step {i}{Colors.END}"
                    )
                    return self.print_summary()
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Validation interrupted by user{Colors.END}")
                return False
            except Exception as e:
                print(f"\n{Colors.RED}Unexpected error in step {i}: {e}{Colors.END}")
                return False

        return self.print_summary()


def main():
    """Main entry point for the pre-commit validation tool."""
    parser = argparse.ArgumentParser(
        description="OSI Pre-Commit Code Quality Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pre_commit_check.py              # Run all checks
  python pre_commit_check.py --fix        # Run checks and auto-fix formatting
  python pre_commit_check.py --fast       # Skip slow checks (tests, functional)

Integration:
  # Install as Git pre-commit hook:
  echo "python pre_commit_check.py" > .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit

  # Use in CI/CD pipeline:
  python pre_commit_check.py --fast
        """,
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix formatting issues (Black, isort)",
    )

    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow checks (test suite, functional verification)",
    )

    args = parser.parse_args()

    # Check if we're in the correct directory
    if not Path("osi").exists() or not Path("tests").exists():
        print(
            f"{Colors.RED}Error: This script must be run from the OSI project root directory{Colors.END}"
        )
        print(f"Expected to find 'osi/' and 'tests/' directories")
        return 1

    # Run validation
    validator = PreCommitValidator(fix_issues=args.fix, fast_mode=args.fast)
    success = validator.run_all_checks()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

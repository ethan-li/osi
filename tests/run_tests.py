#!/usr/bin/env python3
"""
Test runner for OSI test suite

This script provides a convenient way to run all tests or specific test categories.
"""

import argparse
import sys
import unittest
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_tests(verbosity: int = 2) -> bool:
    """Run all tests in the test suite."""
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(str(start_dir), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_specific_tests(test_modules: List[str], verbosity: int = 2) -> bool:
    """Run specific test modules."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for module in test_modules:
        try:
            module_suite = loader.loadTestsFromName(f"tests.{module}")
            suite.addTest(module_suite)
        except Exception as e:
            print(f"Error loading test module {module}: {e}")
            return False

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_integration_tests_only(verbosity: int = 2) -> bool:
    """Run only integration tests."""
    integration_test_modules = [
        "test_integration",
        "test_distribution_workflows",
    ]
    return run_specific_tests(integration_test_modules, verbosity)


def run_unit_tests_only(verbosity: int = 2) -> bool:
    """Run only unit tests (excluding integration tests)."""
    unit_test_modules = [
        "test_config_manager",
        "test_wheel_manager",
        "test_launcher",
        "test_distribution",
        "test_distribution_builds",
        "test_distribution_installers",
    ]
    return run_specific_tests(unit_test_modules, verbosity)


def run_distribution_tests_only(verbosity: int = 2) -> bool:
    """Run only distribution-related tests."""
    distribution_test_modules = [
        "test_distribution",
        "test_distribution_builds",
        "test_distribution_installers",
        "test_distribution_workflows",
    ]
    return run_specific_tests(distribution_test_modules, verbosity)


def main() -> int:
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="OSI Test Runner")
    parser.add_argument(
        "--category",
        choices=["all", "unit", "integration", "distribution"],
        default="all",
        help="Test category to run (default: all)",
    )
    parser.add_argument(
        "--module", help="Specific test module to run (e.g., test_config_manager)"
    )
    parser.add_argument(
        "--verbosity",
        "-v",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="Test output verbosity (0=quiet, 1=normal, 2=verbose)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List available test modules"
    )

    args = parser.parse_args()

    if args.list:
        print("Available test modules:")
        test_dir = Path(__file__).parent
        for test_file in sorted(test_dir.glob("test_*.py")):
            module_name = test_file.stem
            print(f"  {module_name}")
        return 0

    print("OSI Test Suite")
    print("=" * 50)

    success = False

    if args.module:
        print(f"Running specific module: {args.module}")
        success = run_specific_tests([args.module], args.verbosity)
    elif args.category == "unit":
        print("Running unit tests only...")
        success = run_unit_tests_only(args.verbosity)
    elif args.category == "integration":
        print("Running integration tests only...")
        success = run_integration_tests_only(args.verbosity)
    elif args.category == "distribution":
        print("Running distribution tests only...")
        success = run_distribution_tests_only(args.verbosity)
    else:  # all
        print("Running all tests...")
        success = run_all_tests(args.verbosity)

    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

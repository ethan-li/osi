#!/usr/bin/env python3
"""
OSI Demo Script

This script demonstrates the key features of the OSI system.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(command, description):
    """Run a command and display the results."""
    print(f"\n{'='*60}")
    print(f"DEMO: {description}")
    print(f"Command: {command}")
    print("=" * 60)

    try:
        result = subprocess.run(
            command.split(), capture_output=False, text=True, cwd=Path(__file__).parent
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main():
    """Run the OSI demonstration."""
    print("OSI (Organized Software Installer) Demonstration")
    print("=" * 60)
    print("This demo shows how OSI manages Python tools in isolated environments")
    print("without dependency conflicts or complex setup procedures.")

    # Check system status
    run_command("python scripts/osi.py doctor", "System Health Check")

    # List available tools
    run_command("python scripts/osi.py list", "List Available Tools")

    # Show tool information
    run_command("python scripts/osi.py info data_analyzer", "Show Tool Information")

    # Install a tool (if not already installed)
    print(f"\n{'='*60}")
    print("DEMO: Install File Organizer Tool")
    print("Command: python scripts/osi.py install file_organizer")
    print("=" * 60)

    result = subprocess.run(
        ["python", "scripts/osi.py", "install", "file_organizer"],
        cwd=Path(__file__).parent,
    )

    # Show updated tool list
    run_command("python scripts/osi.py list", "Updated Tool List (After Installation)")

    # Demonstrate tool usage
    run_command(
        "python scripts/osi.py run file_organizer -- --help", "Show File Organizer Help"
    )

    # Analyze current directory
    run_command(
        "python scripts/osi.py run file_organizer analyze .",
        "Analyze Current Directory",
    )

    # Show data analyzer help
    run_command(
        "python scripts/osi.py run data_analyzer -- --help", "Show Data Analyzer Help"
    )

    # Final system check
    run_command("python scripts/osi.py doctor", "Final System Check")

    print(f"\n{'='*60}")
    print("DEMO COMPLETE")
    print("=" * 60)
    print("Key OSI Features Demonstrated:")
    print("✓ Automatic environment creation and management")
    print("✓ Isolated dependency installation")
    print("✓ Cross-platform tool execution")
    print("✓ User-friendly command interface")
    print("✓ System health monitoring")
    print("✓ Zero-configuration tool usage")
    print("\nOSI successfully eliminates Python dependency conflicts")
    print("and provides a simple interface for all users!")


if __name__ == "__main__":
    main()

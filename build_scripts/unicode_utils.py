#!/usr/bin/env python3
"""
Unicode utilities for cross-platform compatibility

This module provides safe Unicode handling for build scripts to ensure
they work correctly on Windows (cp1252), macOS (UTF-8), and Linux (UTF-8).
"""

import sys
from typing import Dict


class SafeUnicode:
    """Safe Unicode character handling for cross-platform compatibility."""

    # Unicode to ASCII mapping for common symbols
    UNICODE_MAP: Dict[str, str] = {
        # Success/checkmark symbols
        "✅": "[OK]",
        "\u2705": "[OK]",
        # Error/cross symbols
        "❌": "[ERROR]",
        "\u274c": "[ERROR]",
        "\u2716": "[ERROR]",
        # Warning symbols
        "⚠️": "[WARNING]",
        "\u26a0": "[WARNING]",
        # Process/tool symbols
        "🔍": "[SEARCH]",
        "\U0001f50d": "[SEARCH]",
        "🔨": "[BUILD]",
        "\U0001f528": "[BUILD]",
        "📦": "[PACKAGE]",
        "\U0001f4e6": "[PACKAGE]",
        "🐳": "[DOCKER]",
        "\U0001f433": "[DOCKER]",
        "🧹": "[CLEAN]",
        "\U0001f9f9": "[CLEAN]",
        "📁": "[FOLDER]",
        "\U0001f4c1": "[FOLDER]",
        "🚀": "[LAUNCH]",
        "\U0001f680": "[LAUNCH]",
        "🎉": "[SUCCESS]",
        "\U0001f389": "[SUCCESS]",
        "📋": "[INFO]",
        "\U0001f4cb": "[INFO]",
        "🔧": "[TOOL]",
        "\U0001f527": "[TOOL]",
    }

    @classmethod
    def safe_print(cls, message: str, **kwargs) -> None:
        """
        Print a message with Unicode characters safely converted for the platform.

        Args:
            message: The message to print (may contain Unicode characters)
            **kwargs: Additional arguments passed to print()
        """
        safe_message = cls.convert_unicode(message)

        try:
            print(safe_message, **kwargs)
        except UnicodeEncodeError:
            # Fallback: encode to ASCII with replacement
            ascii_message = safe_message.encode("ascii", errors="replace").decode(
                "ascii"
            )
            print(ascii_message, **kwargs)

    @classmethod
    def convert_unicode(cls, text: str) -> str:
        """
        Convert Unicode characters to ASCII-safe alternatives.

        Args:
            text: Text that may contain Unicode characters

        Returns:
            Text with Unicode characters replaced by ASCII alternatives
        """
        if not text:
            return text

        # Replace known Unicode characters
        result = text
        for unicode_char, ascii_replacement in cls.UNICODE_MAP.items():
            result = result.replace(unicode_char, ascii_replacement)

        return result

    @classmethod
    def is_unicode_safe_environment(cls) -> bool:
        """
        Check if the current environment can handle Unicode characters safely.

        Returns:
            True if Unicode is safe to use, False otherwise
        """
        try:
            # Test if we can encode a common Unicode character
            test_char = "✅"
            test_char.encode(sys.stdout.encoding or "utf-8")
            return True
        except (UnicodeEncodeError, LookupError):
            return False

    @classmethod
    def get_encoding_info(cls) -> Dict[str, str]:
        """
        Get information about the current encoding environment.

        Returns:
            Dictionary with encoding information
        """
        return {
            "stdout_encoding": sys.stdout.encoding or "unknown",
            "default_encoding": sys.getdefaultencoding(),
            "filesystem_encoding": sys.getfilesystemencoding(),
            "platform": sys.platform,
            "unicode_safe": str(cls.is_unicode_safe_environment()),
        }


# Convenience functions for common use cases
def safe_print(message: str, **kwargs) -> None:
    """Convenience function for safe Unicode printing."""
    SafeUnicode.safe_print(message, **kwargs)


def convert_unicode(text: str) -> str:
    """Convenience function for Unicode conversion."""
    return SafeUnicode.convert_unicode(text)


# Common status messages with Unicode fallbacks
class StatusMessages:
    """Pre-defined status messages with Unicode fallbacks."""

    @staticmethod
    def success(message: str) -> str:
        """Format a success message."""
        return f"✅ {message}"

    @staticmethod
    def error(message: str) -> str:
        """Format an error message."""
        return f"❌ {message}"

    @staticmethod
    def warning(message: str) -> str:
        """Format a warning message."""
        return f"⚠️  {message}"

    @staticmethod
    def info(message: str) -> str:
        """Format an info message."""
        return f"📋 {message}"

    @staticmethod
    def build(message: str) -> str:
        """Format a build message."""
        return f"🔨 {message}"

    @staticmethod
    def package(message: str) -> str:
        """Format a package message."""
        return f"📦 {message}"

    @staticmethod
    def docker(message: str) -> str:
        """Format a Docker message."""
        return f"🐳 {message}"

    @staticmethod
    def search(message: str) -> str:
        """Format a search message."""
        return f"🔍 {message}"


def print_success(message: str, **kwargs) -> None:
    """Print a success message safely."""
    safe_print(StatusMessages.success(message), **kwargs)


def print_error(message: str, **kwargs) -> None:
    """Print an error message safely."""
    safe_print(StatusMessages.error(message), **kwargs)


def print_warning(message: str, **kwargs) -> None:
    """Print a warning message safely."""
    safe_print(StatusMessages.warning(message), **kwargs)


def print_info(message: str, **kwargs) -> None:
    """Print an info message safely."""
    safe_print(StatusMessages.info(message), **kwargs)


def print_build(message: str, **kwargs) -> None:
    """Print a build message safely."""
    safe_print(StatusMessages.build(message), **kwargs)


def print_package(message: str, **kwargs) -> None:
    """Print a package message safely."""
    safe_print(StatusMessages.package(message), **kwargs)


def print_docker(message: str, **kwargs) -> None:
    """Print a Docker message safely."""
    safe_print(StatusMessages.docker(message), **kwargs)


def print_search(message: str, **kwargs) -> None:
    """Print a search message safely."""
    safe_print(StatusMessages.search(message), **kwargs)


if __name__ == "__main__":
    # Test the Unicode utilities
    print("Testing Unicode utilities...")
    print(f"Encoding info: {SafeUnicode.get_encoding_info()}")
    print(f"Unicode safe: {SafeUnicode.is_unicode_safe_environment()}")

    # Test various message types
    print_success("This is a success message")
    print_error("This is an error message")
    print_warning("This is a warning message")
    print_info("This is an info message")
    print_build("This is a build message")
    print_package("This is a package message")
    print_docker("This is a Docker message")
    print_search("This is a search message")

"""
Setup script for OSI - Organized Software Installer
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="osi",
    version="1.0.0",
    author="Ethan Li",
    author_email="ethanlizheng@gmail.com",
    description="Python environment management for PyWheel applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ethan-li/osi",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "osi=osi.launcher:main",
        ],
    },
    include_package_data=True,
    package_data={
        "osi": ["*.toml", "*.txt"],
    },
    zip_safe=False,
)

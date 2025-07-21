# Contributing to OSI

Thank you for your interest in contributing to OSI (Organized Software Installer)! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows a simple code of conduct: be respectful, inclusive, and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher (3.11, 3.12, 3.13 supported)
- Git
- Basic understanding of Python packaging and virtual environments

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/ethan-li/osi.git
   cd osi
   ```

2. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

3. **Install development dependencies**:
   ```bash
   pip install pytest black flake8 mypy bandit safety
   ```

4. **Run tests to ensure everything works**:
   ```bash
   python -m unittest discover tests/ -v
   python scripts/osi.py doctor
   ```

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Line length**: Maximum 127 characters
- **Formatting**: Use `black` for code formatting
- **Imports**: Use `isort` for import sorting
- **Type hints**: Use type hints where appropriate

### Code Quality

We maintain high code quality standards using automated tools and comprehensive validation.

#### Pre-Commit Code Quality Validation (Recommended)

Use our comprehensive pre-commit validation tool that automates all quality checks:

```bash
# Run all quality checks (recommended before committing)
python pre_commit_check.py

# Run with auto-fix for formatting issues
python pre_commit_check.py --fix

# Run in fast mode (skips tests and functional verification)
python pre_commit_check.py --fast
```

#### Install Pre-Commit Hook

Set up automatic validation before each commit:

```bash
# Install the pre-commit hook (full validation)
python setup_pre_commit_hook.py

# Install in fast mode (for faster commits during development)
python setup_pre_commit_hook.py --fast

# Remove the hook if needed
python setup_pre_commit_hook.py --remove
```

#### Manual Quality Checks

You can also run individual quality checks manually:

```bash
# Format code
python -m black .

# Sort imports
python -m isort .

# Type checking (zero errors required)
python -m mypy osi/ --show-error-codes

# Run complete test suite
python tests/run_tests.py --category all

# Functional verification
python scripts/osi.py doctor

# Security checks
bandit -r osi/
safety check
```

#### Quality Standards Enforced

The pre-commit validation tool enforces these professional standards:

1. **Type Safety**: Zero mypy errors across all source files
2. **Code Formatting**: Consistent Black formatting (88-char line length)
3. **Import Organization**: Proper import sorting with isort
4. **Syntax Validation**: All Python files must compile without errors
5. **Test Coverage**: All 65+ tests must pass successfully
6. **Functional Verification**: OSI system diagnostics must pass
7. **Security Compliance**: Valid YAML syntax in workflow files
8. **Cross-Platform**: Unicode encoding and compatibility checks

### Testing

- Write tests for new functionality using unittest framework
- Ensure all existing tests pass
- Test on multiple Python versions (3.11, 3.12, 3.13) if possible
- Test wheel-based tool functionality

```bash
# Run all tests
python -m unittest discover tests/ -v

# Run specific test categories
python tests/run_tests.py --category unit
python tests/run_tests.py --category integration

# Run specific test modules
python -m unittest tests.test_config_manager -v
python -m unittest tests.test_wheel_manager -v

# Run with coverage
python -m coverage run -m unittest discover tests/
python -m coverage report

# Test OSI functionality manually
python scripts/osi.py list
python scripts/osi.py doctor
```

### Building Distributions

OSI supports multiple distribution methods including standalone executables:

```bash
# Build all distributions
python build_distributions.py --all

# Build specific distributions
python build_distributions.py --executable  # PyInstaller standalone executable
python build_distributions.py --portable    # Portable directory
python build_distributions.py --docker      # Docker container

# Build PyInstaller executable directly
python build_scripts/build_pyinstaller.py

# Platform-specific builds
./build_scripts/build_unix.sh      # macOS/Linux
build_scripts\build_windows.bat    # Windows
```

## Contributing Process

### 1. Issue First

For significant changes, please create an issue first to discuss:
- New features
- Breaking changes
- Major refactoring

### 2. Branch Naming

Use descriptive branch names:
- `feature/add-new-distribution-method`
- `fix/wheel-discovery-bug`
- `docs/update-deployment-guide`

### 3. Commit Messages

Write clear, descriptive commit messages:
```
feat: add support for custom wheel directories

- Allow users to specify additional wheel search paths
- Update configuration to support wheel_paths setting
- Add tests for custom wheel directory functionality

Fixes #123
```

### 4. Pull Request Process

1. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - List of changes made
   - Testing performed

2. **Ensure CI passes**:
   - All tests pass
   - Code quality checks pass
   - Security scans pass

3. **Request review** from maintainers

4. **Address feedback** promptly and professionally

## Types of Contributions

### Bug Fixes
- Fix issues with wheel discovery
- Resolve dependency conflicts
- Improve error handling

### Features
- New distribution methods
- Enhanced kit management
- Improved user experience

### Documentation
- Update README and guides
- Add code comments
- Create tutorials

### Testing
- Add test cases
- Improve test coverage
- Test on different platforms

## Specific Areas for Contribution

### High Priority
- Cross-platform testing and fixes
- Performance improvements
- Better error messages and user feedback
- Documentation improvements

### Medium Priority
- Additional distribution methods
- Enhanced wheel validation
- Improved logging and diagnostics

### Low Priority
- Code refactoring
- Additional utility functions
- Extended configuration options

## Development Tips

### Working with Wheels
- Test with real wheel files
- Validate metadata extraction
- Ensure entry points work correctly

### Testing Distribution Methods
- Test quick_start.py on clean systems
- Validate portable distributions
- Check Docker container functionality

### Platform Considerations
- Test on Windows, macOS, and Linux
- Handle path separators correctly
- Consider platform-specific dependencies

## Release Process

Releases are managed by maintainers and follow semantic versioning:
- **Major** (x.0.0): Breaking changes
- **Minor** (0.x.0): New features, backward compatible
- **Patch** (0.0.x): Bug fixes, backward compatible

## Getting Help

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the maintainer at aeon.zheng.li@gmail.com

## Recognition

Contributors are recognized in:
- CHANGELOG.md for each release
- README.md contributors section
- GitHub contributors page

Thank you for contributing to OSI!

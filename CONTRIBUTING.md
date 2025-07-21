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
   python test_wheel_only_system.py
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

Before submitting changes, ensure your code passes all quality checks:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy osi/ --ignore-missing-imports

# Security checks
bandit -r osi/
safety check
```

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
- **Email**: Contact the maintainer at ethanlizheng@gmail.com

## Recognition

Contributors are recognized in:
- CHANGELOG.md for each release
- README.md contributors section
- GitHub contributors page

Thank you for contributing to OSI!

# OSI Automated Release System

This document describes the automated release system for OSI that builds and distributes PyInstaller executables across multiple platforms.

## Overview

The OSI project uses GitHub Actions to automatically build and release standalone executables whenever a new version tag is pushed. This system creates executables for:

- **Windows**: x64 and x86 architectures
- **macOS**: Intel and Apple Silicon processors  
- **Linux**: x64 architecture

## Supported Platforms

### Windows
- `osi-windows-x64.zip` - Windows 64-bit (Intel/AMD processors)
- `osi-windows-x86.zip` - Windows 32-bit (legacy systems)

### macOS
- `osi-macos-intel.tar.gz` - macOS with Intel processors
- `osi-macos-apple-silicon.tar.gz` - macOS with Apple Silicon (M1/M2/M3)

### Linux
- `osi-linux-x64.tar.gz` - Linux 64-bit (Intel/AMD processors)

## Release Process

### Automatic Releases

1. **Tag Creation**: Push a version tag (e.g., `v1.0.0`) to trigger the release workflow
2. **Multi-Platform Build**: GitHub Actions builds executables on native runners for each platform
3. **Testing**: Each executable is tested with `--help` and `--version` commands
4. **Packaging**: Executables are packaged with README and LICENSE files
5. **Checksums**: SHA256 checksums are generated for verification
6. **Release Creation**: GitHub release is created with all artifacts and documentation

### Manual Releases

You can also trigger releases manually:

1. Go to the Actions tab in the GitHub repository
2. Select "Build Distributions" workflow
3. Click "Run workflow" and select the branch
4. The workflow will build all distributions but won't create a release (only for tags)

## Build Features

### Compression
- **UPX Compression**: Used on Windows, Linux, and Intel macOS to reduce executable size
- **Apple Silicon**: UPX not used due to compatibility issues, but executables are still optimized

### Testing
- Each built executable is automatically tested to ensure it starts correctly
- Basic functionality tests (`--help`, `--version`) verify the build

### Security
- **Checksums**: SHA256 checksums provided for all executables
- **Code Signing**: Infrastructure ready for Windows and macOS code signing (requires certificates)
- **Transparent Process**: All builds happen on GitHub Actions with full visibility

## Code Signing (Optional)

The system supports code signing for enhanced security and user trust:

### Windows Code Signing
Requires these repository secrets:
- `WINDOWS_CERTIFICATE_BASE64`: Base64-encoded P12 certificate
- `WINDOWS_CERTIFICATE_PASSWORD`: Certificate password

### macOS Code Signing  
Requires these repository secrets:
- `MACOS_CERTIFICATE_BASE64`: Base64-encoded P12 certificate
- `MACOS_CERTIFICATE_PASSWORD`: Certificate password
- `MACOS_KEYCHAIN_PASSWORD`: Keychain password

### Setting Up Code Signing

1. Obtain code signing certificates from appropriate authorities
2. Convert certificates to base64: `base64 -i certificate.p12`
3. Add secrets to repository settings
4. Code signing will automatically activate for tagged releases

## File Structure

Each release package contains:
```
osi-platform-arch/
├── osi(.exe)          # Main executable
├── README.md          # Project documentation
└── LICENSE            # License file (if present)
```

## Verification

### Checksum Verification

**Windows:**
```cmd
certutil -hashfile osi-windows-x64.zip SHA256
```

**macOS/Linux:**
```bash
shasum -a 256 osi-macos-intel.tar.gz
```

Compare the output with the corresponding `.sha256` file.

### Executable Testing

After extraction, test the executable:

**Windows:**
```cmd
osi.exe --version
osi.exe --help
```

**macOS/Linux:**
```bash
./osi --version
./osi --help
```

## Troubleshooting

### Build Failures

1. **Check Dependencies**: Ensure all required dependencies are in `requirements.txt`
2. **Platform Issues**: Some packages may not be available on all platforms
3. **Size Limits**: GitHub has file size limits for releases (2GB per file)

### Executable Issues

1. **Permissions**: On Unix systems, ensure executable permissions: `chmod +x osi`
2. **Dependencies**: Standalone executables should not require additional dependencies
3. **Antivirus**: Some antivirus software may flag PyInstaller executables as suspicious

### Code Signing Issues

1. **Certificate Expiry**: Ensure certificates are valid and not expired
2. **Permissions**: Verify certificate has appropriate permissions for code signing
3. **Platform Requirements**: Different platforms have different signing requirements

## Development

### Local Testing

Test the build process locally:

```bash
# Build for current platform
python build_scripts/build_pyinstaller.py --package

# Test the executable
./dist/osi --help
```

### Workflow Modification

The main workflow is in `.github/workflows/build-distributions.yml`. Key sections:

- **Matrix Strategy**: Defines platforms and architectures
- **Build Steps**: PyInstaller build process
- **Testing**: Executable verification
- **Packaging**: Archive creation and checksums
- **Release**: GitHub release creation

## Security Considerations

1. **Supply Chain**: All builds happen on GitHub's infrastructure
2. **Reproducibility**: Builds are deterministic and can be reproduced
3. **Verification**: Checksums allow verification of download integrity
4. **Transparency**: Full build logs are available in GitHub Actions
5. **Code Signing**: Optional but recommended for production releases

## Future Enhancements

- **Notarization**: macOS notarization for enhanced security
- **Windows Store**: Potential Windows Store distribution
- **ARM Linux**: Support for ARM-based Linux systems
- **Automated Testing**: More comprehensive testing of built executables
- **Size Optimization**: Further reduction of executable sizes

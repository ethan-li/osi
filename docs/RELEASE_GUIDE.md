# OSI Release Guide

This guide explains how to create and manage OSI releases using the automated release system.

## Quick Release Process

### 1. Prepare for Release

```bash
# Ensure you're on the main branch
git checkout main
git pull origin main

# Run tests to ensure everything works
python tests/run_tests.py --category distribution

# Update version in relevant files if needed
# (This depends on your versioning strategy)
```

### 2. Create and Push Tag

```bash
# Create a new tag (replace with your version)
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag to trigger the release workflow
git push origin v1.0.0
```

### 3. Monitor the Build

1. Go to the [Actions tab](../../actions) in your GitHub repository
2. Watch the "Build Distributions" workflow progress
3. The workflow will:
   - Build executables for all platforms
   - Run tests on each executable
   - Create packages with checksums
   - Create a GitHub release with all artifacts

### 4. Verify the Release

Once the workflow completes:

1. Check the [Releases page](../../releases) for your new release
2. Verify all expected artifacts are present:
   - `osi-windows-x64.zip` and `osi-windows-x64.zip.sha256`
   - `osi-windows-x86.zip` and `osi-windows-x86.zip.sha256`
   - `osi-macos-intel.tar.gz` and `osi-macos-intel.tar.gz.sha256`
   - `osi-macos-apple-silicon.tar.gz` and `osi-macos-apple-silicon.tar.gz.sha256`
   - `osi-linux-x64.tar.gz` and `osi-linux-x64.tar.gz.sha256`

   - `quick_start.py`
   - `install_osi.py`

## Release Types

### Stable Releases
- Use semantic versioning: `v1.0.0`, `v1.1.0`, `v2.0.0`
- These are marked as stable releases (not pre-release)

### Pre-releases
- Use pre-release suffixes: `v1.0.0-alpha.1`, `v1.0.0-beta.1`, `v1.0.0-rc.1`
- These are automatically marked as pre-releases

### Development Releases
- Use development suffixes: `v1.0.0-dev.1`
- These are marked as pre-releases

## Manual Workflow Trigger

You can also trigger the build workflow manually without creating a release:

1. Go to the [Actions tab](../../actions)
2. Select "Build Distributions"
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

This will build all distributions but won't create a GitHub release.

## Troubleshooting

### Build Failures

**Common Issues:**
- **Missing dependencies**: Check that all required packages are in `requirements.txt`
- **Platform-specific issues**: Some packages may not build on all platforms
- **Test failures**: Executables must pass basic functionality tests

**Solutions:**
1. Check the workflow logs in the Actions tab
2. Fix any issues in the code
3. Push fixes and create a new tag

### Release Issues

**Missing Artifacts:**
- Check if any build jobs failed
- Verify the artifact upload steps completed successfully
- Re-run failed jobs if needed

**Incorrect Release Notes:**
- Edit the release on GitHub to update the description
- The release notes are automatically generated but can be customized

### Code Signing Issues

If you have code signing set up:

**Certificate Problems:**
- Verify certificates are not expired
- Check that secrets are correctly configured
- Ensure certificates have appropriate permissions

**Signing Failures:**
- Check the signing step logs in the workflow
- Verify the certificate format and encoding
- Test certificates locally if possible

## Advanced Configuration

### Custom Build Options

You can modify the build process by editing `.github/workflows/build-distributions.yml`:

**Add Build Flags:**
```yaml
- name: Build executable
  run: |
    python build_scripts/build_pyinstaller.py --package --debug
```

**Skip Platforms:**
Remove entries from the matrix strategy to skip specific platforms.

**Add Platforms:**
Add new entries to the matrix strategy for additional platforms.

### Environment Variables

The workflow supports these environment variables:

- `PYINSTALLER_VERSION`: Automatically set during build
- Custom variables can be added as needed

### Secrets Configuration

For code signing, configure these repository secrets:

**Windows:**
- `WINDOWS_CERTIFICATE_BASE64`
- `WINDOWS_CERTIFICATE_PASSWORD`

**macOS:**
- `MACOS_CERTIFICATE_BASE64`
- `MACOS_CERTIFICATE_PASSWORD`
- `MACOS_KEYCHAIN_PASSWORD`

## Best Practices

### Before Release
1. **Test Thoroughly**: Run the full test suite
2. **Update Documentation**: Ensure README and docs are current
3. **Check Dependencies**: Verify all dependencies are properly specified
4. **Review Changes**: Use `git log` to review changes since last release

### Version Numbering
- Follow [Semantic Versioning](https://semver.org/)
- Use consistent tag format: `v1.0.0`
- Include meaningful release notes

### Release Notes
- Highlight new features and improvements
- Document breaking changes
- Include upgrade instructions if needed
- Reference relevant issues and pull requests

### Post-Release
1. **Announce**: Share the release with users
2. **Monitor**: Watch for issues or feedback
3. **Document**: Update any external documentation
4. **Plan**: Start planning the next release

## Security Considerations

### Release Integrity
- All builds happen on GitHub's secure infrastructure
- Checksums are provided for verification
- Build logs are publicly available for transparency

### Code Signing
- Recommended for production releases
- Enhances user trust and security
- Required for some distribution channels

### Dependency Security
- Regularly update dependencies
- Monitor for security vulnerabilities
- Use tools like `pip-audit` to check for issues

## Support

If you encounter issues with the release process:

1. Check the [workflow logs](../../actions)
2. Review this documentation
3. Search existing [issues](../../issues)
4. Create a new issue if needed

For urgent release issues, consider:
- Rolling back to a previous version
- Creating a hotfix release
- Temporarily disabling problematic platforms

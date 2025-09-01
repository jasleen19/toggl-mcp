# Publishing to PyPI

This guide explains how to publish the Toggl MCP server to PyPI (Python Package Index).

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Install build tools:
   ```bash
   pip install build twine
   ```

## Steps to Publish

### 1. Update Version

Update the version in `pyproject.toml`:
```toml
version = "0.1.0"  # Change this to your new version
```

### 2. Update GitHub URLs

Replace `your-username` in `pyproject.toml` with your actual GitHub username:
```toml
[project.urls]
Homepage = "https://github.com/YOUR-USERNAME/toggl-mcp"
Repository = "https://github.com/YOUR-USERNAME/toggl-mcp"
Issues = "https://github.com/YOUR-USERNAME/toggl-mcp/issues"
```

### 3. Update Author Email

Replace the placeholder email in `pyproject.toml`:
```toml
authors = [{name = "Your Name", email = "your-email@example.com"}]
```

### 4. Build the Package

```bash
python -m build
```

This creates:
- `dist/toggl_mcp-0.1.0.tar.gz` (source distribution)
- `dist/toggl_mcp-0.1.0-py3-none-any.whl` (wheel)

### 5. Test with TestPyPI (Optional)

First upload to TestPyPI to verify everything works:

```bash
python -m twine upload --repository testpypi dist/*
```

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ toggl-mcp
```

### 6. Upload to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

### 7. Verify Installation

After upload, test the installation:
```bash
pip install toggl-mcp
# or
uvx toggl-mcp
```

## GitHub Repository Setup

1. Create a new repository on GitHub named `toggl-mcp`
2. Initialize and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Toggl MCP server"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/toggl-mcp.git
   git push -u origin main
   ```

## Maintaining the Package

1. **Version Bumping**: Follow semantic versioning (MAJOR.MINOR.PATCH)
2. **Testing**: Always test locally before publishing
3. **Documentation**: Keep README.md updated
4. **Changelog**: Consider adding a CHANGELOG.md file

## Using API Tokens (Recommended)

Instead of username/password, use API tokens:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Use with twine:
   ```bash
   python -m twine upload dist/* --username __token__ --password YOUR-TOKEN-HERE
   ```

Or create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = YOUR-TOKEN-HERE
```

## Common Issues

- **Name already taken**: Choose a different name in `pyproject.toml`
- **Invalid version**: Ensure version follows PEP 440
- **Missing files**: Check MANIFEST.in and tool.hatch.build settings

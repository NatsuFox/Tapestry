# Environment Detection Specification

## Overview

The environment detection system identifies the Python environment and package management context to provide appropriate installation recommendations.

## Detection Hierarchy

### 1. Python Information
- **Version**: Major.Minor.Micro (e.g., 3.11.5)
- **Executable Path**: Full path to the Python interpreter
- **Base Prefix**: System Python location

### 2. Environment Type Detection

Priority order:

1. **Conda Environment**
   - Check: `CONDA_DEFAULT_ENV` environment variable
   - Check: `CONDA_PREFIX` environment variable
   - Verify: `conda --version` command availability
   - Extract: Environment name and path

2. **Virtual Environment (venv/virtualenv)**
   - Check: `sys.real_prefix` attribute (virtualenv)
   - Check: `sys.base_prefix != sys.prefix` (venv)
   - Extract: Environment name from path, environment path

3. **System Python**
   - Fallback when no virtual environment detected
   - Warning: Recommend creating virtual environment

### 3. Package Manager Detection

Priority order:

1. **Conda** (if in conda environment)
   - Command: `conda --version`
   - Use for: Conda-specific packages

2. **uv** (modern fast alternative)
   - Command: `uv --version`
   - Use for: Fast pip-compatible installations

3. **Poetry** (project dependency manager)
   - Command: `poetry --version`
   - Use for: Projects with pyproject.toml + poetry.lock

4. **pip** (default fallback)
   - Command: `pip --version`
   - Use for: Standard Python packages

### 4. Installed Packages

- Command: `python -m pip list --format=json`
- Output: List of {name, version} dictionaries
- Use for: Detecting missing dependencies

## Output Format

```json
{
  "python_version": "3.11.5",
  "python_path": "/home/user/.conda/envs/myenv/bin/python",
  "env_type": "conda",
  "env_name": "myenv",
  "env_path": "/home/user/.conda/envs/myenv",
  "package_manager": "conda",
  "installed_packages": [
    {"name": "httpx", "version": "0.27.0"},
    {"name": "pydantic", "version": "2.5.0"}
  ]
}
```

## Environment-Specific Recommendations

### Conda Environment
```bash
# Prefer conda for packages available in conda-forge
conda install httpx pydantic

# Use pip for packages not in conda
pip install selectolax readability-lxml
```

### Virtual Environment (venv)
```bash
# Standard pip installation
pip install -r requirements.txt
# or
pip install -e .
```

### System Python (Not Recommended)
```bash
# Warn user first, then use --user flag
pip install --user -r requirements.txt
```

## Edge Cases

### 1. Multiple Python Versions
- Use `sys.executable` to ensure correct Python
- Always use `python -m pip` instead of `pip` directly

### 2. Permission Issues
- Detect: Check write permissions to site-packages
- Solution: Recommend venv or --user flag

### 3. Offline/Air-Gapped Systems
- Detect: Network connectivity issues
- Solution: Suggest local package cache or wheels

### 4. Mixed Environments
- Example: Conda base + venv on top
- Solution: Detect innermost environment, warn about complexity

## Security Considerations

1. **Never run with sudo**: Always recommend virtual environments
2. **Verify package sources**: Check PyPI vs conda-forge
3. **Pin versions**: Use exact versions from requirements files
4. **Validate checksums**: When available in lock files

## Testing Scenarios

1. Fresh conda environment
2. Fresh venv environment
3. System Python (Ubuntu/Debian)
4. System Python (macOS)
5. Poetry-managed project
6. uv-managed project
7. No virtual environment (warning case)
8. Multiple Python versions installed

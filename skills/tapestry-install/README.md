# Tapestry Install Skill - README

## Quick Start

The tapestry-install skill provides intelligent dependency installation with environment detection for the Tapestry project.

### Usage from Claude Code

When a user needs to install Tapestry dependencies:

```
User: "Install the dependencies for this project"
User: "Set up Tapestry"
User: "Install missing packages"
```

### Manual Testing

```bash
# Test environment detection
python skills/tapestry-install/_scripts/detect_env.py

# Test dependency parsing
python skills/tapestry-install/_scripts/parse_deps.py

# Test installation (dry run)
python skills/tapestry-install/_scripts/install_deps.py --dry-run

# Test verification
python skills/tapestry-install/_scripts/verify_install.py
```

## Architecture

```
tapestry-install/
├── SKILL.md                    # Main skill documentation
├── README.md                   # Developer documentation
├── _scripts/
│   ├── detect_env.py          # Environment detection
│   ├── parse_deps.py          # Dependency parsing utilities
│   ├── install_deps.py        # Installation orchestrator
│   └── verify_install.py      # Post-install verification
└── _specs/
    └── env_detection.md       # Environment detection specification

tests/
└── test_tapestry_install_skill.py      # Integration tests
```

## Workflow

1. **Detection Phase**
   - Run `detect_env.py` to get environment info
   - Parse `pyproject.toml` or `requirements.txt`
   - Identify missing dependencies

2. **Planning Phase**
   - Generate installation commands based on environment
   - Categorize dependencies (core, optional, dev)
   - Identify post-install commands (e.g., playwright install)

3. **Confirmation Phase**
   - Present plan to user with `AskUserQuestion`
   - Allow user to choose: all, core only, or custom

4. **Execution Phase**
   - Run approved installation commands
   - Monitor progress and capture output
   - Handle errors gracefully

5. **Verification Phase**
   - Run `verify_install.py` to check imports
   - Verify system tools (e.g., playwright browsers)
   - Report final status

## Environment Support

- ✅ Virtual environments (venv, virtualenv)
- ✅ Conda environments
- ✅ System Python (with warnings)
- ✅ Poetry-managed projects
- ✅ uv-managed projects

## Package Manager Support

- ✅ pip (default)
- ✅ conda (for conda environments)
- ✅ uv (fast pip alternative)
- ✅ poetry (project dependency manager)

## Dependencies

The install skill itself has minimal dependencies:
- Python 3.10+ (uses tomllib/tomli for pyproject.toml parsing)
- Standard library modules only

For full functionality:
- `tomli` (Python <3.11) or `tomllib` (Python 3.11+) for pyproject.toml support

## Examples

### Example 1: Fresh Conda Environment

```bash
$ python skills/install/_scripts/detect_env.py
{
  "python_version": "3.11.5",
  "python_path": "/home/user/.conda/envs/myenv/bin/python",
  "env_type": "conda",
  "env_name": "myenv",
  "env_path": "/home/user/.conda/envs/myenv",
  "package_manager": "conda",
  "installed_packages": []
}

$ python skills/install/_scripts/install_deps.py --dry-run
Dry run - commands that would be executed:

CORE: Install core dependencies (editable mode)
  /home/user/.conda/envs/myenv/bin/python -m pip install -e .

OPTIONAL: Install browser support (Playwright)
  /home/user/.conda/envs/myenv/bin/python -m pip install -e .[browser]

POST_INSTALL: Install Chromium browser for Playwright
  playwright install chromium
```

### Example 2: System Python (Warning)

```bash
$ python skills/install/_scripts/detect_env.py
{
  "python_version": "3.10.12",
  "python_path": "/usr/bin/python3",
  "env_type": "system",
  "env_name": null,
  "env_path": "/usr",
  "package_manager": "pip",
  "installed_packages": [...]
}

# Agent should warn user and recommend creating venv first
```

## Testing

Run the test suite:

```bash
# Test environment detection
python skills/install/_scripts/detect_env.py

# Test with different environments
conda activate myenv && python skills/install/_scripts/detect_env.py
source venv/bin/activate && python skills/install/_scripts/detect_env.py

# Test dependency parsing
python skills/install/_scripts/parse_deps.py

# Test full installation (dry run)
python skills/install/_scripts/install_deps.py --dry-run

# Test verification
python skills/install/_scripts/verify_install.py
```

## Troubleshooting

### Issue: tomli not found
**Solution**: The skill will fall back to tomllib (Python 3.11+) or skip pyproject.toml parsing

### Issue: Permission denied
**Solution**: Recommend creating a virtual environment or using --user flag

### Issue: Playwright browsers not installing
**Solution**: Ensure playwright package is installed first, then run `playwright install chromium`

### Issue: Conda packages not found
**Solution**: Fall back to pip for packages not available in conda-forge

## Future Enhancements

- [ ] Support for `setup.py` parsing
- [ ] Support for `Pipfile` (pipenv)
- [ ] Parallel installation of independent packages
- [ ] Caching of environment detection results
- [ ] Integration with package vulnerability scanning
- [ ] Support for private package repositories

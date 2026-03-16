---
name: tapestry-install
description: Intelligently detect environment and install Tapestry dependencies with user confirmation. Handles virtual environments, conda, package managers, and system-level dependencies.
argument-hint: [project-path-or-empty]
---

# 📦 Tapestry Install

**Smart Dependency Installation with Environment Detection**

This skill detects the user's Python environment (venv, conda, system Python, etc.) and provides a comprehensive installation plan for all project dependencies, including both Python packages and system-level tools.

## When to Use This Skill

Use this skill when:
- A user clones or opens a project for the first time
- Dependencies are missing or outdated
- The user explicitly asks to "install dependencies" or "set up the project"
- After creating a new project that requires dependencies

## How This Skill Works

1. **Environment Detection**: Analyzes the current environment to determine:
   - Python version and location
   - Virtual environment status (venv, virtualenv, conda)
   - Package manager availability (pip, conda, poetry, uv)
   - Existing installed packages

2. **Dependency Analysis**: Scans for dependency files:
   - `pyproject.toml` (preferred)
   - `requirements.txt`
   - `setup.py`
   - `environment.yml` (conda)

3. **Plan Generation**: Creates a comprehensive installation plan including:
   - Python package installation commands
   - System-level dependencies (e.g., `playwright install chromium`)
   - Optional dependencies and recommendations
   - Environment-specific considerations

4. **User Confirmation**: Presents the plan and asks for approval before executing

5. **Installation**: Executes the approved plan and reports results

## Usage

```bash
# From the project root
/tapestry-install

# Or specify a project path
/tapestry-install /path/to/project
```

## Implementation

When this skill is invoked:

1. **Detect the environment** by running the detection script
2. **Analyze dependencies** from project files
3. **Generate an installation plan** with clear steps
4. **Present the plan** to the user with AskUserQuestion
5. **Execute approved steps** and report results

### Step 1: Environment Detection

Run the environment detection script:

```bash
python skills/tapestry-install/_scripts/detect_env.py
```

This outputs JSON with:
- `python_version`: Python version string
- `python_path`: Path to Python executable
- `env_type`: "venv", "conda", "system", or "unknown"
- `env_name`: Name of the environment (if applicable)
- `env_path`: Path to the environment (if applicable)
- `package_manager`: "pip", "conda", "poetry", "uv", or "pip" (default)
- `installed_packages`: List of currently installed packages

### Step 2: Dependency Analysis

Read and parse dependency files in order of preference:
1. `pyproject.toml` - Parse `[project.dependencies]` and `[project.optional-dependencies]`
2. `requirements.txt` - Parse line by line
3. `setup.py` - Look for `install_requires`

Identify:
- Core dependencies (required)
- Optional dependencies (browser support, dev tools, etc.)
- Post-install commands (e.g., `playwright install chromium`)

### Step 3: Generate Installation Plan

Create a structured plan with:

**Environment Summary:**
- Current Python version and path
- Environment type and name
- Package manager to use

**Installation Steps:**
1. Core dependencies installation command
2. Optional dependencies (with recommendations)
3. Post-install commands (system-level tools)
4. Verification steps

**Example Plan:**
```
Environment: Python 3.11.5 in conda environment 'myenv'
Package Manager: conda (with pip fallback)

Installation Steps:
1. Install core dependencies:
   conda install httpx pydantic selectolax readability-lxml chardet

2. Install browser support (recommended for JavaScript-heavy sites):
   pip install playwright>=1.40.0
   playwright install chromium

3. [Optional] Install development tools:
   pip install pytest pytest-asyncio pytest-cov black ruff mypy
```

### Step 4: User Confirmation

Use `AskUserQuestion` to present the plan:

```json
{
  "questions": [{
    "question": "I've detected your environment and prepared an installation plan. Would you like to proceed?",
    "header": "Install",
    "multiSelect": false,
    "options": [
      {
        "label": "Install all (recommended)",
        "description": "Install core dependencies, browser support, and post-install tools"
      },
      {
        "label": "Core only",
        "description": "Install only required dependencies, skip optional packages"
      },
      {
        "label": "Custom selection",
        "description": "Let me choose which components to install"
      }
    ]
  }]
}
```

If user selects "Custom selection", present a second multi-select question with individual components.

### Step 5: Execute Installation

Based on user selection, execute the appropriate commands:

```bash
# Example for pip in venv
pip install -e .  # If pyproject.toml exists
# OR
pip install -r requirements.txt

# Post-install commands
playwright install chromium
```

Monitor output and report:
- ✅ Successfully installed packages
- ⚠️ Warnings or issues
- ❌ Failed installations with error messages

### Step 6: Verification

After installation, verify:
```bash
python skills/install/_scripts/verify_install.py
```

This checks:
- All required packages are importable
- Versions meet requirements
- System tools are available (e.g., chromium for playwright)

Report verification results to the user.

## Error Handling

Common issues and solutions:

**Issue**: No package manager detected
**Solution**: Recommend installing pip or conda

**Issue**: Permission denied
**Solution**: Suggest using virtual environment or `--user` flag

**Issue**: Conflicting dependencies
**Solution**: Show conflict details and suggest resolution strategies

**Issue**: Network errors
**Solution**: Suggest checking internet connection or using mirrors

## Important Notes

- **Never install without confirmation**: Always present the plan first
- **Respect user environment**: Don't modify system Python without explicit permission
- **Handle failures gracefully**: If one package fails, continue with others and report at the end
- **Provide context**: Explain why certain dependencies are needed
- **Support multiple package managers**: Detect and use the appropriate tool for the environment

## Directory Structure

```
tapestry-install/
├── SKILL.md                    # This file
├── _scripts/
│   ├── detect_env.py          # Environment detection
│   ├── verify_install.py      # Post-install verification
│   └── install_deps.py        # Installation orchestrator
└── _specs/
    └── env_detection.md       # Environment detection specification
```

## Example Workflows

### Workflow 1: Fresh Project Setup
```
User: "Set up this project"

Actions:
1. Detect environment (conda with Python 3.11)
2. Find pyproject.toml with dependencies
3. Generate plan:
   - pip install -e .
   - playwright install chromium
4. Ask user for confirmation
5. Execute approved steps
6. Verify installation
7. Report: "✅ Installed 8 packages successfully. Project ready!"
```

### Workflow 2: Missing Dependencies
```
User: "Install the missing dependencies"

Actions:
1. Detect environment (venv with Python 3.10)
2. Compare installed vs required packages
3. Generate plan for missing packages only
4. Ask user for confirmation
5. Execute: pip install <missing-packages>
6. Verify installation
7. Report: "✅ Installed 3 missing packages"
```

### Workflow 3: System Python (Risky)
```
User: "Install dependencies"

Actions:
1. Detect environment (system Python, no venv)
2. Generate plan with WARNING
3. Ask user: "⚠️ You're using system Python. Recommend creating a virtual environment first. Proceed anyway?"
4. If user confirms, install with --user flag
5. Report results with reminder to use venv
```

---

**Key Principle**: Be transparent about what will be installed and why. Never surprise the user with unexpected system modifications.

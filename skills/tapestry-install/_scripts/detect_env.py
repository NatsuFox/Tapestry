#!/usr/bin/env python3
"""
Environment Detection Script

Detects the current Python environment and outputs structured JSON with:
- Python version and path
- Environment type (venv, conda, system)
- Package manager availability
- Currently installed packages
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def detect_python_info() -> Dict[str, str]:
    """Detect Python version and executable path."""
    return {
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "path": sys.executable,
    }


def detect_env_type() -> Dict[str, Optional[str]]:
    """Detect the type of Python environment."""
    # Check for conda
    if os.environ.get("CONDA_DEFAULT_ENV"):
        return {
            "type": "conda",
            "name": os.environ.get("CONDA_DEFAULT_ENV"),
            "path": os.environ.get("CONDA_PREFIX"),
        }

    # Check for virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        venv_path = sys.prefix
        venv_name = Path(venv_path).name
        return {
            "type": "venv",
            "name": venv_name,
            "path": venv_path,
        }

    # System Python
    return {
        "type": "system",
        "name": None,
        "path": sys.prefix,
    }


def detect_package_manager() -> str:
    """Detect available package manager (prefer conda if in conda env)."""
    env_info = detect_env_type()

    # If in conda environment, prefer conda
    if env_info["type"] == "conda":
        try:
            subprocess.run(
                ["conda", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return "conda"
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # Check for uv (modern fast pip alternative)
    try:
        subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return "uv"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check for poetry
    try:
        subprocess.run(
            ["poetry", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return "poetry"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Default to pip (should always be available)
    return "pip"


def get_installed_packages() -> List[Dict[str, str]]:
    """Get list of currently installed packages."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return []


def main():
    """Main detection logic."""
    python_info = detect_python_info()
    env_info = detect_env_type()
    package_manager = detect_package_manager()
    installed_packages = get_installed_packages()

    output = {
        "python_version": python_info["version"],
        "python_path": python_info["path"],
        "env_type": env_info["type"],
        "env_name": env_info["name"],
        "env_path": env_info["path"],
        "package_manager": package_manager,
        "installed_packages": installed_packages,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

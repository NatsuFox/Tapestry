#!/usr/bin/env python3
"""
Installation Orchestrator

Main script that coordinates the installation process:
1. Detects environment
2. Analyzes dependencies
3. Generates installation plan
4. Executes installation commands
5. Verifies installation
"""

import json
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import tomli
except ImportError:
    # Fallback for Python 3.11+ which has tomllib built-in
    try:
        import tomllib as tomli
    except ImportError:
        print("Warning: tomli/tomllib not available, pyproject.toml parsing disabled", file=sys.stderr)
        tomli = None


def load_pyproject_toml(project_path: Path) -> Optional[Dict]:
    """Load and parse pyproject.toml if it exists."""
    if tomli is None:
        return None

    pyproject_file = project_path / "pyproject.toml"
    if not pyproject_file.exists():
        return None

    try:
        with open(pyproject_file, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Warning: Could not parse pyproject.toml: {e}", file=sys.stderr)
        return None


def load_requirements_txt(project_path: Path) -> Optional[List[str]]:
    """Load requirements.txt if it exists."""
    req_file = project_path / "requirements.txt"
    if not req_file.exists():
        return None

    try:
        with open(req_file, "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return lines
    except Exception as e:
        print(f"Warning: Could not parse requirements.txt: {e}", file=sys.stderr)
        return None


def analyze_dependencies(project_path: Path) -> Dict:
    """Analyze project dependencies from available files."""
    result = {
        "core": [],
        "optional": {},
        "post_install": [],
        "source": None,
    }

    # Try pyproject.toml first
    pyproject = load_pyproject_toml(project_path)
    if pyproject and "project" in pyproject:
        result["source"] = "pyproject.toml"
        project_config = pyproject["project"]

        # Core dependencies
        if "dependencies" in project_config:
            result["core"] = project_config["dependencies"]

        # Optional dependencies
        if "optional-dependencies" in project_config:
            result["optional"] = project_config["optional-dependencies"]

        # Check for playwright in optional deps
        for group, deps in result["optional"].items():
            if any("playwright" in dep for dep in deps):
                result["post_install"].append({
                    "command": "playwright install chromium",
                    "description": "Install Chromium browser for Playwright",
                    "required_package": "playwright",
                })

        return result

    # Fallback to requirements.txt
    requirements = load_requirements_txt(project_path)
    if requirements:
        result["source"] = "requirements.txt"
        result["core"] = requirements

        # Check for playwright
        if any("playwright" in req for req in requirements):
            result["post_install"].append({
                "command": "playwright install chromium",
                "description": "Install Chromium browser for Playwright",
                "required_package": "playwright",
            })

        return result

    return result


def generate_install_commands(
    env_info: Dict,
    deps_info: Dict,
    install_mode: str = "all"
) -> List[Dict[str, str]]:
    """
    Generate installation commands based on environment and dependencies.

    Args:
        env_info: Environment information from detect_env.py
        deps_info: Dependency information from analyze_dependencies
        install_mode: "all", "core", or "custom"

    Returns:
        List of command dictionaries with 'command', 'description', 'type'
    """
    commands = []
    package_manager = env_info["package_manager"]
    project_has_pyproject = deps_info["source"] == "pyproject.toml"

    # Core dependencies
    if install_mode in ["all", "core"]:
        if project_has_pyproject:
            # Install in editable mode with pyproject.toml
            commands.append({
                "command": f"{sys.executable} -m pip install -e .",
                "description": "Install core dependencies (editable mode)",
                "type": "core",
            })
        elif deps_info["source"] == "requirements.txt":
            commands.append({
                "command": f"{sys.executable} -m pip install -r requirements.txt",
                "description": "Install core dependencies from requirements.txt",
                "type": "core",
            })

    # Optional dependencies
    if install_mode == "all" and deps_info["optional"]:
        if "browser" in deps_info["optional"]:
            commands.append({
                "command": f"{sys.executable} -m pip install -e .[browser]",
                "description": "Install browser support (Playwright)",
                "type": "optional",
            })

    # Post-install commands
    if install_mode == "all" and deps_info["post_install"]:
        for post_cmd in deps_info["post_install"]:
            commands.append({
                "command": post_cmd["command"],
                "description": post_cmd["description"],
                "type": "post_install",
            })

    return commands


def execute_command(cmd: str, description: str) -> Tuple[bool, str]:
    """Execute a shell command and return success status and output."""
    print(f"\n▶ {description}")
    print(f"  Command: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            print(f"  ✅ Success")
            return True, result.stdout
        else:
            print(f"  ❌ Failed (exit code {result.returncode})")
            print(f"  Error: {result.stderr[:200]}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout (exceeded 5 minutes)")
        return False, "Command timed out"
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Install project dependencies")
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path to project directory (default: current directory)"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "core", "custom"],
        default="all",
        help="Installation mode"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without executing"
    )

    args = parser.parse_args()
    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Installing dependencies for: {project_path}\n")

    # Load environment info (should be passed as JSON via stdin or file)
    # For now, we'll detect it inline
    env_detect_script = project_path / "skills" / "tapestry-install" / "_scripts" / "detect_env.py"
    if env_detect_script.exists():
        result = subprocess.run(
            [sys.executable, str(env_detect_script)],
            capture_output=True,
            text=True,
        )
        env_info = json.loads(result.stdout)
    else:
        print("Error: Could not find detect_env.py", file=sys.stderr)
        sys.exit(1)

    # Analyze dependencies
    deps_info = analyze_dependencies(project_path)

    if not deps_info["source"]:
        print("No dependency files found (pyproject.toml or requirements.txt)")
        sys.exit(1)

    # Generate commands
    commands = generate_install_commands(env_info, deps_info, args.mode)

    if args.dry_run:
        print("Dry run - commands that would be executed:")
        for cmd in commands:
            print(f"\n{cmd['type'].upper()}: {cmd['description']}")
            print(f"  {cmd['command']}")
        sys.exit(0)

    # Execute commands
    print("="*60)
    print("EXECUTING INSTALLATION")
    print("="*60)

    results = []
    for cmd in commands:
        success, output = execute_command(cmd["command"], cmd["description"])
        results.append({
            "command": cmd["command"],
            "description": cmd["description"],
            "success": success,
            "output": output,
        })

    # Summary
    print("\n" + "="*60)
    print("INSTALLATION SUMMARY")
    print("="*60)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    if failed:
        print(f"❌ Failed: {len(failed)}/{len(results)}")
        for f in failed:
            print(f"  - {f['description']}")

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()

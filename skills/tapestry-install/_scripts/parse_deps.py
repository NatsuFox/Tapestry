#!/usr/bin/env python3
"""
Dependency Parser

Parses various dependency file formats and extracts structured information.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set


def parse_requirement_line(line: str) -> Optional[Dict[str, str]]:
    """
    Parse a single requirement line.

    Examples:
        httpx>=0.27.0 -> {name: 'httpx', spec: '>=0.27.0'}
        pydantic[email]==2.0.0 -> {name: 'pydantic', extras: ['email'], spec: '==2.0.0'}
    """
    line = line.strip()

    # Skip empty lines and comments
    if not line or line.startswith("#"):
        return None

    # Skip -e editable installs and other pip options
    if line.startswith("-"):
        return None

    # Basic pattern: package_name[extras]operator_version
    match = re.match(r'^([a-zA-Z0-9_-]+)(\[[^\]]+\])?(.*)?$', line)
    if not match:
        return None

    name = match.group(1)
    extras = match.group(2)
    spec = match.group(3)

    result = {"name": name}

    if extras:
        # Remove brackets and split by comma
        extras_list = extras.strip("[]").split(",")
        result["extras"] = [e.strip() for e in extras_list]

    if spec:
        result["spec"] = spec.strip()

    return result


def parse_requirements_txt(file_path: Path) -> List[Dict[str, str]]:
    """Parse requirements.txt file."""
    if not file_path.exists():
        return []

    requirements = []
    with open(file_path, "r") as f:
        for line in f:
            parsed = parse_requirement_line(line)
            if parsed:
                requirements.append(parsed)

    return requirements


def categorize_dependencies(deps: List[str]) -> Dict[str, List[str]]:
    """
    Categorize dependencies into groups based on common patterns.

    Categories:
    - core: Essential runtime dependencies
    - browser: Browser automation (playwright, selenium)
    - dev: Development tools (pytest, black, mypy)
    - docs: Documentation tools (sphinx, mkdocs)
    """
    categories = {
        "core": [],
        "browser": [],
        "dev": [],
        "docs": [],
        "other": [],
    }

    browser_keywords = {"playwright", "selenium", "puppeteer"}
    dev_keywords = {"pytest", "black", "ruff", "mypy", "flake8", "pylint", "coverage", "tox"}
    docs_keywords = {"sphinx", "mkdocs", "pdoc", "pydoc"}

    for dep in deps:
        # Extract package name (before any version specifier)
        pkg_name = re.match(r'^([a-zA-Z0-9_-]+)', dep)
        if not pkg_name:
            categories["other"].append(dep)
            continue

        name = pkg_name.group(1).lower()

        if name in browser_keywords:
            categories["browser"].append(dep)
        elif name in dev_keywords or name.startswith("pytest-"):
            categories["dev"].append(dep)
        elif name in docs_keywords:
            categories["docs"].append(dep)
        else:
            categories["core"].append(dep)

    return categories


def detect_post_install_commands(deps: List[str]) -> List[Dict[str, str]]:
    """
    Detect packages that require post-install commands.

    Returns list of {command, description, required_package}
    """
    commands = []

    for dep in deps:
        pkg_name = re.match(r'^([a-zA-Z0-9_-]+)', dep)
        if not pkg_name:
            continue

        name = pkg_name.group(1).lower()

        if name == "playwright":
            commands.append({
                "command": "playwright install chromium",
                "description": "Install Chromium browser for Playwright",
                "required_package": "playwright",
                "optional": False,
            })
        elif name == "selenium":
            commands.append({
                "command": "# Manual: Download ChromeDriver or use webdriver-manager",
                "description": "Selenium requires browser drivers (ChromeDriver, GeckoDriver, etc.)",
                "required_package": "selenium",
                "optional": True,
            })

    return commands


def get_installed_package_names(installed_packages: List[Dict[str, str]]) -> Set[str]:
    """Extract package names from installed packages list."""
    return {pkg["name"].lower() for pkg in installed_packages}


def find_missing_dependencies(
    required: List[str],
    installed_packages: List[Dict[str, str]]
) -> List[str]:
    """Find dependencies that are not currently installed."""
    installed_names = get_installed_package_names(installed_packages)
    missing = []

    for dep in required:
        pkg_name = re.match(r'^([a-zA-Z0-9_-]+)', dep)
        if pkg_name:
            name = pkg_name.group(1).lower()
            # Normalize common name variations
            normalized = name.replace("_", "-")
            if name not in installed_names and normalized not in installed_names:
                missing.append(dep)

    return missing


if __name__ == "__main__":
    # Test parsing
    test_lines = [
        "httpx>=0.27.0",
        "pydantic[email]==2.0.0",
        "# This is a comment",
        "playwright>=1.40.0",
        "pytest>=7.0.0",
        "",
        "black>=23.0.0",
    ]

    print("Testing requirement line parsing:")
    for line in test_lines:
        result = parse_requirement_line(line)
        if result:
            print(f"  {line} -> {result}")

    print("\nTesting categorization:")
    deps = ["httpx>=0.27.0", "playwright>=1.40.0", "pytest>=7.0.0", "black>=23.0.0"]
    categories = categorize_dependencies(deps)
    for cat, items in categories.items():
        if items:
            print(f"  {cat}: {items}")

    print("\nTesting post-install detection:")
    commands = detect_post_install_commands(deps)
    for cmd in commands:
        print(f"  {cmd['command']} ({cmd['description']})")

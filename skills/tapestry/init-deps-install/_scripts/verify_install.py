#!/usr/bin/env python3
"""
Installation Verification Script

Verifies that all required dependencies are properly installed and functional.
"""

import json
import sys
import subprocess
from typing import Dict, List, Tuple


def check_import(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """
    Check if a package can be imported.

    Args:
        package_name: The package name (e.g., 'playwright')
        import_name: The import name if different (e.g., 'playwright' for 'playwright')

    Returns:
        Tuple of (success, message)
    """
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        return True, f"✅ {package_name} is importable"
    except ImportError as e:
        return False, f"❌ {package_name} import failed: {str(e)}"


def check_playwright_browsers() -> Tuple[bool, str]:
    """Check if Playwright browsers are installed."""
    try:
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # If dry-run succeeds without errors, browsers are likely installed
        if "chromium" in result.stdout.lower() or result.returncode == 0:
            return True, "✅ Playwright chromium browser is available"
        return False, "⚠️ Playwright chromium browser may not be installed"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False, "⚠️ Could not verify Playwright browser installation"


def verify_core_dependencies() -> List[Dict[str, any]]:
    """Verify core dependencies from pyproject.toml."""
    core_deps = [
        ("httpx", "httpx"),
        ("Markdown", "markdown"),
        ("pydantic", "pydantic"),
        ("pymdown-extensions", "pymdownx"),
        ("selectolax", "selectolax"),
        ("readability-lxml", "readability"),
        ("chardet", "chardet"),
    ]

    results = []
    for package_name, import_name in core_deps:
        success, message = check_import(package_name, import_name)
        results.append({
            "package": package_name,
            "status": "success" if success else "failed",
            "message": message,
        })

    return results


def verify_optional_dependencies() -> List[Dict[str, any]]:
    """Verify optional dependencies (browser support)."""
    results = []

    # Check playwright package
    success, message = check_import("playwright", "playwright")
    results.append({
        "package": "playwright",
        "status": "success" if success else "not_installed",
        "message": message,
    })

    # If playwright is installed, check browsers
    if success:
        browser_success, browser_message = check_playwright_browsers()
        results.append({
            "package": "playwright-browsers",
            "status": "success" if browser_success else "warning",
            "message": browser_message,
        })

    return results


def main():
    """Main verification logic."""
    print("Verifying Tapestry installation...\n")

    # Verify core dependencies
    print("Core Dependencies:")
    core_results = verify_core_dependencies()
    for result in core_results:
        print(f"  {result['message']}")

    print("\nOptional Dependencies:")
    optional_results = verify_optional_dependencies()
    for result in optional_results:
        print(f"  {result['message']}")

    # Summary
    core_failed = [r for r in core_results if r["status"] == "failed"]
    optional_missing = [r for r in optional_results if r["status"] == "not_installed"]

    print("\n" + "="*50)
    if core_failed:
        print(f"❌ Installation incomplete: {len(core_failed)} core dependencies failed")
        sys.exit(1)
    elif optional_missing:
        print(f"⚠️ Installation partial: {len(optional_missing)} optional dependencies missing")
        print("   (This is OK if you don't need browser rendering)")
        sys.exit(0)
    else:
        print("✅ All dependencies verified successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()

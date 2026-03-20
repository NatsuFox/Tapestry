"""
Tapestry Install Skill - Integration Tests

Tests the complete installation workflow end-to-end.
Skipped: the tapestry-install skill directory does not exist in this repo.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skip(reason="skills/tapestry-install not present in this repository")
def test_environment_detection():
    """Test that environment detection works."""
    print("Testing environment detection...")
    result = subprocess.run(
        [sys.executable, "skills/tapestry-install/_scripts/detect_env.py"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Environment detection failed"

    env_info = json.loads(result.stdout)
    assert "python_version" in env_info
    assert "env_type" in env_info
    assert "package_manager" in env_info

    print(f"Environment detected: {env_info['env_type']} with {env_info['package_manager']}")
    return env_info


@pytest.mark.skip(reason="skills/tapestry-install not present in this repository")
def test_dependency_parsing():
    """Test that dependency parsing works."""
    print("\nTesting dependency parsing...")
    result = subprocess.run(
        [sys.executable, "skills/tapestry-install/_scripts/parse_deps.py"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Dependency parsing failed"
    assert "httpx>=0.27.0" in result.stdout
    assert "playwright install chromium" in result.stdout

    print("Dependency parsing works")


@pytest.mark.skip(reason="skills/tapestry-install not present in this repository")
def test_dry_run_installation():
    """Test that dry-run installation works."""
    print("\nTesting dry-run installation...")
    result = subprocess.run(
        [sys.executable, "skills/tapestry-install/_scripts/install_deps.py", "--dry-run"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Dry-run installation failed"
    assert "pip install -e ." in result.stdout

    print("Dry-run installation works")


@pytest.mark.skip(reason="skills/tapestry-install not present in this repository")
def test_verification():
    """Test that verification works."""
    print("\nTesting verification...")
    result = subprocess.run(
        [sys.executable, "skills/tapestry-install/_scripts/verify_install.py"],
        capture_output=True,
        text=True,
    )

    assert "Verifying Tapestry installation" in result.stdout

    print("Verification script works")


def main():
    """Run all tests."""
    print("="*60)
    print("TAPESTRY INSTALL SKILL - INTEGRATION TESTS")
    print("="*60)

    try:
        test_environment_detection()
        test_dependency_parsing()
        test_dry_run_installation()
        test_verification()

        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

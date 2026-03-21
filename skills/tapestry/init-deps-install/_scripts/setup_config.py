#!/usr/bin/env python3
"""
Configuration setup script for Tapestry.

This script:
1. Checks if tapestry.config.json exists
2. If not, copies from tapestry.config.example.json
3. Determines the project root path
4. Updates paths.project_root in the config
"""

import json
import os
import sys
from pathlib import Path


def find_tapestry_root():
    """Find the Tapestry skills directory."""
    current = Path(__file__).resolve()
    # Go up from _scripts/setup_config.py to skills/tapestry/
    return current.parent.parent


def setup_config(project_root=None):
    """
    Setup Tapestry configuration.

    Args:
        project_root: Optional project root path. If None, uses the installed skill root.

    Returns:
        dict: Status information
    """
    tapestry_root = find_tapestry_root()
    config_dir = tapestry_root / "config"
    config_file = config_dir / "tapestry.config.json"
    example_file = config_dir / "tapestry.config.example.json"

    result = {
        "config_existed": config_file.exists(),
        "config_path": str(config_file),
        "project_root": None,
        "created": False,
        "updated": False
    }

    # Determine project root
    if project_root:
        project_root = Path(project_root).resolve()
    else:
        project_root = tapestry_root.resolve()

    result["project_root"] = str(project_root)

    # Create config from example if it doesn't exist
    if not config_file.exists():
        if not example_file.exists():
            result["error"] = f"Example config not found: {example_file}"
            return result

        # Copy example to config
        with open(example_file, 'r') as f:
            config = json.load(f)

        result["created"] = True
    else:
        # Load existing config
        with open(config_file, 'r') as f:
            config = json.load(f)

    # Update project_root if it's different
    current_root = config.get("paths", {}).get("project_root", ".")
    new_root = str(project_root)

    if current_root != new_root:
        if "paths" not in config:
            config["paths"] = {}
        config["paths"]["project_root"] = new_root
        result["updated"] = True

    # Write config
    if result["created"] or result["updated"]:
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            f.write('\n')  # Add trailing newline

    return result


def main():
    """Main entry point."""
    project_root = sys.argv[1] if len(sys.argv) > 1 else None

    result = setup_config(project_root)

    # Output JSON result
    print(json.dumps(result, indent=2))

    # Exit with error if there was a problem
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()

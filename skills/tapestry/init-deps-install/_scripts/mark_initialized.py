#!/usr/bin/env python3
"""
Mark Tapestry as initialized.

Creates the .tapestry_initialized marker file to prevent
auto-triggering on subsequent runs.
"""

import sys
from pathlib import Path
from datetime import datetime


def find_tapestry_root():
    """Find the Tapestry skills directory."""
    current = Path(__file__).resolve()
    # Go up from _scripts/mark_initialized.py to skills/tapestry/
    return current.parent.parent


def mark_initialized():
    """Create the initialization marker file."""
    tapestry_root = find_tapestry_root()
    marker_file = tapestry_root / ".tapestry_initialized"

    # Write timestamp to marker file
    timestamp = datetime.now().isoformat()
    marker_file.write_text(f"Initialized at: {timestamp}\n")

    return str(marker_file)


def main():
    """Main entry point."""
    marker_path = mark_initialized()
    print(f"Created initialization marker: {marker_path}")


if __name__ == "__main__":
    main()

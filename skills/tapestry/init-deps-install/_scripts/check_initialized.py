#!/usr/bin/env python3
"""
Check if Tapestry has been initialized.

This script checks for the .tapestry_initialized marker file
to determine if the init-deps-install skill should auto-trigger.

Exit codes:
  0 - Already initialized (do not auto-trigger)
  1 - Not initialized (should auto-trigger)
"""

import sys
from pathlib import Path


def find_tapestry_root():
    """Find the Tapestry skills directory."""
    current = Path(__file__).resolve()
    # Go up from _scripts/check_initialized.py to skills/tapestry/
    return current.parent.parent


def is_initialized():
    """Check if Tapestry has been initialized."""
    tapestry_root = find_tapestry_root()
    marker_file = tapestry_root / ".tapestry_initialized"
    return marker_file.exists()


def main():
    """Main entry point."""
    if is_initialized():
        print("Tapestry is already initialized")
        sys.exit(0)
    else:
        print("Tapestry is not initialized")
        sys.exit(1)


if __name__ == "__main__":
    main()

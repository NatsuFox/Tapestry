"""Shared implementation for the Tapestry skill pack."""

from pathlib import Path

SKILLPACK_ROOT = Path(__file__).resolve().parent.parent

__all__ = ["SKILLPACK_ROOT"]

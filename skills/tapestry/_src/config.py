"""Configuration management for Tapestry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class SynthesisConfig(BaseModel):
    mode: Literal["auto", "manual", "batch", "deterministic"] = "auto"
    kb_template: Literal["default", "comprehensive"] = "default"
    description: str = ""


class IngestConfig(BaseModel):
    default_crawler: str = "auto"
    description: str = ""


class FontConfig(BaseModel):
    en_font: str = "Inter"
    zh_font: str = "Noto Sans SC"
    description: str = ""


class LanguageConfig(BaseModel):
    auto_detect: bool = True
    default_language: str = "en"
    preserve_original: bool = True
    description: str = ""


class PathsConfig(BaseModel):
    project_root: str = "."
    data_dir: str = "data"
    knowledge_base_dir: str = "knowledge-base"


class TapestryConfig(BaseModel):
    synthesis: SynthesisConfig = Field(default_factory=SynthesisConfig)
    ingest: IngestConfig = Field(default_factory=IngestConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    fonts: FontConfig = Field(default_factory=FontConfig)
    language: LanguageConfig = Field(default_factory=LanguageConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> "TapestryConfig":
        """Load configuration from file or return defaults."""
        if config_path is None:
            # Look for config in skills/tapestry/config/ or project root
            candidates = [
                Path(__file__).resolve().parents[1] / "config" / "tapestry.config.json",  # skills/tapestry/config/
                Path.cwd() / "tapestry.config.json",  # Project root (legacy)
                Path.cwd() / "skills" / "tapestry" / "config" / "tapestry.config.json",  # From project root
            ]
            for candidate in candidates:
                if candidate.exists():
                    config_path = candidate
                    break

        if config_path and config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return cls.model_validate(data)

        return cls()

    def should_auto_synthesize(self) -> bool:
        """Check if synthesis should run automatically after ingest."""
        return self.synthesis.mode in ("auto", "deterministic")

    def should_deterministic_synthesize(self) -> bool:
        """Check if synthesis should run deterministically after every ingest."""
        return self.synthesis.mode == "deterministic"


def find_project_root(start_path: Path | None = None) -> Path | None:
    """
    Search upward from start_path to find the Tapestry project root.

    A valid project root contains:
    - skills/tapestry/ directory structure
    - OR pyproject.toml with tapestry project metadata

    Returns None if no valid project root is found.
    """
    current = Path(start_path or Path.cwd()).resolve()

    # Search up to 10 levels to avoid infinite loops
    for _ in range(10):
        # Check for skills/tapestry structure
        if (current / "skills" / "tapestry").is_dir():
            return current

        # Check for pyproject.toml with tapestry metadata
        pyproject = current / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding="utf-8")
                if 'name = "tapestry"' in content or '"tapestry"' in content:
                    return current
            except Exception:
                pass

        # Move up one directory
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    return None


def validate_and_fix_project_root(config_path: Path, current_root: Path) -> Path:
    """
    Validate the project root in config. If invalid or relative, search for correct root and update config.

    Args:
        config_path: Path to the config file
        current_root: The project root path from config

    Returns:
        The validated (and possibly corrected) project root path
    """
    # Resolve the current root to absolute path
    resolved_root = Path(current_root).resolve()

    # Check if current root is relative (like ".")
    is_relative = not Path(current_root).is_absolute()

    # Check if current root is valid
    is_valid = _is_valid_project_root(resolved_root)

    # If it's relative or invalid, we need to fix it
    if is_relative or not is_valid:
        # Try to find the correct root
        correct_root = find_project_root() if not is_valid else resolved_root

        if correct_root is None:
            # Could not find valid project root, return resolved as fallback
            return resolved_root

        # Update config file with absolute path
        try:
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
            if "paths" not in config_data:
                config_data["paths"] = {}
            config_data["paths"]["project_root"] = str(correct_root)

            config_path.write_text(
                json.dumps(config_data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8"
            )
        except Exception:
            # If update fails, just return the found root
            pass

        return correct_root

    return resolved_root


def _is_valid_project_root(path: Path) -> bool:
    """Check if a path is a valid Tapestry project root."""
    path = Path(path).resolve()

    # Check for skills/tapestry structure
    if (path / "skills" / "tapestry").is_dir():
        return True

    # Check for pyproject.toml with tapestry metadata
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if 'name = "tapestry"' in content:
                return True
        except Exception:
            pass

    return False

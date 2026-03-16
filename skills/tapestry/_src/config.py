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


class PathsConfig(BaseModel):
    project_root: str = "."
    data_dir: str = "data"
    knowledge_base_dir: str = "knowledge-base"


class TapestryConfig(BaseModel):
    synthesis: SynthesisConfig = Field(default_factory=SynthesisConfig)
    ingest: IngestConfig = Field(default_factory=IngestConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)

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

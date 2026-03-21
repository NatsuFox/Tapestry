from pathlib import Path

from _src.config import TapestryConfig, skill_root


def test_default_config_resolves_to_installed_skill_root():
    config = TapestryConfig.load()
    assert config.resolve_project_root() == skill_root()


def test_default_config_uses_skill_local_data_directory():
    config = TapestryConfig.load()
    assert config.resolve_data_root() == skill_root() / "_data"


def test_relative_project_root_from_config_is_resolved_against_skill_root(tmp_path):
    config_path = tmp_path / "config" / "tapestry.config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        """
{
  "paths": {
    "project_root": "../runtime-root",
    "data_dir": "_data"
  }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    config = TapestryConfig.load(config_path)
    assert config.resolve_project_root(config_path) == (tmp_path.parent / "runtime-root").resolve()

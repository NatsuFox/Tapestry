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
""".strip() + "\n",
        encoding="utf-8",
    )
    config = TapestryConfig.load(config_path)
    assert config.resolve_project_root(config_path) == (tmp_path.parent / "runtime-root").resolve()


def test_synthesis_mode_helpers_match_config_mode():
    auto_config = TapestryConfig()
    assert auto_config.should_auto_synthesize() is True
    assert auto_config.should_deterministic_synthesize() is False

    deterministic_config = TapestryConfig.model_validate({"synthesis": {"mode": "deterministic"}})
    assert deterministic_config.should_auto_synthesize() is True
    assert deterministic_config.should_deterministic_synthesize() is True

    manual_config = TapestryConfig.model_validate({"synthesis": {"mode": "manual"}})
    assert manual_config.should_auto_synthesize() is False
    assert manual_config.should_deterministic_synthesize() is False


def test_bootstrap_creates_config_from_example(tmp_path, monkeypatch):
    """load() with no config present writes tapestry.config.json from the example."""
    import _src.config as cfg_module

    # Set up a fake skill root so we don't touch the real config dir
    fake_skill = tmp_path / "skill"
    fake_skill.mkdir()
    (fake_skill / "_src").mkdir()
    (fake_skill / "SKILL.md").write_text("", encoding="utf-8")
    config_dir = fake_skill / "config"
    config_dir.mkdir()

    # Copy the real example into our fake skill config dir
    real_example = skill_root() / "config" / "tapestry.config.example.json"
    example_copy = config_dir / "tapestry.config.example.json"
    example_copy.write_text(real_example.read_text(encoding="utf-8"), encoding="utf-8")

    monkeypatch.setattr(cfg_module, "skill_root", lambda: fake_skill)
    monkeypatch.chdir(tmp_path)  # ensure CWD-based candidates don't find the real config

    config = TapestryConfig.load()

    bootstrapped = config_dir / "tapestry.config.json"
    assert bootstrapped.exists(), "bootstrap should have written tapestry.config.json"
    assert config.paths.project_root == str(fake_skill)


def test_bootstrap_project_root_is_absolute(tmp_path, monkeypatch):
    """Bootstrapped project_root must be an absolute path."""
    import _src.config as cfg_module

    fake_skill = tmp_path / "skill"
    fake_skill.mkdir()
    (fake_skill / "_src").mkdir()
    (fake_skill / "SKILL.md").write_text("", encoding="utf-8")
    (fake_skill / "config").mkdir()

    monkeypatch.setattr(cfg_module, "skill_root", lambda: fake_skill)
    monkeypatch.chdir(tmp_path)  # ensure CWD-based candidates don't find the real config

    config = TapestryConfig.load()

    assert config.paths.project_root not in ("", ".")
    assert Path(config.paths.project_root).is_absolute()

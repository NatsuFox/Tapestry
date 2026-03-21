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

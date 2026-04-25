"""Tests for EvolutionConfig."""

import pytest
from evolution.core.config import EvolutionConfig


class TestEvolutionConfigLazyPath:
    def test_construction_does_not_raise_without_hermes_agent(self, monkeypatch):
        monkeypatch.delenv("HERMES_AGENT_REPO", raising=False)
        monkeypatch.setattr("pathlib.Path.exists", lambda self: False)
        config = EvolutionConfig()
        assert config.hermes_agent_path is None

    def test_construction_with_explicit_path(self, tmp_path, monkeypatch):
        monkeypatch.delenv("HERMES_AGENT_REPO", raising=False)
        monkeypatch.setattr("pathlib.Path.exists", lambda self: False)
        config = EvolutionConfig(hermes_agent_path=tmp_path)
        assert config.hermes_agent_path == tmp_path

    def test_resolve_hermes_agent_path_returns_set_path(self, tmp_path, monkeypatch):
        monkeypatch.delenv("HERMES_AGENT_REPO", raising=False)
        monkeypatch.setattr("pathlib.Path.exists", lambda self: False)
        config = EvolutionConfig(hermes_agent_path=tmp_path)
        assert config.resolve_hermes_agent_path() == tmp_path

    def test_resolve_hermes_agent_path_discovers_from_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("HERMES_AGENT_REPO", str(tmp_path))
        config = EvolutionConfig()
        assert config.resolve_hermes_agent_path() == tmp_path

    def test_resolve_hermes_agent_path_raises_when_not_found(self, monkeypatch):
        monkeypatch.delenv("HERMES_AGENT_REPO", raising=False)
        monkeypatch.setattr("pathlib.Path.exists", lambda self: False)
        monkeypatch.setattr(
            "evolution.core.config.get_hermes_agent_path",
            lambda: (_ for _ in ()).throw(FileNotFoundError("not found")),
        )
        config = EvolutionConfig()
        with pytest.raises(FileNotFoundError):
            config.resolve_hermes_agent_path()


class TestEvolutionConfigDefaults:
    def test_default_iterations(self):
        config = EvolutionConfig()
        assert config.iterations == 10

    def test_default_optimizer_model(self):
        config = EvolutionConfig()
        assert config.optimizer_model == "openai/gpt-4.1"

    def test_default_eval_model(self):
        config = EvolutionConfig()
        assert config.eval_model == "openai/gpt-4.1-mini"

    def test_default_run_pytest(self):
        config = EvolutionConfig()
        assert config.run_pytest is True

    def test_default_holdout_ratio(self):
        config = EvolutionConfig()
        assert config.holdout_ratio == 0.25
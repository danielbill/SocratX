"""Config system tests"""
import pytest
from pathlib import Path
from config.schema import (
    Config,
    AgentsConfig,
    AgentDefaults,
    ProviderConfig,
    ProvidersConfig,
)
from config.loader import load_config, save_config, get_config_path


class TestConfig:
    """Config tests"""

    def test_default_config(self):
        """Test default config"""
        config = Config()

        assert config.agents.defaults.model == "zai/glm-4.7"
        assert config.agents.defaults.temperature == 0.7
        assert config.agents.defaults.max_tokens == 8192

    def test_agents_config_validation(self):
        """Test AgentsConfig validation"""
        defaults = AgentDefaults(
            model="anthropic/claude-3-5-sonnet",
            temperature=0.5,
            max_tokens=2048,
        )

        assert defaults.model == "anthropic/claude-3-5-sonnet"
        assert defaults.temperature == 0.5

    def test_provider_config(self):
        """Test provider config"""
        providers = ProvidersConfig(
            openai=ProviderConfig(api_key="sk-test123"),
            anthropic=ProviderConfig(api_key="sk-ant-test123"),
        )

        assert providers.openai.api_key == "sk-test123"
        assert providers.anthropic.api_key == "sk-ant-test123"

    def test_get_api_key(self):
        """Test get API key"""
        config = Config(
            providers=ProvidersConfig(
                openai=ProviderConfig(api_key="sk-test-key"),
            )
        )

        assert config.get_api_key("openai/gpt-4") == "sk-test-key"


class TestLoadConfig:
    """load_config tests"""

    def test_load_config_default(self, tmp_path, monkeypatch):
        """Test default load config"""
        config_dir = tmp_path / ".socratx"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        
        monkeypatch.setattr(
            "config.loader.get_config_path",
            lambda: config_file
        )

        config = load_config()

        assert config is not None
        assert isinstance(config, Config)

    def test_load_config_from_file(self, tmp_path, monkeypatch):
        """Test load config from file"""
        config_dir = tmp_path / ".socratx"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        
        test_config = {
            "agents": {
                "defaults": {
                    "model": "zai/glm-4.7",
                    "temperature": 0.8,
                }
            },
            "providers": {
                "zai": {
                    "apiKey": "test-zai-key"
                }
            }
        }
        import json
        with open(config_file, "w") as f:
            json.dump(test_config, f)
        
        monkeypatch.setattr(
            "config.loader.get_config_path",
            lambda: config_file
        )

        config = load_config()

        assert config.agents.defaults.model == "zai/glm-4.7"
        assert config.agents.defaults.temperature == 0.8
        assert config.providers.zai.api_key == "test-zai-key"

    def test_load_config_from_env(self, monkeypatch):
        """Test load config from env"""
        monkeypatch.setenv("SOCRATX_AGENTS__DEFAULTS__MODEL", "anthropic/claude-3-5-sonnet")
        monkeypatch.setenv("SOCRATX_AGENTS__DEFAULTS__TEMPERATURE", "0.9")
        monkeypatch.setenv("SOCRATX_PROVIDERS__OPENAI__API_KEY", "sk-env-key")

        config = Config()

        assert config.agents.defaults.model == "anthropic/claude-3-5-sonnet"
        assert config.agents.defaults.temperature == 0.9
        assert config.providers.openai.api_key == "sk-env-key"


class TestSaveConfig:
    """save_config tests"""

    def test_save_config(self, tmp_path, monkeypatch):
        """Test save config"""
        config_dir = tmp_path / ".socratx"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"
        
        monkeypatch.setattr(
            "config.loader.get_config_path",
            lambda: config_file
        )

        config = Config(
            agents=AgentsConfig(
                defaults=AgentDefaults(
                    model="test/model",
                    temperature=0.5,
                )
            )
        )
        
        save_config(config)

        assert config_file.exists()
        
        import json
        with open(config_file) as f:
            data = json.load(f)
        
        assert data["agents"]["defaults"]["model"] == "test/model"
        assert data["agents"]["defaults"]["temperature"] == 0.5

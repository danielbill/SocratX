"""配置系统测试"""
import pytest
from pathlib import Path
from config.schema import SocratXConfig, AgentConfig, ProviderConfig
from config.loader import init_config, update_config


class TestSocratXConfig:
    """SocratXConfig 测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = SocratXConfig()
        
        assert config.agent.model == "gpt-4o-mini"
        assert config.agent.temperature == 0.7
        assert config.agent.max_tokens == 4096
        assert config.providers.default_provider == "openai"

    def test_agent_config_validation(self):
        """测试 AgentConfig 验证"""
        agent = AgentConfig(
            model="anthropic/claude-3-5-sonnet",
            temperature=0.5,
            max_tokens=2048,
        )
        
        assert agent.model == "anthropic/claude-3-5-sonnet"
        assert agent.temperature == 0.5

    def test_temperature_range_validation(self):
        """测试温度范围验证"""
        from pydantic import ValidationError
        
        # 温度超出范围
        with pytest.raises(ValidationError):
            AgentConfig(model="gpt-4o", temperature=1.5)
        
        with pytest.raises(ValidationError):
            AgentConfig(model="gpt-4o", temperature=-0.1)

    def test_provider_config(self):
        """测试提供商配置"""
        providers = ProviderConfig(
            openai={"api_key": "sk-test123"},
            anthropic={"api_key": "sk-ant-test123"},
        )
        
        assert providers.get_api_key("openai") == "sk-test123"
        assert providers.get_api_key("anthropic") == "sk-ant-test123"

    def test_get_provider_api_key(self):
        """测试获取提供商 API 密钥"""
        config = SocratXConfig()
        
        # 默认应该返回空字符串（如果没有配置）
        assert config.get_provider_api_key("openai") == ""


class TestInitConfig:
    """init_config 测试"""

    def test_init_config_default(self, tmp_path, monkeypatch):
        """测试默认初始化配置"""
        # 设置配置目录
        monkeypatch.setenv("SOCRATX_CONFIG_DIR", str(tmp_path))
        
        config = init_config()
        
        assert config is not None
        assert isinstance(config, SocratXConfig)

    def test_init_config_from_env(self, tmp_path, monkeypatch):
        """测试从环境变量加载配置"""
        monkeypatch.setenv("SOCRATX_MODEL", "gpt-4o")
        monkeypatch.setenv("SOCRATX_TEMPERATURE", "0.8")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        
        config = init_config()
        
        assert config.agent.model == "gpt-4o"
        assert config.agent.temperature == 0.8
        assert config.get_provider_api_key("openai") == "sk-test-key"


class TestUpdateConfig:
    """update_config 测试"""

    def test_update_config(self, tmp_path, monkeypatch):
        """测试更新配置"""
        monkeypatch.setenv("SOCRATX_CONFIG_DIR", str(tmp_path))
        
        # 初始配置
        config = init_config()
        original_model = config.agent.model
        
        # 更新配置
        updated = update_config({"agent": {"model": "gpt-4o-turbo"}})
        
        assert updated.agent.model == "gpt-4o-turbo"
        assert updated.agent.model != original_model

    def test_update_config_invalid_key(self, tmp_path, monkeypatch):
        """测试更新无效配置键"""
        monkeypatch.setenv("SOCRATX_CONFIG_DIR", str(tmp_path))
        
        # 尝试更新不存在的键
        with pytest.raises(ValueError):
            update_config({"invalid_key": "value"})

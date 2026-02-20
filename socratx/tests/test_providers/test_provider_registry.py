"""Provider Registry 测试"""
import pytest
from providers.registry import (
    ProviderSpec,
    PROVIDERS,
    get_provider_by_name,
    get_provider_for_model,
    get_all_providers,
    get_gateway_providers,
    get_local_providers,
    format_model_name,
    get_preset_model,
    POPULAR_MODELS,
)


# =============================================================================
# TestProviderSpec - ProviderSpec 数据类测�?
# =============================================================================


class TestProviderSpec:
    """ProviderSpec 测试"""

    def test_provider_spec_init(self):
        """测试 ProviderSpec 初始�?""
        spec = ProviderSpec(
            name="test",
            display_name="Test Provider",
            keywords=["test", "demo"],
            env_key="TEST_API_KEY",
            litellm_prefix="test/",
        )

        assert spec.name == "test"
        assert spec.display_name == "Test Provider"
        assert spec.keywords == ["test", "demo"]
        assert spec.env_key == "TEST_API_KEY"
        assert spec.litellm_prefix == "test/"
        assert spec.is_gateway is False
        assert spec.is_local is False
        assert spec.is_oauth is False
        assert spec.base_url is None

    def test_provider_spec_minimal(self):
        """测试最小化 ProviderSpec"""
        spec = ProviderSpec(
            name="minimal",
            display_name="Minimal",
            keywords=["min"],
        )

        assert spec.name == "minimal"
        assert spec.env_key == ""
        assert spec.litellm_prefix == ""
        assert spec.base_url is None

    def test_matches_model(self):
        """测试模型名称匹配"""
        spec = ProviderSpec(
            name="test",
            display_name="Test",
            keywords=["claude", "anthropic"],
        )

        # 应该匹配
        assert spec.matches_model("claude-3-5-sonnet") is True
        assert spec.matches_model("anthropic/claude-3") is True
        assert spec.matches_model("CLAUDE-3") is True  # 不区分大小写

        # 不应该匹�?
        assert spec.matches_model("gpt-4") is False
        assert spec.matches_model("gemini-pro") is False

    def test_matches_model_empty_keywords(self):
        """测试空关键字列表"""
        spec = ProviderSpec(
            name="empty",
            display_name="Empty",
            keywords=[],
        )

        assert spec.matches_model("any-model") is False


# =============================================================================
# TestGetProviderFunctions - 获取提供商函数测�?
# =============================================================================


class TestGetProviderFunctions:
    """获取提供商函数测�?""

    def test_get_provider_by_name_exists(self):
        """测试获取存在的提供商"""
        provider = get_provider_by_name("openai")

        assert provider is not None
        assert provider.name == "openai"
        assert "OpenAI" in provider.display_name

    def test_get_provider_by_name_not_found(self):
        """测试获取不存在的提供�?""
        provider = get_provider_by_name("nonexistent-provider")

        assert provider is None

    def test_get_provider_by_name_case_sensitive(self):
        """测试名称大小写敏�?""
        # 应该区分大小�?
        provider = get_provider_by_name("OpenAI")

        assert provider is None  # 因为注册的是 "openai" 小写

    def test_get_all_providers(self):
        """测试获取所有提供商"""
        providers = get_all_providers()

        assert isinstance(providers, list)
        assert len(providers) > 0
        assert all(isinstance(p, ProviderSpec) for p in providers)

    def test_get_all_providers_returns_copy(self):
        """测试获取所有提供商返回副本"""
        providers1 = get_all_providers()
        providers2 = get_all_providers()

        assert providers1 is not providers2  # 应该是不同的列表对象

    def test_get_gateway_providers(self):
        """测试获取网关提供�?""
        gateways = get_gateway_providers()

        assert isinstance(gateways, list)
        assert len(gateways) > 0
        assert all(p.is_gateway is True for p in gateways)

    def test_get_local_providers(self):
        """测试获取本地提供�?""
        locals_ = get_local_providers()

        assert isinstance(locals_, list)
        assert len(locals_) > 0
        assert all(p.is_local is True for p in locals_)


# =============================================================================
# TestGetProviderForModel - 模型匹配测试
# =============================================================================


class TestGetProviderForModel:
    """根据模型获取提供商测�?""

    def test_get_provider_for_model_openai(self):
        """测试 OpenAI 模型匹配"""
        provider = get_provider_for_model("gpt-4o")

        assert provider is not None
        assert provider.name == "openai"

    def test_get_provider_for_model_anthropic(self):
        """测试 Anthropic 模型匹配"""
        provider = get_provider_for_model("claude-3-5-sonnet")

        assert provider is not None
        assert provider.name == "anthropic"

    def test_get_provider_for_model_gemini(self):
        """测试 Gemini 模型匹配"""
        provider = get_provider_for_model("gemini-2.0-flash")

        assert provider is not None
        assert provider.name == "gemini"

    def test_get_provider_for_model_deepseek(self):
        """测试 DeepSeek 模型匹配"""
        provider = get_provider_for_model("deepseek-chat")

        assert provider is not None
        assert provider.name == "deepseek"

    def test_get_provider_for_model_with_prefix(self):
        """测试带前缀的模型名�?""
        provider = get_provider_for_model("openai/gpt-4o")

        assert provider is not None
        assert provider.name == "openai"

    def test_get_provider_for_model_unknown(self):
        """测试未知模型"""
        # 未知模型应该回退到网关提供商
        provider = get_provider_for_model("unknown-model-xyz")

        # 要么找到网关提供商，要么返回 None（如果没有网关）
        if provider:
            assert provider.is_gateway is True

    def test_get_provider_for_model_no_fallback(self):
        """测试禁用回退"""
        provider = get_provider_for_model(
            "unknown-model-xyz",
            fallback_to_gateway=False,
        )

        assert provider is None


# =============================================================================
# TestFormatModelName - 模型名称格式化测�?
# =============================================================================


class TestFormatModelName:
    """模型名称格式化测�?""

    def test_format_model_name_adds_prefix(self):
        """测试添加提供商前缀"""
        result = format_model_name("gpt-4o")

        assert result == "openai/gpt-4o"

    def test_format_model_name_already_has_prefix(self):
        """测试已有前缀的模型名�?""
        result = format_model_name("openai/gpt-4o")

        assert result == "openai/gpt-4o"

    def test_format_model_name_with_provider(self):
        """测试指定提供�?""
        provider = get_provider_by_name("anthropic")
        result = format_model_name("claude-3-5-sonnet", provider)

        assert result == "anthropic/claude-3-5-sonnet"

    def test_format_model_name_claude(self):
        """测试 Claude 模型"""
        result = format_model_name("claude-3-haiku")

        assert "anthropic/" in result

    def test_format_model_name_ollama(self):
        """测试 Ollama 模型"""
        result = format_model_name("llama3")

        assert "ollama/" in result


# =============================================================================
# TestGetPresetModel - 预设模型测试
# =============================================================================


class TestGetPresetModel:
    """预设模型测试"""

    def test_get_preset_model_exists(self):
        """测试获取存在的预设模�?""
        result = get_preset_model("gpt-4o")

        assert result is not None
        assert result == "openai/gpt-4o"

    def test_get_preset_model_claude(self):
        """测试获取 Claude 预设模型"""
        result = get_preset_model("claude-3-5-sonnet")

        assert result is not None
        assert "anthropic/" in result

    def test_get_preset_model_not_found(self):
        """测试获取不存在的预设模型"""
        result = get_preset_model("nonexistent-model")

        assert result is None

    def test_popular_models_not_empty(self):
        """测试预设模型列表不为�?""
        assert len(POPULAR_MODELS) > 0

    def test_popular_models_format(self):
        """测试预设模型格式"""
        for name, model in POPULAR_MODELS.items():
            assert "/" in model  # 应该包含提供商前缀


# =============================================================================
# TestProvidersRegistry - 注册表完整性测�?
# =============================================================================


class TestProvidersRegistry:
    """提供商注册表完整性测�?""

    def test_providers_not_empty(self):
        """测试注册表不为空"""
        assert len(PROVIDERS) > 0

    def test_providers_unique_names(self):
        """测试提供商名称唯一"""
        names = [p.name for p in PROVIDERS]
        assert len(names) == len(set(names))  # 名称应该唯一

    def test_providers_have_required_fields(self):
        """测试提供商有必填字段"""
        for provider in PROVIDERS:
            assert provider.name
            assert provider.display_name
            assert isinstance(provider.keywords, list)
            assert len(provider.keywords) > 0

    def test_providers_gateway_count(self):
        """测试网关提供商数�?""
        gateways = [p for p in PROVIDERS if p.is_gateway]
        assert len(gateways) > 0

    def test_providers_local_count(self):
        """测试本地提供商数�?""
        locals_ = [p for p in PROVIDERS if p.is_local]
        assert len(locals_) > 0

    def test_providers_env_keys(self):
        """测试提供商环境变量密�?""
        # 大部分提供商应该有环境变量密�?
        providers_with_env = [p for p in PROVIDERS if p.env_key]
        assert len(providers_with_env) > 0

    def test_providers_litellm_prefixes(self):
        """测试提供�?LiteLLM 前缀"""
        # 大部分提供商应该有前缀
        providers_with_prefix = [p for p in PROVIDERS if p.litellm_prefix]
        assert len(providers_with_prefix) > 0

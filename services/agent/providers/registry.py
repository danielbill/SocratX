"""
LLM Provider Registry - LLM 提供商注册表

参考: nanobot/nanobot/providers/registry.py
支持 15+ LLM 提供商的统一接口
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderSpec:
    """
    LLM 提供商规格

    Args:
        name: 提供商名称（用于配置）
        display_name: 显示名称
        keywords: 模型名称关键字列表（用于自动匹配）
        env_key: LiteLLM 环境变量
        litellm_prefix: 模型路由前缀
        is_gateway: 是否为网关提供商
        is_local: 是否为本地提供商
        is_oauth: 是否使用 OAuth 认证
        base_url: 自定义 API base URL
    """

    name: str
    display_name: str
    keywords: list[str]
    env_key: str = ""
    litellm_prefix: str = ""
    is_gateway: bool = False
    is_local: bool = False
    is_oauth: bool = False
    base_url: Optional[str] = None

    def matches_model(self, model: str) -> bool:
        """
        检查模型名称是否匹配此提供商

        Args:
            model: 模型名称

        Returns:
            是否匹配
        """
        model_lower = model.lower()
        return any(keyword in model_lower for keyword in self.keywords)


# LLM 提供商注册表
PROVIDERS: list[ProviderSpec] = [
    # 网关提供商（优先使用）
    ProviderSpec(
        name="openrouter",
        display_name="OpenRouter",
        keywords=["openrouter"],
        env_key="OPENROUTER_API_KEY",
        litellm_prefix="openrouter/",
        is_gateway=True,
    ),
    ProviderSpec(
        name="aihubmix",
        display_name="AiHubMix",
        keywords=["aihubmix"],
        env_key="AIHUBMIX_API_KEY",
        litellm_prefix="aihubmix/",
        is_gateway=True,
    ),

    # 主要提供商
    ProviderSpec(
        name="anthropic",
        display_name="Anthropic (Claude)",
        keywords=["claude", "anthropic"],
        env_key="ANTHROPIC_API_KEY",
        litellm_prefix="anthropic/",
    ),
    ProviderSpec(
        name="openai",
        display_name="OpenAI",
        keywords=["gpt", "openai", "chatgpt"],
        env_key="OPENAI_API_KEY",
        litellm_prefix="openai/",
    ),
    ProviderSpec(
        name="deepseek",
        display_name="DeepSeek",
        keywords=["deepseek"],
        env_key="DEEPSEEK_API_KEY",
        litellm_prefix="deepseek/",
    ),
    ProviderSpec(
        name="gemini",
        display_name="Google Gemini",
        keywords=["gemini", "google"],
        env_key="GEMINI_API_KEY",
        litellm_prefix="gemini/",
    ),
    ProviderSpec(
        name="zhipu",
        display_name="智谱 AI (旧版)",
        keywords=["zhipu", "chatglm"],  # 移除 glm，避免与 zai 冲突
        env_key="ZHIPUAI_API_KEY",
        litellm_prefix="zhipu/",
    ),
    ProviderSpec(
        name="zai",
        display_name="Z.ai (智谱 AI)",
        keywords=["glm", "zai", "z.ai"],
        env_key="ZAI_API_KEY",
        litellm_prefix="zai/",
    ),
    ProviderSpec(
        name="dashscope",
        display_name="通义千问 (DashScope)",
        keywords=["qwen", "dashscope", "aliyun", "通义"],
        env_key="DASHSCOPE_API_KEY",
        litellm_prefix="dashscope/",
    ),
    ProviderSpec(
        name="moonshot",
        display_name="月之暗面 (Kimi)",
        keywords=["moonshot", "kimi", "月之暗面"],
        env_key="MOONSHOT_API_KEY",
        litellm_prefix="moonshot/",
    ),
    ProviderSpec(
        name="minimax",
        display_name="MiniMax",
        keywords=["minimax"],
        env_key="MINIMAX_API_KEY",
        litellm_prefix="minimax/",
    ),
    ProviderSpec(
        name="baichuan",
        display_name="百川智能",
        keywords=["baichuan", "百川"],
        env_key="BAICHUAN_API_KEY",
        litellm_prefix="baichuan/",
    ),

    # 本地提供商
    ProviderSpec(
        name="ollama",
        display_name="Ollama (本地)",
        keywords=["ollama", "llama"],
        env_key="",
        litellm_prefix="ollama/",
        is_local=True,
    ),
    ProviderSpec(
        name="vllm",
        display_name="vLLM (本地)",
        keywords=["vllm"],
        env_key="",
        litellm_prefix="openai/",  # vLLM 使用 OpenAI 兼容 API
        is_local=True,
        base_url="http://localhost:8000",
    ),

    # 其他提供商
    ProviderSpec(
        name="groq",
        display_name="Groq",
        keywords=["groq", "llama3-groq"],
        env_key="GROQ_API_KEY",
        litellm_prefix="groq/",
    ),
    ProviderSpec(
        name="together",
        display_name="Together AI",
        keywords=["together"],
        env_key="TOGETHER_API_KEY",
        litellm_prefix="together/",
    ),
    ProviderSpec(
        name="azure",
        display_name="Azure OpenAI",
        keywords=["azure"],
        env_key="AZURE_API_KEY",
        litellm_prefix="azure/",
    ),
]


def get_provider_by_name(name: str) -> Optional[ProviderSpec]:
    """
    根据名称获取提供商

    Args:
        name: 提供商名称

    Returns:
        ProviderSpec 或 None
    """
    for provider in PROVIDERS:
        if provider.name == name:
            return provider
    return None


def get_provider_for_model(model: str, fallback_to_gateway: bool = True) -> Optional[ProviderSpec]:
    """
    根据模型名称自动匹配提供商

    Args:
        model: 模型名称
        fallback_to_gateway: 是否回退到网关提供商

    Returns:
        匹配的 ProviderSpec
    """
    # 首先尝试精确匹配
    for provider in PROVIDERS:
        if provider.matches_model(model):
            return provider

    # 回退到网关提供商
    if fallback_to_gateway:
        for provider in PROVIDERS:
            if provider.is_gateway:
                return provider

    return None


def get_all_providers() -> list[ProviderSpec]:
    """获取所有提供商"""
    return PROVIDERS.copy()


def get_gateway_providers() -> list[ProviderSpec]:
    """获取所有网关提供商"""
    return [p for p in PROVIDERS if p.is_gateway]


def get_local_providers() -> list[ProviderSpec]:
    """获取所有本地提供商"""
    return [p for p in PROVIDERS if p.is_local]


def format_model_name(model: str, provider: Optional[ProviderSpec] = None) -> str:
    """
    格式化模型名称为 LiteLLM 格式

    Args:
        model: 原始模型名称
        provider: 提供商规格（可选）

    Returns:
        格式化后的模型名称
    """
    # 如果已经包含前缀，直接返回
    if "/" in model and model.split("/")[0] in [p.litellm_prefix.rstrip("/") for p in PROVIDERS if p.litellm_prefix]:
        return model

    # 自动检测提供商
    if provider is None:
        provider = get_provider_for_model(model, fallback_to_gateway=False)

    # 添加提供商前缀
    if provider and provider.litellm_prefix:
        # 检查模型名是否已经包含前缀
        if not model.startswith(provider.litellm_prefix):
            return f"{provider.litellm_prefix}{model}"

    return model


# 常用模型预设
POPULAR_MODELS = {
    # Anthropic
    "claude-sonnet-4": "anthropic/claude-sonnet-4-20250514",
    "claude-opus-4": "anthropic/claude-opus-4-20250514",
    "claude-3-5-sonnet": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3-haiku": "anthropic/claude-3-haiku-20240307",

    # OpenAI
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",

    # DeepSeek
    "deepseek-chat": "deepseek/deepseek-chat",
    "deepseek-coder": "deepseek/deepseek-coder",

    # Google
    "gemini-2.0-flash": "gemini/gemini-2.0-flash-exp",
    "gemini-pro": "gemini/gemini-pro",

    # 智谱
    "glm-4": "zhipu/glm-4",
    "glm-4-plus": "zhipu/glm-4-plus",

    # 通义
    "qwen-turbo": "dashscope/qwen-turbo",
    "qwen-plus": "dashscope/qwen-plus",
    "qwen-max": "dashscope/qwen-max",

    # Kimi
    "moonshot-v1": "moonshot/moonshot-v1-8k",
    "moonshot-v1-32k": "moonshot/moonshot-v1-32k",

    # 本地
    "llama3": "ollama/llama3",
    "llama3-8b": "ollama/llama3:8b",
    "qwen2": "ollama/qwen2",
}


def get_preset_model(name: str) -> Optional[str]:
    """
    获取预设模型

    Args:
        name: 预设名称

    Returns:
        完整模型名称或 None
    """
    return POPULAR_MODELS.get(name)

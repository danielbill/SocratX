"""
Config Schema - 配置模型定义

参考: nanobot/nanobot/config/schema.py
使用 Pydantic 定义配置结构
"""

from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """代理配置"""

    model: str = Field(default="zhipu/glm-4", description="默认模型")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(default=4096, gt=0, description="最大输出 token")
    max_iterations: int = Field(default=20, gt=0, description="最大工具调用迭代次数")
    workspace: str = Field(default="", description="工作区路径")

    # 记忆配置
    memory_enabled: bool = Field(default=True, description="启用记忆系统")
    memory_file: str = Field(default="MEMORY.md", description="记忆文件名")
    history_file: str = Field(default="HISTORY.md", description="历史文件名")

    # 会话配置
    session_ttl: int = Field(default=86400, description="会话过期时间（秒）")


class ToolConfig(BaseModel):
    """工具配置"""

    enabled: List[str] = Field(
        default_factory=lambda: ["file_read", "file_write", "shell_exec", "web_search"],
        description="启用的工具列表"
    )

    # 工具限制
    workspace_read_only: bool = Field(default=False, description="工作区只读模式")
    allow_shell: bool = Field(default=True, description="允许执行 shell 命令")
    allowed_shell_commands: List[str] = Field(
        default_factory=list,
        description="允许的 shell 命令白名单（空=无限制）"
    )

    # MCP 服务器
    mcp_servers: List[str] = Field(
        default_factory=list,
        description="MCP 服务器 URL 列表"
    )


class ProviderConfig(BaseModel):
    """LLM 提供商配置"""
    api_key: str = Field(default="", alias="apiKey")
    api_base: str | None = Field(default=None, alias="apiBase")
    extra_headers: dict[str, str] | None = Field(default=None, alias="extraHeaders")
    
    model_config = {"populate_by_name": True}


class ProvidersConfig(BaseModel):
    """LLM 提供商集合配置"""
    custom: ProviderConfig = Field(default_factory=ProviderConfig)
    anthropic: ProviderConfig = Field(default_factory=ProviderConfig)
    openai: ProviderConfig = Field(default_factory=ProviderConfig)
    openrouter: ProviderConfig = Field(default_factory=ProviderConfig)
    deepseek: ProviderConfig = Field(default_factory=ProviderConfig)
    zhipu: ProviderConfig = Field(default_factory=ProviderConfig)
    zai: ProviderConfig = Field(default_factory=ProviderConfig)  # Z.ai (智谱 AI 新版)
    dashscope: ProviderConfig = Field(default_factory=ProviderConfig)
    gemini: ProviderConfig = Field(default_factory=ProviderConfig)
    moonshot: ProviderConfig = Field(default_factory=ProviderConfig)
    ollama: ProviderConfig = Field(default_factory=ProviderConfig)
    vllm: ProviderConfig = Field(default_factory=ProviderConfig)


class GatewayConfig(BaseModel):
    """网关配置"""

    host: str = Field(default="127.0.0.1", description="监听地址")
    port: int = Field(default=8000, gt=0, lt=65536, description="监听端口")

    # CORS
    allow_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:1420"],
        description="允许的 CORS 源"
    )

    # 认证
    require_auth: bool = Field(default=False, description="是否需要认证")
    api_key: Optional[str] = Field(default=None, description="API 认证密钥")


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = Field(default="INFO", description="日志级别")
    file: Optional[str] = Field(default=None, description="日志文件路径")
    rotate: bool = Field(default=True, description="是否轮转日志")
    max_size: int = Field(default=10 * 1024 * 1024, description="日志文件最大大小（字节）")


class SocratXConfig(BaseModel):
    """SocratX 完整配置"""

    version: str = Field(default="1.0.0", description="配置版本")

    agent: AgentConfig = Field(default_factory=AgentConfig, description="代理配置")
    tools: ToolConfig = Field(default_factory=ToolConfig, description="工具配置")
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig, description="提供商配置")
    gateway: GatewayConfig = Field(default_factory=GatewayConfig, description="网关配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            Path: str,
        }
        # 允许字段别名
        populate_by_name = True

    def get_provider_api_key(self, provider_name: str) -> Optional[str]:
        """
        获取指定提供商的 API 密钥

        Args:
            provider_name: 提供商名称

        Returns:
            API 密钥或 None
        """
        # 从 providers 中获取对应的 provider 配置
        if hasattr(self.providers, provider_name):
            provider_config = getattr(self.providers, provider_name)
            if hasattr(provider_config, "api_key"):
                return provider_config.api_key
        return None

    def model_dump_json(self, **kwargs) -> str:
        """导出为 JSON"""
        return super().model_dump_json(exclude_none=True, indent=2, **kwargs)


# 默认配置
DEFAULT_CONFIG = SocratXConfig(
    agent=AgentConfig(
        model="zhipu/glm-4",
    ),
)


def get_default_config() -> SocratXConfig:
    """获取默认配置"""
    return DEFAULT_CONFIG.model_copy()

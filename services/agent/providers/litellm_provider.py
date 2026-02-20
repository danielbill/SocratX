"""
LiteLLM Provider - 基于 LiteLLM 的 LLM 提供商实现

参考: nanobot/nanobot/providers/litellm_provider.py
统一的 LLM 调用接口，支持 100+ 模型
"""

import asyncio
import os
import logging
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime

from .registry import (
    get_provider_for_model,
    format_model_name,
    ProviderSpec,
)

# 获取 AI 日志记录器
ai_logger = logging.getLogger("socratx.ai")


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ToolCall:
    """工具调用"""
    id: str
    type: str = "function"
    function: Optional[dict] = None


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    tool_calls: list[dict] = None
    model: str = ""
    usage: dict = None

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []
        if self.usage is None:
            self.usage = {}


class LiteLLMProvider:
    """
    基于 LiteLLM 的 LLM 提供商

    提供统一的接口调用多种 LLM 提供商
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """
        初始化 LLM 提供商

        Args:
            model: 模型名称
            api_key: API 密钥（可选，默认从环境变量读取）
            base_url: 自定义 API base URL
            temperature: 温度参数
            max_tokens: 最大 token 数
        """
        print(f"LiteLLMProvider init: model={model}, api_key={'***' if api_key else 'None'}")
        
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 检测提供商
        self.provider = get_provider_for_model(model)
        print(f"Provider detected: {self.provider.name if self.provider else 'None'}")

        # 格式化模型名称
        self.formatted_model = format_model_name(model, self.provider)
        print(f"Formatted model: {self.formatted_model}")

        # 设置环境变量
        self._setup_env()

    def _setup_env(self) -> None:
        """设置 LiteLLM 环境变量"""
        if self.provider and self.provider.env_key and not self.api_key:
            # 从环境变量获取 API key
            self.api_key = os.getenv(self.provider.env_key)

        if self.api_key:
            # 设置所有可能的 API Key 环境变量
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
            os.environ["OPENAI_API_KEY"] = self.api_key
            os.environ["OPENROUTER_API_KEY"] = self.api_key
            os.environ["ZHIPUAI_API_KEY"] = self.api_key
            os.environ["DASHSCOPE_API_KEY"] = self.api_key
            os.environ["GEMINI_API_KEY"] = self.api_key
            os.environ["DEEPSEEK_API_KEY"] = self.api_key
            os.environ["MOONSHOT_API_KEY"] = self.api_key
            
            # 设置 LiteLLM 特定的 API Key 格式
            os.environ[f"{self.provider.name.upper()}_API_KEY"] = self.api_key
        else:
            # 调试：记录 API Key 缺失
            print(f"WARNING: No API key for provider: {self.provider.name if self.provider else 'unknown'}")

        if self.base_url:
            os.environ["OPENAI_API_BASE"] = self.base_url

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            tools: 工具 schema 列表
            model: 覆盖默认模型
            temperature: 覆盖默认温度
            max_tokens: 覆盖默认最大 token
            **kwargs: 其他参数

        Returns:
            LLMResponse
        """
        # 导入 litellm（延迟导入，避免未安装时的错误）
        try:
            from litellm import acompletion
        except ImportError:
            raise ImportError(
                "litellm is not installed. "
                "Install it with: pip install litellm"
            )

        # 使用提供的模型或默认模型
        model_to_use = model or self.formatted_model

        # 构建请求参数
        request_params = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }
        
        # 传递 API Key（如果已设置）
        if self.api_key:
            request_params["api_key"] = self.api_key
            
        # 传递 API Base（如果已设置）
        if self.base_url:
            request_params["api_base"] = self.base_url

        # 添加工具（如果提供）
        if tools:
            request_params["tools"] = tools

        # 添加额外参数
        request_params.update(kwargs)

        try:
            # 调用 LLM - 记录请求
            msg_preview = str(messages)[:200] + "..." if len(str(messages)) > 200 else str(messages)
            ai_logger.info("[REQUEST] Model: %s | Messages: %s", model_to_use, msg_preview)
            
            response = await acompletion(**request_params)

            # 解析响应
            llm_response = self._parse_response(response)
            
            # 记录 AI 响应
            content_preview = llm_response.content[:100] + "..." if len(llm_response.content) > 100 else llm_response.content
            usage_str = f" | Usage: {llm_response.usage}" if llm_response.usage else ""
            ai_logger.info("[RESPONSE] %s%s", content_preview, usage_str)
            
            return llm_response

        except Exception as e:
            # 错误处理
            ai_logger.error("Error calling LLM: %s", e, exc_info=True)
            return LLMResponse(
                content=f"Error calling LLM: {str(e)}",
                model=model_to_use,
            )

    def _parse_response(self, response: Any) -> LLMResponse:
        """
        解析 LLM 响应

        Args:
            response: litellm 响应对象

        Returns:
            LLMResponse
        """
        # 获取内容
        content = ""
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message") and choice.message:
                message = choice.message
                content = getattr(message, "content", "") or ""

        # 获取工具调用
        tool_calls = []
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message") and choice.message:
                message = choice.message
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tc in message.tool_calls:
                        tool_calls.append({
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        })

        # 获取使用信息
        usage = {}
        if hasattr(response, "usage"):
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, "prompt_tokens") else 0,
                "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, "completion_tokens") else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response.usage, "total_tokens") else 0,
            }

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            model=getattr(response, "model", self.model),
            usage=usage,
        )

    async def stream_chat(
        self,
        messages: list[dict],
        **kwargs,
    ):
        """
        流式聊天（暂不实现，留作扩展）

        Args:
            messages: 消息列表
            **kwargs: 其他参数
        """
        raise NotImplementedError("Streaming is not yet implemented")


class MockLLMProvider:
    """
    Mock LLM 提供商，用于测试

    返回预定义的响应，不调用真实 API
    """

    def __init__(self, response: str = "This is a mock response."):
        self.response = response

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] = None,
        **kwargs,
    ) -> LLMResponse:
        """返回 mock 响应"""
        # 检查最后一条消息
        if messages:
            last_message = messages[-1]
            if last_message.get("role") == "user":
                content = f"Mock response to: {last_message.get('content', '')[:50]}..."
            else:
                content = self.response
        else:
            content = self.response

        return LLMResponse(
            content=content,
            model="mock-model",
        )


# 便捷函数
async def create_provider(
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    mock: bool = False,
) -> LiteLLMProvider | MockLLMProvider:
    """
    创建 LLM 提供商

    Args:
        model: 模型名称
        api_key: API 密钥
        base_url: API Base URL
        mock: 是否使用 mock 提供商

    Returns:
        LLM 提供商实例
    """
    if mock:
        return MockLLMProvider()

    return LiteLLMProvider(
        model=model,
        api_key=api_key,
        base_url=base_url,
    )

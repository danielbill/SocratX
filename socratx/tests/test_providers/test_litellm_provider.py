"""LiteLLM Provider 测试"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

from providers.litellm_provider import (
    LiteLLMProvider,
    MockLLMProvider,
    LLMResponse,
    ChatMessage,
    ToolCall,
    create_provider,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_litellm_response():
    """创建 Mock litellm 响应对象"""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Hello! How can I help you?",
                tool_calls=None,
            )
        )
    ]
    mock_response.usage = MagicMock(
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
    )
    mock_response.model = "gpt-4o"
    return mock_response


@pytest.fixture
def mock_litellm_with_tool_calls():
    """创建带工具调用的 Mock litellm 响应"""
    # 创建 function mock
    mock_function = MagicMock()
    mock_function.name = "search"
    mock_function.arguments = '{"query": "test"}'

    # 创建 tool call mock
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_123"
    mock_tool_call.type = "function"
    mock_tool_call.function = mock_function

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=None,
                tool_calls=[mock_tool_call],
            )
        )
    ]
    mock_response.usage = MagicMock(
        prompt_tokens=15,
        completion_tokens=5,
        total_tokens=20,
    )
    mock_response.model = "gpt-4o"
    return mock_response


# =============================================================================
# TestLiteLLMProviderInit - 初始化测�?
# =============================================================================


class TestLiteLLMProviderInit:
    """LiteLLMProvider 初始化测�?""

    def test_init_default(self):
        """测试默认初始�?""
        provider = LiteLLMProvider()

        assert provider.model == "gpt-4o-mini"
        assert provider.temperature == 0.7
        assert provider.max_tokens == 4096
        assert provider.api_key is None
        assert provider.base_url is None

    def test_init_with_api_key(self):
        """测试�?API 密钥初始�?""
        provider = LiteLLMProvider(
            model="anthropic/claude-3-5-sonnet",
            api_key="sk-test-key-123",
            temperature=0.5,
            max_tokens=2048,
        )

        assert provider.model == "anthropic/claude-3-5-sonnet"
        assert provider.api_key == "sk-test-key-123"
        assert provider.temperature == 0.5
        assert provider.max_tokens == 2048

    def test_init_with_custom_params(self):
        """测试自定义参数初始化"""
        provider = LiteLLMProvider(
            model="openai/gpt-4-turbo",
            base_url="https://api.example.com/v1",
            temperature=0.9,
            max_tokens=8192,
        )

        assert provider.model == "openai/gpt-4-turbo"
        assert provider.base_url == "https://api.example.com/v1"
        assert provider.temperature == 0.9
        assert provider.max_tokens == 8192

    def test_setup_env(self, monkeypatch):
        """测试环境变量设置"""
        # 清除可能存在的环境变�?
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        provider = LiteLLMProvider(
            model="openai/gpt-4o",
            api_key="sk-test-key",
        )

        # 验证环境变量被设�?
        assert os.environ.get("OPENAI_API_KEY") == "sk-test-key"
        assert os.environ.get("ANTHROPIC_API_KEY") == "sk-test-key"

    def test_setup_env_with_base_url(self, monkeypatch):
        """测试�?base URL 的环境变量设�?""
        monkeypatch.delenv("OPENAI_API_BASE", raising=False)

        provider = LiteLLMProvider(
            model="openai/gpt-4o",
            base_url="https://custom.api.com/v1",
        )

        assert os.environ.get("OPENAI_API_BASE") == "https://custom.api.com/v1"


# =============================================================================
# TestLiteLLMProviderChat - 聊天测试
# =============================================================================


class TestLiteLLMProviderChat:
    """LiteLLMProvider 聊天测试"""

    @pytest.mark.asyncio
    async def test_chat_basic(self, mocker, mock_litellm_response):
        """测试基础聊天"""
        # Mock litellm.acompletion
        mocker.patch(
            "litellm.acompletion",
            return_value=mock_litellm_response,
        )

        provider = LiteLLMProvider(model="gpt-4o")
        response = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}]
        )

        assert response.content == "Hello! How can I help you?"
        assert response.model == "gpt-4o"
        assert response.usage["total_tokens"] == 30
        assert len(response.tool_calls) == 0

    @pytest.mark.asyncio
    async def test_chat_with_tools(self, mocker, mock_litellm_with_tool_calls):
        """测试带工具调�?""
        mocker.patch(
            "litellm.acompletion",
            return_value=mock_litellm_with_tool_calls,
        )

        provider = LiteLLMProvider(model="gpt-4o")
        response = await provider.chat(
            messages=[{"role": "user", "content": "Search for test"}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "search",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            },
                        },
                    },
                }
            ],
        )

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["id"] == "call_123"
        assert response.tool_calls[0]["function"]["name"] == "search"

    @pytest.mark.asyncio
    async def test_chat_with_system_prompt(self, mocker, mock_litellm_response):
        """测试带系统提�?""
        mocker.patch(
            "litellm.acompletion",
            return_value=mock_litellm_response,
        )

        provider = LiteLLMProvider(model="gpt-4o")
        response = await provider.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
            ]
        )

        assert response.content == "Hello! How can I help you?"

    @pytest.mark.asyncio
    async def test_chat_error_handling(self, mocker):
        """测试错误处理"""
        # Mock litellm 抛出异常
        mocker.patch(
            "litellm.acompletion",
            side_effect=Exception("API error"),
        )

        provider = LiteLLMProvider(model="gpt-4o")
        response = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}]
        )

        # 应该返回错误响应而不是抛出异�?
        assert "Error calling LLM" in response.content
        assert "API error" in response.content

    @pytest.mark.asyncio
    async def test_chat_with_override_params(self, mocker, mock_litellm_response):
        """测试覆盖默认参数"""
        mocker.patch(
            "litellm.acompletion",
            return_value=mock_litellm_response,
        )

        provider = LiteLLMProvider(
            model="gpt-4o",
            temperature=0.5,
            max_tokens=1000,
        )

        response = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.9,
            max_tokens=2000,
            model="gpt-4-turbo",
        )

        # 验证使用了覆盖参�?
        assert response.content == "Hello! How can I help you?"


# =============================================================================
# TestLiteLLMProviderParse - 响应解析测试
# =============================================================================


class TestLiteLLMProviderParse:
    """LiteLLMProvider 响应解析测试"""

    def test_parse_simple_response(self, mock_litellm_response):
        """测试解析简单响�?""
        provider = LiteLLMProvider(model="gpt-4o")
        response = provider._parse_response(mock_litellm_response)

        assert response.content == "Hello! How can I help you?"
        assert response.model == "gpt-4o"
        assert response.usage["total_tokens"] == 30
        assert len(response.tool_calls) == 0

    def test_parse_tool_call_response(self, mock_litellm_with_tool_calls):
        """测试解析工具调用响应"""
        provider = LiteLLMProvider(model="gpt-4o")
        response = provider._parse_response(mock_litellm_with_tool_calls)

        assert response.content is None or response.content == ""
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["id"] == "call_123"
        assert response.tool_calls[0]["function"]["name"] == "search"

    def test_parse_empty_response(self):
        """测试解析空响�?""
        # 创建一个空�?Mock 响应
        mock_response = MagicMock()
        mock_response.choices = []
        mock_response.usage = MagicMock(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
        )
        mock_response.model = "gpt-4o"

        provider = LiteLLMProvider(model="gpt-4o")
        response = provider._parse_response(mock_response)

        assert response.content == ""
        assert len(response.tool_calls) == 0

    def test_parse_malformed_response(self):
        """测试解析格式错误响应"""
        # 创建一个缺少属性的 Mock 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=None)]
        mock_response.usage = None
        mock_response.model = "gpt-4o"

        provider = LiteLLMProvider(model="gpt-4o")
        response = provider._parse_response(mock_response)

        # 应该处理 None 值而不抛出异常
        assert response.content == ""
        assert len(response.tool_calls) == 0


# =============================================================================
# TestMockLLMProvider - Mock 提供商测�?
# =============================================================================


class TestMockLLMProvider:
    """MockLLMProvider 测试"""

    @pytest.mark.asyncio
    async def test_mock_chat(self):
        """测试 Mock 聊天"""
        provider = MockLLMProvider(response="Mock response")

        response = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}]
        )

        assert "Mock response" in response.content or "Mock response to:" in response.content
        assert response.model == "mock-model"

    @pytest.mark.asyncio
    async def test_mock_chat_with_tool_calls(self):
        """测试 Mock 带工具调�?""
        provider = MockLLMProvider(response="Mock response")

        response = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            tools=[{"type": "function", "function": {"name": "test"}}],
        )

        # Mock provider 应该忽略工具参数
        assert response.model == "mock-model"

    @pytest.mark.asyncio
    async def test_mock_chat_empty_messages(self):
        """测试 Mock 空消息列�?""
        provider = MockLLMProvider(response="Default mock response")

        response = await provider.chat(messages=[])

        assert response.content == "Default mock response"


# =============================================================================
# TestCreateProvider - 便捷函数测试
# =============================================================================


class TestCreateProvider:
    """create_provider 函数测试"""

    @pytest.mark.asyncio
    async def test_create_provider_mock(self):
        """测试创建 Mock 提供�?""
        provider = await create_provider(mock=True)

        assert isinstance(provider, MockLLMProvider)

    @pytest.mark.asyncio
    async def test_create_provider_real(self):
        """测试创建真实提供�?""
        provider = await create_provider(
            model="gpt-4o",
            api_key="sk-test-key",
        )

        assert isinstance(provider, LiteLLMProvider)
        assert provider.model == "gpt-4o"


# =============================================================================
# TestLLMResponse - 数据类测�?
# =============================================================================


class TestLLMResponse:
    """LLMResponse 数据类测�?""

    def test_llm_response_default(self):
        """测试 LLMResponse 默认�?""
        response = LLMResponse(content="Test")

        assert response.content == "Test"
        assert response.tool_calls == []
        assert response.model == ""
        assert response.usage == {}

    def test_llm_response_with_values(self):
        """测试 LLMResponse 带�?""
        response = LLMResponse(
            content="Test",
            tool_calls=[{"id": "1", "function": {"name": "test"}}],
            model="gpt-4o",
            usage={"total_tokens": 100},
        )

        assert response.content == "Test"
        assert len(response.tool_calls) == 1
        assert response.model == "gpt-4o"
        assert response.usage["total_tokens"] == 100


# =============================================================================
# TestChatMessage - 数据类测�?
# =============================================================================


class TestChatMessage:
    """ChatMessage 数据类测�?""

    def test_chat_message_user(self):
        """测试用户消息"""
        msg = ChatMessage(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.tool_calls is None

    def test_chat_message_with_tool_calls(self):
        """测试带工具调用的消息"""
        msg = ChatMessage(
            role="assistant",
            content=None,
            tool_calls=[{"id": "1", "function": {"name": "test"}}],
        )

        assert msg.role == "assistant"
        assert msg.content is None
        assert len(msg.tool_calls) == 1

"""AgentLoop 核心测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from agent.loop import AgentLoop, AgentConfig, AgentResponse, create_agent_loop
from agent.session import SessionManager, Session, Message
from agent.memory import MemoryStore
from agent.tools.registry import ToolRegistry, SimpleTool, ToolResult
from agent.context import ContextBuilder
from providers.litellm_provider import LLMResponse, MockLLMProvider


# =============================================================================
# Mock 工具定义
# =============================================================================


class MockTool(SimpleTool):
    """测试用 Mock 工具"""

    async def execute(self, **kwargs):
        """Mock 执行"""
        return ToolResult(
            success=True,
            content=f"Mock tool executed with args: {kwargs}",
        )


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def config(tmp_path) -> AgentConfig:
    """创建测试配置"""
    return AgentConfig(
        model="mock-model",
        temperature=0.7,
        max_tokens=4096,
        max_iterations=5,
        workspace=str(tmp_path),
        memory_enabled=True,
    )


@pytest.fixture
def session_manager(tmp_path) -> SessionManager:
    """创建会话管理器"""
    return SessionManager(storage_dir=tmp_path / "sessions")


@pytest.fixture
def memory_store(tmp_path) -> MemoryStore:
    """创建记忆存储"""
    return MemoryStore(tmp_path)


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """创建工具注册表"""
    registry = ToolRegistry()
    # 注册一个测试工具
    registry.register_simple(
        name="test_tool",
        description="A test tool",
        handler=lambda **kwargs: f"Test result: {kwargs}",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Test query"},
            },
            "required": ["query"],
        },
    )
    return registry


@pytest.fixture
def context_builder() -> ContextBuilder:
    """创建上下文构建器"""
    return ContextBuilder()


@pytest.fixture
def mock_llm_provider():
    """创建 Mock LLM 提供商"""
    provider = MockLLMProvider(response="Mock response from LLM")
    return provider


@pytest.fixture
def agent_loop(config, session_manager, memory_store, tool_registry, context_builder, mock_llm_provider):
    """创建完整的 AgentLoop 实例"""
    loop = AgentLoop(
        config=config,
        session_manager=session_manager,
        memory_store=memory_store,
        tool_registry=tool_registry,
        context_builder=context_builder,
    )
    loop.set_llm_provider(mock_llm_provider)
    return loop


# =============================================================================
# TestAgentLoopBasic - 基础功能测试
# =============================================================================


class TestAgentLoopBasic:
    """AgentLoop 基础功能测试"""

    def test_init(self, config, session_manager, memory_store, tool_registry):
        """测试初始化"""
        loop = AgentLoop(
            config=config,
            session_manager=session_manager,
            memory_store=memory_store,
            tool_registry=tool_registry,
        )

        assert loop.config == config
        assert loop.session_manager == session_manager
        assert loop.memory_store == memory_store
        assert loop.tool_registry == tool_registry
        assert loop._llm_provider is None

    @pytest.mark.asyncio
    async def test_run_simple_message(self, agent_loop):
        """测试简单消息处理"""
        response = await agent_loop.run(
            message="Hello",
            session_id="test-session",
            user_id="user-1",
        )

        assert isinstance(response, AgentResponse)
        assert response.content != ""
        assert isinstance(response.content, str)
        assert len(response.tool_calls) == 0

    @pytest.mark.asyncio
    async def test_run_adds_to_session(self, agent_loop, session_manager):
        """测试消息添加到会话"""
        await agent_loop.run(
            message="Test message",
            session_id="test-session",
            user_id="user-1",
        )

        session = session_manager.get("test-session")
        assert session is not None
        assert len(session.messages) == 2  # 用户消息 + 助手响应
        assert session.messages[0].role == "user"
        assert session.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_run_returns_response(self, agent_loop):
        """测试返回响应"""
        response = await agent_loop.run(
            message="What is the weather?",
            session_id="test-session",
        )

        assert isinstance(response, AgentResponse)
        assert hasattr(response, "content")
        assert hasattr(response, "tool_calls")
        assert hasattr(response, "metadata")

    @pytest.mark.asyncio
    async def test_run_without_llm_provider(self, config, session_manager, memory_store, tool_registry):
        """测试未设置 LLM 提供商"""
        loop = AgentLoop(
            config=config,
            session_manager=session_manager,
            memory_store=memory_store,
            tool_registry=tool_registry,
        )
        # 不设置 LLM 提供商

        with pytest.raises(RuntimeError, match="LLM provider not set"):
            await loop.run(message="Hello", session_id="test")


# =============================================================================
# TestAgentLoopToolCalls - 工具调用测试
# =============================================================================


class TestAgentLoopToolCalls:
    """AgentLoop 工具调用测试"""

    @pytest.fixture
    def mock_llm_with_tool_call(self, mocker):
        """Mock LLM 返回工具调用"""
        mock_response = LLMResponse(
            content=None,
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "test_tool",
                        "arguments": {"query": "test query"},
                    },
                }
            ],
        )
        return mocker.patch(
            "providers.litellm_provider.MockLLMProvider.chat",
            return_value=mock_response,
        )

    @pytest.mark.asyncio
    async def test_run_with_single_tool_call(self, agent_loop, mocker):
        """测试单次工具调用"""
        # Mock LLM 返回工具调用
        mock_response = LLMResponse(
            content=None,
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": {"query": "test"}},
                }
            ],
        )

        # 第一次调用返回工具调用，第二次返回最终响应
        final_response = LLMResponse(content="Final response after tool execution")

        agent_loop._llm_provider.chat = AsyncMock(
            side_effect=[mock_response, final_response]
        )

        # Mock 工具执行
        agent_loop.tool_registry.execute = AsyncMock(return_value="Tool result")

        response = await agent_loop.run(
            message="Use test tool",
            session_id="test-session",
        )

        # 验证工具被调用
        assert agent_loop.tool_registry.execute.called
        assert response.metadata.get("iterations", 0) >= 1

    @pytest.mark.asyncio
    async def test_run_with_multiple_tool_calls(self, agent_loop, mocker):
        """测试多次工具调用"""
        # Mock LLM 返回多个工具调用
        mock_response = LLMResponse(
            content=None,
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": {"query": "test1"}},
                },
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": {"query": "test2"}},
                },
            ],
        )

        final_response = LLMResponse(content="Done")

        agent_loop._llm_provider.chat = AsyncMock(
            side_effect=[mock_response, final_response]
        )

        agent_loop.tool_registry.execute = AsyncMock(return_value="Result")

        response = await agent_loop.run(
            message="Use multiple tools",
            session_id="test-session",
        )

        # 验证工具被执行多次
        assert agent_loop.tool_registry.execute.call_count >= 2

    @pytest.mark.asyncio
    async def test_run_reaches_max_iterations(self, agent_loop, mocker):
        """测试达到最大迭代次数"""
        # Mock LLM 持续返回工具调用
        mock_response = LLMResponse(
            content=None,
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": "{}"},
                }
            ],
        )

        # 设置每次调用都返回工具调用
        agent_loop._llm_provider.chat = AsyncMock(return_value=mock_response)
        agent_loop.tool_registry.execute = AsyncMock(return_value="Result")

        # 设置很小的 max_iterations
        agent_loop.config.max_iterations = 3

        response = await agent_loop.run(
            message="Infinite loop test",
            session_id="test-session",
        )

        # 应该返回错误响应
        assert response.metadata.get("error") == "max_iterations"
        assert "达到最大迭代次数" in response.content


# =============================================================================
# TestAgentLoopMemory - 记忆系统测试
# =============================================================================


class TestAgentLoopMemory:
    """AgentLoop 记忆系统测试"""

    @pytest.mark.asyncio
    async def test_run_with_memory_enabled(self, agent_loop, memory_store):
        """测试启用记忆时运行"""
        # 先添加一些记忆
        await memory_store.update_memory("Important fact: Python is great")

        response = await agent_loop.run(
            message="What do you remember?",
            session_id="test-session",
        )

        assert isinstance(response, AgentResponse)
        # 验证会话被保存
        session = agent_loop.session_manager.get("test-session")
        assert session is not None

    @pytest.mark.asyncio
    async def test_run_consolidates_memory(self, agent_loop, session_manager, memory_store):
        """测试记忆整合（消息过多时）"""
        # 创建有很多消息的会话
        session = session_manager.get_or_create("long-session", "user-1")

        # 添加超过 50 条消息（使用 Message 对象）
        for i in range(55):
            session.add_message(Message(
                role="user",
                content=f"Message {i}",
                timestamp=datetime.now().isoformat(),
            ))
        session_manager.save(session)

        # Mock LLM 响应
        mock_response = LLMResponse(content="Response")
        agent_loop._llm_provider.chat = AsyncMock(return_value=mock_response)

        response = await agent_loop.run(
            message="Continue",
            session_id="long-session",
        )

        # 验证历史被追加到记忆
        history_content = memory_store.history_file.read_text(encoding="utf-8")
        assert "Message" in history_content


# =============================================================================
# TestAgentLoopEdgeCases - 边界条件测试
# =============================================================================


class TestAgentLoopEdgeCases:
    """AgentLoop 边界条件测试"""

    @pytest.mark.asyncio
    async def test_run_empty_message(self, agent_loop):
        """测试空消息"""
        response = await agent_loop.run(
            message="",
            session_id="test-session",
        )

        assert isinstance(response, AgentResponse)
        # 空消息也应该有响应
        assert response is not None

    @pytest.mark.asyncio
    async def test_run_very_long_message(self, agent_loop):
        """测试超长消息"""
        long_message = "a" * 10000

        response = await agent_loop.run(
            message=long_message,
            session_id="test-session",
        )

        assert isinstance(response, AgentResponse)
        assert response is not None

    @pytest.mark.asyncio
    async def test_run_special_characters(self, agent_loop):
        """测试特殊字符消息"""
        special_message = "Hello! @#$%^&*() 你好 🚀 \n\t\r"

        response = await agent_loop.run(
            message=special_message,
            session_id="test-session",
        )

        assert isinstance(response, AgentResponse)
        assert response is not None

    @pytest.mark.asyncio
    async def test_run_concurrent_sessions(self, agent_loop):
        """测试并发会话"""
        import asyncio

        async def run_session(session_id):
            return await agent_loop.run(
                message=f"Message for {session_id}",
                session_id=session_id,
            )

        # 并发运行多个会话
        results = await asyncio.gather(
            run_session("session-1"),
            run_session("session-2"),
            run_session("session-3"),
        )

        assert len(results) == 3
        assert all(isinstance(r, AgentResponse) for r in results)


# =============================================================================
# TestCreateAgentLoop - 便捷函数测试
# =============================================================================


class TestCreateAgentLoop:
    """create_agent_loop 函数测试"""

    @pytest.mark.asyncio
    async def test_create_agent_loop(self, config, mock_llm_provider):
        """测试创建 AgentLoop"""
        loop = await create_agent_loop(
            config=config,
            llm_provider=mock_llm_provider,
        )

        assert isinstance(loop, AgentLoop)
        assert loop._llm_provider is not None
        assert loop.config == config

    @pytest.mark.asyncio
    async def test_create_agent_loop_has_tools(self, config, mock_llm_provider):
        """测试创建的 AgentLoop 有工具"""
        loop = await create_agent_loop(
            config=config,
            llm_provider=mock_llm_provider,
        )

        # 验证有内置工具
        tools = loop.tool_registry.list_tools()
        assert len(tools) > 0
        # 应该包含文件工具
        assert any("file" in tool for tool in tools)


# =============================================================================
# TestAgentLoopIntegration - 简单集成测试
# =============================================================================


class TestAgentLoopIntegration:
    """AgentLoop 简单集成测试"""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, tmp_path, mock_llm_provider):
        """测试完整对话流程"""
        # 创建所有组件
        config = AgentConfig(model="mock-model", workspace=str(tmp_path))
        session_manager = SessionManager(storage_dir=tmp_path / "sessions")
        memory_store = MemoryStore(tmp_path)
        tool_registry = ToolRegistry()
        context_builder = ContextBuilder()

        # 创建 AgentLoop
        loop = AgentLoop(
            config=config,
            session_manager=session_manager,
            memory_store=memory_store,
            tool_registry=tool_registry,
            context_builder=context_builder,
        )
        loop.set_llm_provider(mock_llm_provider)

        # 第一轮对话
        response1 = await loop.run(
            message="Hello",
            session_id="conv-test",
        )
        assert isinstance(response1, AgentResponse)

        # 第二轮对话
        response2 = await loop.run(
            message="How are you?",
            session_id="conv-test",
        )
        assert isinstance(response2, AgentResponse)

        # 验证会话历史
        session = session_manager.get("conv-test")
        assert session is not None
        assert len(session.messages) == 4  # 2 轮对话

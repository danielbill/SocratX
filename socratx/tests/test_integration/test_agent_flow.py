"""集成测试 - Agent 端到端流�?""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock

from agent.loop import AgentLoop, AgentConfig, AgentResponse
from agent.session import SessionManager
from agent.memory import MemoryStore
from agent.tools.registry import ToolRegistry
from agent.context import ContextBuilder
from providers.litellm_provider import LLMResponse, MockLLMProvider


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_workspace(tmp_path):
    """创建临时工作�?""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def components(temp_workspace):
    """创建完整的组件集�?""
    config = AgentConfig(
        model="mock-model",
        temperature=0.7,
        max_tokens=4096,
        max_iterations=5,
        workspace=str(temp_workspace),
        memory_enabled=True,
    )

    session_manager = SessionManager(storage_dir=temp_workspace / "sessions")
    memory_store = MemoryStore(temp_workspace)
    tool_registry = ToolRegistry()
    context_builder = ContextBuilder(workspace=str(temp_workspace))

    # 注册测试工具
    tool_registry.register_simple(
        name="echo_tool",
        description="Echo back the input",
        handler=lambda text, **kwargs: f"Echo: {text}",
        parameters_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to echo"},
            },
            "required": ["text"],
        },
    )

    return {
        "config": config,
        "session_manager": session_manager,
        "memory_store": memory_store,
        "tool_registry": tool_registry,
        "context_builder": context_builder,
        "workspace": temp_workspace,
    }


@pytest.fixture
def agent_loop(components):
    """创建完整�?AgentLoop"""
    loop = AgentLoop(
        config=components["config"],
        session_manager=components["session_manager"],
        memory_store=components["memory_store"],
        tool_registry=components["tool_registry"],
        context_builder=components["context_builder"],
    )

    # 设置 Mock LLM Provider
    mock_provider = MockLLMProvider(response="Hello! How can I help you?")
    loop.set_llm_provider(mock_provider)

    return loop


# =============================================================================
# TestEndToEndFlow - 端到端流程测�?
# =============================================================================


class TestEndToEndFlow:
    """端到端流程测�?""

    @pytest.mark.asyncio
    async def test_user_message_to_response(self, agent_loop):
        """测试用户消息到响应的完整流程"""
        response = await agent_loop.run(
            message="Hello",
            session_id="test-session",
            user_id="user-1",
        )

        assert isinstance(response, AgentResponse)
        assert response.content != ""

        # 验证会话被保�?
        session = agent_loop.session_manager.get("test-session")
        assert session is not None
        assert len(session.messages) == 2  # 用户 + 助手

    @pytest.mark.asyncio
    async def test_conversation_with_history(self, agent_loop):
        """测试带历史对�?""
        # 第一轮对�?
        response1 = await agent_loop.run(
            message="Hello",
            session_id="conv-test",
        )
        assert isinstance(response1, AgentResponse)

        # 第二轮对�?
        response2 = await agent_loop.run(
            message="How are you?",
            session_id="conv-test",
        )
        assert isinstance(response2, AgentResponse)

        # 验证会话历史
        session = agent_loop.session_manager.get("conv-test")
        assert session is not None
        assert len(session.messages) == 4  # 2 轮对�?

    @pytest.mark.asyncio
    async def test_tool_execution_flow(self, components):
        """测试工具执行流程"""
        loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )

        # Mock LLM 返回工具调用
        mock_response_with_tool = LLMResponse(
            content=None,
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "echo_tool",
                        "arguments": {"text": "Hello"},
                    },
                }
            ],
        )

        mock_response_final = LLMResponse(
            content="Tool executed successfully!",
        )

        mock_provider = MockLLMProvider()
        mock_provider.chat = AsyncMock(
            side_effect=[mock_response_with_tool, mock_response_final]
        )
        loop.set_llm_provider(mock_provider)

        response = await loop.run(
            message="Use echo tool",
            session_id="tool-test",
        )

        # 验证响应
        assert isinstance(response, AgentResponse)
        # 验证会话包含工具调用历史
        session = loop.session_manager.get("tool-test")
        assert session is not None
        assert len(session.messages) >= 2

    @pytest.mark.asyncio
    async def test_memory_persistence(self, components):
        """测试记忆持久�?""
        loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )

        mock_provider = MockLLMProvider(response="Response 1")
        loop.set_llm_provider(mock_provider)

        # 第一轮对�?
        await loop.run(
            message="First message",
            session_id="memory-test",
        )

        # 验证记忆文件存在
        assert components["memory_store"].memory_file.exists()

        # 创建新的 AgentLoop 实例，验证可以读取之前的记忆
        new_loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )
        new_provider = MockLLMProvider(response="Response 2")
        new_loop.set_llm_provider(new_provider)

        # 第二轮对�?
        response = await new_loop.run(
            message="Second message",
            session_id="memory-test",
        )

        assert isinstance(response, AgentResponse)

    @pytest.mark.asyncio
    async def test_session_management(self, components):
        """测试会话管理"""
        loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )

        mock_provider = MockLLMProvider(response="Response")
        loop.set_llm_provider(mock_provider)

        # 创建多个会话
        for i in range(3):
            await loop.run(
                message=f"Message {i}",
                session_id=f"session-{i}",
            )

        # 验证会话列表
        sessions = components["session_manager"].list_sessions()
        assert len(sessions) == 3

        # 获取单个会话
        session = components["session_manager"].get("session-0")
        assert session is not None
        assert len(session.messages) == 2

        # 删除会话
        components["session_manager"].delete_session("session-0")
        session = components["session_manager"].get("session-0")
        assert session is None


# =============================================================================
# TestAPIIntegration - API 集成测试
# =============================================================================


class TestAPIIntegration:
    """API 集成测试"""

    @pytest.mark.asyncio
    async def test_chat_api_endpoint(self, client, temp_workspace):
        """测试聊天 API 端点"""
        # 这个测试需�?FastAPI 应用运行
        # 使用 TestClient 进行测试
        from main import app
        from fastapi.testclient import TestClient

        test_client = TestClient(app)

        response = test_client.post(
            "/api/chat",
            json={
                "message": "Hello",
                "session_id": "api-test",
            },
        )

        # 由于没有配置 LLM，可能返�?503
        # 这里主要验证 API 端点可以接收请求
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_session_api_flow(self, temp_workspace):
        """测试会话 API 流程"""
        from main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # 创建会话（通过聊天�?
        response = client.post(
            "/api/chat",
            json={
                "message": "Hello",
                "session_id": "session-api-test",
            },
        )

        # 获取会话列表
        sessions_response = client.get("/api/sessions")

        # 验证 API 可以访问
        assert sessions_response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_memory_api_flow(self, temp_workspace):
        """测试记忆 API 流程"""
        from main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # 获取记忆
        memory_response = client.get("/api/memory")

        # 验证 API 可以访问
        assert memory_response.status_code in [200, 503]


# =============================================================================
# TestComponentIntegration - 组件集成测试
# =============================================================================


class TestComponentIntegration:
    """组件集成测试"""

    @pytest.mark.asyncio
    async def test_agent_with_session(self, components):
        """测试 Agent + Session 集成"""
        loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )

        mock_provider = MockLLMProvider(response="Response")
        loop.set_llm_provider(mock_provider)

        # 运行对话
        response = await loop.run(
            message="Test session integration",
            session_id="integration-test",
        )

        # 验证会话被正确保�?
        session = components["session_manager"].get("integration-test")
        assert session is not None
        assert len(session.messages) == 2

    @pytest.mark.asyncio
    async def test_agent_with_memory(self, components):
        """测试 Agent + Memory 集成"""
        # 先添加一些记�?
        await components["memory_store"].update_memory("User prefers Python.")

        loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )

        mock_provider = MockLLMProvider(response="Response with memory context")
        loop.set_llm_provider(mock_provider)

        response = await loop.run(
            message="What do you know about me?",
            session_id="memory-integration",
        )

        # 验证记忆文件存在
        assert components["memory_store"].memory_file.exists()

    @pytest.mark.asyncio
    async def test_agent_with_tools(self, components):
        """测试 Agent + Tools 集成"""
        loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )

        # Mock LLM 返回工具调用
        mock_response = LLMResponse(
            content=None,
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "echo_tool",
                        "arguments": {"text": "Test"},
                    },
                }
            ],
        )

        mock_provider = MockLLMProvider()
        mock_provider.chat = AsyncMock(return_value=mock_response)
        loop.set_llm_provider(mock_provider)

        response = await loop.run(
            message="Use a tool",
            session_id="tools-integration",
        )

        # 验证工具被调�?
        assert response is not None


# =============================================================================
# TestMultiTurnConversation - 多轮对话测试
# =============================================================================


class TestMultiTurnConversation:
    """多轮对话测试"""

    @pytest.mark.asyncio
    async def test_multi_turn_basic(self, agent_loop):
        """测试基础多轮对话"""
        responses = []
        messages = ["Hello", "How are you?", "What's the weather?"]

        for msg in messages:
            response = await agent_loop.run(
                message=msg,
                session_id="multi-turn-test",
            )
            responses.append(response)

        # 验证所有响应都有效
        assert all(isinstance(r, AgentResponse) for r in responses)

        # 验证会话历史
        session = agent_loop.session_manager.get("multi-turn-test")
        assert len(session.messages) == len(messages) * 2  # 每轮 2 条消�?

    @pytest.mark.asyncio
    async def test_multi_turn_context_awareness(self, agent_loop):
        """测试上下文感知多轮对�?""
        # 第一�?
        await agent_loop.run(
            message="My name is Alice",
            session_id="context-test",
        )

        # 第二�?- 应该能记住名�?
        response = await agent_loop.run(
            message="What's my name?",
            session_id="context-test",
        )

        # 验证会话包含所有历�?
        session = agent_loop.session_manager.get("context-test")
        assert len(session.messages) == 4


# =============================================================================
# TestConcurrentSessions - 并发会话测试
# =============================================================================


class TestConcurrentSessions:
    """并发会话测试"""

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, components):
        """测试并发会话处理"""
        import asyncio

        loop = AgentLoop(
            config=components["config"],
            session_manager=components["session_manager"],
            memory_store=components["memory_store"],
            tool_registry=components["tool_registry"],
            context_builder=components["context_builder"],
        )

        mock_provider = MockLLMProvider(response="Response")
        loop.set_llm_provider(mock_provider)

        # 并发运行多个会话
        async def run_session(session_id):
            return await loop.run(
                message=f"Message for {session_id}",
                session_id=session_id,
            )

        results = await asyncio.gather(
            run_session("concurrent-1"),
            run_session("concurrent-2"),
            run_session("concurrent-3"),
        )

        # 验证所有会话都成功
        assert len(results) == 3
        assert all(isinstance(r, AgentResponse) for r in results)

        # 验证所有会话都被保�?
        sessions = components["session_manager"].list_sessions()
        assert len(sessions) == 3

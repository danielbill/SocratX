"""pytest 测试配置"""
import pytest
import sys
from pathlib import Path
from typing import Generator

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from main import app
from agent.loop import AgentLoop
from agent.memory import MemoryStore
from agent.session import SessionManager
import httpx


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """测试客户端"""
    client = TestClient(app)
    yield client
    client.close()


@pytest.fixture
def async_client() -> Generator[httpx.AsyncClient, None, None]:
    """异步测试客户端"""
    client = httpx.AsyncClient(base_url="http://test", timeout=5.0)
    yield client
    client.aclose()


@pytest.fixture
def agent_loop(tmp_path) -> AgentLoop:
    """Agent 循环实例"""
    return AgentLoop(model="openai/gpt-4o", base_dir=str(tmp_path))


@pytest.fixture
def memory_store(tmp_path) -> MemoryStore:
    """记忆存储实例"""
    return MemoryStore(base_dir=str(tmp_path))


@pytest.fixture
def session_manager(tmp_path) -> SessionManager:
    """会话管理器实例"""
    return SessionManager(storage_dir=tmp_path / "sessions")


@pytest.fixture
def mock_llm_response(mocker):
    """Mock LLM 响应"""
    return mocker.patch(
        'litellm.completion',
        return_value={
            'choices': [{
                'message': {'content': 'Mock response'}
            }]
        }
    )

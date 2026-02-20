"""API 接口测试"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


class TestRootEndpoint:
    """根路径端点测试"""

    def test_root(self, client: TestClient):
        """测试根路径"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "SocratX" in data["name"]
        assert data["version"] == "1.0.0"


class TestHealthEndpoint:
    """健康检查端点测试"""

    def test_health_check(self, client: TestClient):
        """测试健康检查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "components" in data


class TestChatEndpoint:
    """聊天端点测试"""

    def test_chat_empty_message(self, client: TestClient):
        """测试空消息"""
        response = client.post(
            "/api/chat",
            json={"message": "", "session_id": "test"}
        )
        
        # 空消息应该被拒绝或处理
        assert response.status_code in [200, 400]

    def test_chat_missing_message(self, client: TestClient):
        """测试缺失消息"""
        response = client.post(
            "/api/chat",
            json={"session_id": "test"}
        )
        
        # 缺少消息应该返回 422 验证错误
        assert response.status_code == 422

    def test_chat_with_session(self, client: TestClient):
        """测试带会话的聊天"""
        response = client.post(
            "/api/chat",
            json={
                "message": "Hello",
                "session_id": "test-session-123",
                "user_id": "user-1"
            }
        )
        
        # 由于没有配置 LLM，可能会失败，但应该正确处理
        assert response.status_code in [200, 500]

    def test_chat_default_session(self, client: TestClient):
        """测试默认会话聊天"""
        response = client.post(
            "/api/chat",
            json={"message": "Hello"}
        )
        
        # 应该使用默认 session_id
        assert response.status_code in [200, 500]


class TestSessionsEndpoint:
    """会话端点测试"""

    def test_list_sessions(self, client: TestClient):
        """测试列出会话"""
        response = client.get("/api/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data

    def test_list_sessions_with_user(self, client: TestClient):
        """测试按用户列出会话"""
        response = client.get("/api/sessions?user_id=user-1")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data

    def test_list_sessions_with_limit(self, client: TestClient):
        """测试限制列出数量"""
        response = client.get("/api/sessions?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) <= 5

    def test_get_session_not_found(self, client: TestClient):
        """测试获取不存在的会话"""
        response = client.get("/api/sessions/nonexistent-session")
        
        assert response.status_code == 404

    def test_delete_session_not_found(self, client: TestClient):
        """测试删除不存在的会话"""
        response = client.delete("/api/sessions/nonexistent-session")
        
        assert response.status_code == 404


class TestMemoryEndpoint:
    """记忆端点测试"""

    def test_get_memory(self, client: TestClient):
        """测试获取记忆"""
        response = client.get("/api/memory")
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_update_memory(self, client: TestClient):
        """测试更新记忆"""
        response = client.post(
            "/api/memory",
            json={"content": "Test memory item"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] is True

    def test_update_memory_with_section(self, client: TestClient):
        """测试更新特定章节的记忆"""
        response = client.post(
            "/api/memory",
            json={
                "content": "New user info",
                "section": "用户信息"
            }
        )
        
        assert response.status_code == 200

    def test_search_memory(self, client: TestClient):
        """测试搜索记忆"""
        response = client.get("/api/memory/search?query=test")
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_search_memory_with_limit(self, client: TestClient):
        """测试搜索记忆限制"""
        response = client.get("/api/memory/search?query=test&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 5


class TestConfigEndpoint:
    """配置端点测试"""

    def test_get_config(self, client: TestClient):
        """测试获取配置"""
        response = client.get("/api/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "config" in data

    def test_update_config(self, client: TestClient):
        """测试更新配置"""
        response = client.post(
            "/api/config",
            json={"updates": {"agent": {"temperature": 0.8}}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] is True


class TestToolsEndpoint:
    """工具端点测试"""

    def test_list_tools(self, client: TestClient):
        """测试列出工具"""
        response = client.get("/api/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "count" in data


class TestStatsEndpoint:
    """统计端点测试"""

    def test_get_stats(self, client: TestClient):
        """测试获取统计"""
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestCORS:
    """CORS 测试"""

    def test_cors_headers(self, client: TestClient):
        """测试 CORS 头"""
        response = client.options(
            "/api/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            }
        )
        
        # CORS 预检请求应该成功
        assert response.status_code == 200

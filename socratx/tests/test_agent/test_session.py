"""会话管理测试"""
import pytest
from datetime import datetime, timedelta
from agent.session import SessionManager, Session, Message


class TestSession:
    """Session 测试"""

    def test_create_session(self):
        """测试创建会话"""
        session = Session(id="test-123", user_id="user-1")
        
        assert session.id == "test-123"
        assert session.user_id == "user-1"
        assert len(session.messages) == 0
        assert session.created_at is not None

    def test_add_message(self):
        """测试添加消息"""
        session = Session(id="test-123", user_id="user-1")
        
        message = Message(
            role="user",
            content="Hello",
            timestamp=datetime.now().isoformat(),
        )
        session.add_message(message)
        
        assert len(session.messages) == 1
        assert session.messages[0].role == "user"
        assert session.messages[0].content == "Hello"

    def test_add_multiple_messages(self):
        """测试添加多条消息"""
        session = Session(id="test-123", user_id="user-1")
        
        for i in range(5):
            session.add_message(Message(
                role="user",
                content=f"Message {i}",
                timestamp=datetime.now().isoformat(),
            ))
        
        assert len(session.messages) == 5

    def test_to_dict(self):
        """测试转换为字�?""
        session = Session(id="test-123", user_id="user-1")
        session.add_message(Message(
            role="user",
            content="Test",
            timestamp=datetime.now().isoformat(),
        ))
        
        data = session.to_dict()
        
        assert data["id"] == "test-123"
        assert data["user_id"] == "user-1"
        assert len(data["messages"]) == 1
        assert "created_at" in data

    def test_is_expired(self):
        """测试会话过期检�?""
        # 未过�?
        session = Session(
            id="test-123",
            user_id="user-1",
            created_at=datetime.now(),
        )
        assert not session.is_expired()
        
        # 已过期（1 小时前创建，TTL �?0�?
        expired_session = Session(
            id="test-456",
            user_id="user-1",
            created_at=datetime.now() - timedelta(hours=1),
            ttl=0,
        )
        assert expired_session.is_expired()

    def test_get_last_message(self):
        """测试获取最后一条消�?""
        session = Session(id="test-123", user_id="user-1")
        
        session.add_message(Message(
            role="user",
            content="First",
            timestamp=datetime.now().isoformat(),
        ))
        session.add_message(Message(
            role="assistant",
            content="Second",
            timestamp=datetime.now().isoformat(),
        ))
        
        last_msg = session.get_last_message()
        assert last_msg is not None
        assert last_msg.content == "Second"

    def test_get_last_message_empty(self):
        """测试空会话获取最后消�?""
        session = Session(id="test-123", user_id="user-1")
        
        last_msg = session.get_last_message()
        assert last_msg is None


class TestSessionManager:
    """SessionManager 测试"""

    @pytest.fixture
    def session_manager(self, tmp_path) -> SessionManager:
        """创建测试用的 SessionManager"""
        return SessionManager(base_dir=str(tmp_path))

    def test_get_or_create_new(self, session_manager: SessionManager):
        """测试获取或创建新会话"""
        session = session_manager.get_or_create("new-session", "user-1")
        
        assert session is not None
        assert session.id == "new-session"
        assert session.user_id == "user-1"

    def test_get_or_create_existing(self, session_manager: SessionManager):
        """测试获取已存在的会话"""
        # 先创�?
        session_manager.get_or_create("test-session", "user-1")
        
        # 再获�?
        session = session_manager.get_or_create("test-session", "user-1")
        
        assert session is not None
        assert session.id == "test-session"

    def test_get(self, session_manager: SessionManager):
        """测试获取会话"""
        session_manager.get_or_create("test-123", "user-1")
        
        session = session_manager.get("test-123")
        assert session is not None
        assert session.id == "test-123"

    def test_get_not_found(self, session_manager: SessionManager):
        """测试获取不存在的会话"""
        session = session_manager.get("nonexistent")
        assert session is None

    def test_delete_session(self, session_manager: SessionManager):
        """测试删除会话"""
        session_manager.get_or_create("test-123", "user-1")
        
        success = session_manager.delete_session("test-123")
        assert success is True
        
        # 验证已删�?
        session = session_manager.get("test-123")
        assert session is None

    def test_delete_session_not_found(self, session_manager: SessionManager):
        """测试删除不存在的会话"""
        success = session_manager.delete_session("nonexistent")
        assert success is False

    def test_list_sessions(self, session_manager: SessionManager):
        """测试列出会话"""
        # 创建多个会话
        for i in range(5):
            session_manager.get_or_create(f"session-{i}", "user-1")
        
        sessions = session_manager.list_sessions()
        assert len(sessions) == 5

    def test_list_sessions_by_user(self, session_manager: SessionManager):
        """测试按用户列出会�?""
        # 创建不同用户的会�?
        session_manager.get_or_create("session-u1-1", "user-1")
        session_manager.get_or_create("session-u1-2", "user-1")
        session_manager.get_or_create("session-u2-1", "user-2")
        
        sessions = session_manager.list_sessions(user_id="user-1")
        assert len(sessions) == 2
        assert all(s.user_id == "user-1" for s in sessions)

    def test_list_sessions_limit(self, session_manager: SessionManager):
        """测试列出会话限制"""
        for i in range(10):
            session_manager.get_or_create(f"session-{i}", "user-1")
        
        sessions = session_manager.list_sessions(limit=5)
        assert len(sessions) == 5

    def test_save_session(self, session_manager: SessionManager):
        """测试保存会话"""
        session = session_manager.get_or_create("test-123", "user-1")
        session.add_message(Message(
            role="user",
            content="Test message",
            timestamp=datetime.now().isoformat(),
        ))
        
        session_manager.save(session)
        
        # 验证文件存在
        session_file = session_manager.base_dir / "sessions" / "test-123.jsonl"
        assert session_file.exists()

    def test_load_session(self, session_manager: SessionManager):
        """测试加载会话"""
        # 创建并保�?
        session = session_manager.get_or_create("test-123", "user-1")
        session.add_message(Message(
            role="user",
            content="Test",
            timestamp=datetime.now().isoformat(),
        ))
        session_manager.save(session)
        
        # 清除缓存
        session_manager._sessions.clear()
        
        # 重新加载
        session = session_manager.get("test-123")
        assert session is not None
        assert len(session.messages) == 1

    def test_get_stats(self, session_manager: SessionManager):
        """测试获取统计信息"""
        # 创建多个会话
        for i in range(3):
            session_manager.get_or_create(f"session-{i}", "user-1")
        
        stats = session_manager.get_stats()
        
        assert "total_sessions" in stats
        assert stats["total_sessions"] >= 3

    def test_cleanup_expired(self, session_manager: SessionManager):
        """测试清理过期会话"""
        # 创建过期会话
        from datetime import timedelta
        expired_session = Session(
            id="expired-123",
            user_id="user-1",
            created_at=datetime.now() - timedelta(hours=2),
            ttl=3600,  # 1 小时 TTL
        )
        session_manager._sessions["expired-123"] = expired_session
        
        # 清理
        session_manager.cleanup_expired()
        
        # 验证已清�?
        assert "expired-123" not in session_manager._sessions

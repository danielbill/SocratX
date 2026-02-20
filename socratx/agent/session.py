"""
SessionManager - 会话管理器

参考: socrats/socrats/session/manager.py
负责会话的创建、持久化和检索
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
import threading
import hashlib


@dataclass
class Message:
    """消息数据类"""

    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    timestamp: str = ""
    metadata: dict = field(default_factory=dict)
    tool_calls: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """从字典创建"""
        return cls(**data)


@dataclass
class Session:
    """会话数据类"""

    id: str
    user_id: str
    messages: list[Message] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def add_message(self, message: Message) -> None:
        """添加消息到会话"""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """从字典创建"""
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            messages=messages,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            metadata=data.get("metadata", {}),
        )


class SessionManager:
    """
    会话管理器

    负责会话的持久化存储和检索，使用 JSONL 格式
    """

    def __init__(self, storage_dir: Optional[Path | str] = None):
        """
        初始化会话管理器

        Args:
            storage_dir: 会话存储目录，默认为 ~/.socratx/sessions/
        """
        if storage_dir is None:
            home = Path.home()
            storage_dir = home / ".socratx" / "sessions"
        else:
            storage_dir = Path(storage_dir)

        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存
        self._cache: dict[str, Session] = {}
        self._lock = threading.Lock()

    def _get_session_path(self, session_id: str) -> Path:
        """获取会话文件路径"""
        return self.storage_dir / f"{session_id}.jsonl"

    def _generate_session_id(self, user_id: str) -> str:
        """生成唯一的会话 ID"""
        timestamp = datetime.now().isoformat()
        content = f"{user_id}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_or_create(
        self,
        session_id: Optional[str] = None,
        user_id: str = "default",
    ) -> Session:
        """
        获取或创建会话

        Args:
            session_id: 会话 ID，如果为 None 则创建新会话
            user_id: 用户 ID

        Returns:
            Session 对象
        """
        with self._lock:
            # 如果没有提供 session_id，创建新会话
            if session_id is None:
                session_id = self._generate_session_id(user_id)
                session = Session(id=session_id, user_id=user_id)
                self._cache[session_id] = session
                self._save_session(session)
                return session

            # 尝试从缓存获取
            if session_id in self._cache:
                return self._cache[session_id]

            # 从磁盘加载
            session = self._load_session(session_id)
            if session is None:
                # 会话不存在，创建新会话
                session = Session(id=session_id, user_id=user_id)

            self._cache[session_id] = session
            return session

    def get(self, session_id: str) -> Optional[Session]:
        """
        获取会话

        Args:
            session_id: 会话 ID

        Returns:
            Session 对象，如果不存在则返回 None
        """
        with self._lock:
            if session_id in self._cache:
                return self._cache[session_id]

            return self._load_session(session_id)

    def save(self, session: Session) -> None:
        """
        保存会话

        Args:
            session: 要保存的会话
        """
        with self._lock:
            session.updated_at = datetime.now().isoformat()
            self._cache[session.id] = session
            self._save_session(session)

    def _save_session(self, session: Session) -> None:
        """保存会话到磁盘"""
        session_path = self._get_session_path(session.id)

        # 追加模式写入 JSONL
        with open(session_path, "a", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, ensure_ascii=False)
            f.write("\n")

    def _load_session(self, session_id: str) -> Optional[Session]:
        """从磁盘加载会话"""
        session_path = self._get_session_path(session_id)

        if not session_path.exists():
            return None

        try:
            # 读取最后一行（最新的会话状态）
            with open(session_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines:
                    return None

                last_line = lines[-1].strip()
                data = json.loads(last_line)
                return Session.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[Session]:
        """
        列出会话

        Args:
            user_id: 用户 ID，如果为 None 则返回所有用户的会话
            limit: 最大返回数量

        Returns:
            会话列表，按更新时间降序
        """
        sessions = []

        for session_file in self.storage_dir.glob("*.jsonl"):
            try:
                session = self._load_session(session_file.stem)
                if session:
                    if user_id is None or session.user_id == user_id:
                        sessions.append(session)
            except Exception as e:
                print(f"Error loading session file {session_file}: {e}")
                continue

        # 按更新时间降序排序
        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        return sessions[:limit]

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话 ID

        Returns:
            是否成功删除
        """
        with self._lock:
            # 从缓存移除
            if session_id in self._cache:
                del self._cache[session_id]

            # 删除文件
            session_path = self._get_session_path(session_id)
            if session_path.exists():
                session_path.unlink()
                return True

            return False

    def clear_cache(self) -> None:
        """清空内存缓存"""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> dict:
        """获取统计信息"""
        session_files = list(self.storage_dir.glob("*.jsonl"))

        total_messages = 0
        for session_file in session_files:
            session = self._load_session(session_file.stem)
            if session:
                total_messages += len(session.messages)

        return {
            "total_sessions": len(session_files),
            "cached_sessions": len(self._cache),
            "total_messages": total_messages,
            "storage_dir": str(self.storage_dir),
        }

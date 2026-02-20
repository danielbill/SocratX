"""
SocratX 统一日志系统

提供三个日志通道：
- system: 系统信息 → logs/SocratX.log
- conversation: 对话内容 → logs/conversation.log
- ai: AI 交互 → logs/ai.log
"""

import logging
from pathlib import Path
from datetime import datetime


class SocratXLogger:
    """统一日志系统单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._setup_loggers()

    def _setup_loggers(self):
        """设置三个日志通道"""
        # 日志目录
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # 通用格式
        default_format = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 对话格式
        conversation_format = logging.Formatter(
            "[%(asctime)s] [SESSION:%(sessionid)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # AI 格式
        ai_format = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 1. 系统日志 → SocratX.log
        self._system_logger = logging.getLogger("socratx.system")
        self._system_logger.setLevel(logging.INFO)
        self._system_logger.propagate = False
        system_handler = logging.FileHandler(log_dir / "SocratX.log", encoding="utf-8")
        system_handler.setFormatter(default_format)
        self._system_logger.addHandler(system_handler)

        # 2. 对话日志 → conversation.log
        self._conversation_logger = logging.getLogger("socratx.conversation")
        self._conversation_logger.setLevel(logging.INFO)
        self._conversation_logger.propagate = False
        conversation_handler = logging.FileHandler(log_dir / "conversation.log", encoding="utf-8")
        conversation_handler.setFormatter(conversation_format)
        self._conversation_logger.addHandler(conversation_handler)

        # 3. AI 日志 → ai.log
        self._ai_logger = logging.getLogger("socratx.ai")
        self._ai_logger.setLevel(logging.DEBUG)
        self._ai_logger.propagate = False
        ai_handler = logging.FileHandler(log_dir / "ai.log", encoding="utf-8")
        ai_handler.setFormatter(ai_format)
        self._ai_logger.addHandler(ai_handler)

    def system(self, msg: str):
        """系统日志"""
        self._system_logger.info(msg)

    def conversation(self, session_id: str, role: str, content: str):
        """
        对话日志

        Args:
            session_id: 会话 ID
            role: 角色 (USER/AI/SYSTEM)
            content: 内容
        """
        extra = {"sessionid": session_id}
        self._conversation_logger.info(f"[{role}] {content}", extra=extra)

    def ai_request(self, model: str, messages: list):
        """
        AI 请求日志

        Args:
            model: 模型名称
            messages: 消息列表
        """
        msg_preview = str(messages)[:200] + "..." if len(str(messages)) > 200 else str(messages)
        self._ai_logger.info(f"[REQUEST] Model: {model} | Messages: {msg_preview}")

    def ai_response(self, content: str, usage: dict = None):
        """
        AI 响应日志

        Args:
            content: 响应内容
            usage: Token 使用情况
        """
        usage_str = f" | Usage: {usage}" if usage else ""
        content_preview = content[:100] + "..." if len(content) > 100 else content
        self._ai_logger.info(f"[RESPONSE] {content_preview}{usage_str}")

    def error(self, msg: str, exc: Exception = None):
        """错误日志"""
        if exc:
            self._system_logger.error(f"{msg}: {exc}", exc_info=True)
        else:
            self._system_logger.error(msg)


# 全局单例
logger = SocratXLogger()

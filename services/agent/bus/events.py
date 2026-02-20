"""
Message Bus Events - 消息事件定义

参考: nanobot/nanobot/bus/events.py
定义入站和出站消息的数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, List
from enum import Enum


class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"
    SYSTEM = "system"
    COMMAND = "command"
    TOOL_RESULT = "tool_result"


@dataclass
class InboundMessage:
    """
    入站消息

    从外部源（如 UI）进入系统的消息
    """

    channel: str  # 来源渠道
    sender_id: str  # 发送者 ID
    chat_id: str  # 聊天 ID
    content: str  # 消息内容
    message_type: MessageType = MessageType.TEXT
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    media: Optional[List[str]] = None  # 附件（图片、文件等）
    metadata: dict = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "channel": self.channel,
            "sender_id": self.sender_id,
            "chat_id": self.chat_id,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
            "media": self.media,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InboundMessage":
        """从字典创建"""
        return cls(
            channel=data["channel"],
            sender_id=data["sender_id"],
            chat_id=data["chat_id"],
            content=data["content"],
            message_type=MessageType(data.get("message_type", MessageType.TEXT)),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            media=data.get("media"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class OutboundMessage:
    """
    出站消息

    从系统发送到外部目标（如 UI）的消息
    """

    channel: str  # 目标渠道
    chat_id: str  # 聊天 ID
    content: str  # 消息内容
    message_type: MessageType = MessageType.TEXT
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reply_to: Optional[str] = None  # 回复的消息 ID
    media: Optional[List[str]] = None  # 附件
    metadata: dict = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "channel": self.channel,
            "chat_id": self.chat_id,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
            "reply_to": self.reply_to,
            "media": self.media,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OutboundMessage":
        """从字典创建"""
        return cls(
            channel=data["channel"],
            chat_id=data["chat_id"],
            content=data["content"],
            message_type=MessageType(data.get("message_type", MessageType.TEXT)),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            reply_to=data.get("reply_to"),
            media=data.get("media"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class StreamChunk:
    """
    流式消息块

    用于流式输出的部分消息
    """

    chat_id: str
    content: str
    is_final: bool = False  # 是否是最后一块
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "chat_id": self.chat_id,
            "content": self.content,
            "is_final": self.is_final,
            "timestamp": self.timestamp,
        }

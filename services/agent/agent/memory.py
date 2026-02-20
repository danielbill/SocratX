"""
MemoryStore - 记忆存储系统

参考: nanobot/nanobot/agent/memory.py
双层记忆系统：MEMORY.md (长期事实) + HISTORY.md (对话日志)
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional


class MemoryStore:
    """
    记忆存储系统

    实现双层记忆：
    - MEMORY.md: 长期事实记忆（用户信息、偏好、重要知识）
    - HISTORY.md: 可搜索的对话历史日志
    """

    def __init__(self, workspace: Optional[Path | str] = None):
        """
        初始化记忆存储

        Args:
            workspace: 工作区路径，默认为当前目录
        """
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.memory_file = self.workspace / "MEMORY.md"
        self.history_file = self.workspace / "HISTORY.md"

        # 确保文件存在
        self._ensure_files()

    def _ensure_files(self) -> None:
        """确保记忆文件存在"""
        if not self.memory_file.exists():
            self.memory_file.write_text(
                "# SocratX 记忆\n\n"
                "这是 SocratX 的长期记忆文件，用于存储重要事实和用户偏好。\n\n"
                "## 用户信息\n\n"
                "## 重要知识\n\n"
                "## 偏好设置\n\n",
                encoding="utf-8",
            )

        if not self.history_file.exists():
            self.history_file.write_text(
                "# SocratX 对话历史\n\n"
                "这是 SocratX 的对话历史日志，可被搜索和引用。\n\n"
                "---\n\n",
                encoding="utf-8",
            )

    async def get_memory(self) -> str:
        """
        获取长期记忆内容

        Returns:
            MEMORY.md 的内容
        """
        return self.memory_file.read_text(encoding="utf-8")

    async def update_memory(self, content: str, section: Optional[str] = None) -> None:
        """
        更新长期记忆

        Args:
            content: 要添加的内容
            section: 目标章节，如果为 None 则追加到末尾
        """
        current = await self.get_memory()

        if section:
            # 更新特定章节
            section_marker = f"## {section}"
            if section_marker in current:
                # 章节存在，追加内容
                parts = current.split(section_marker)
                if len(parts) >= 2:
                    before = parts[0]
                    after_parts = parts[1].split("##", 1)
                    section_content = after_parts[0]
                    after = after_parts[1] if len(after_parts) > 1 else ""

                    # 更新章节内容
                    new_content = section_content.rstrip() + f"\n\n- {content}\n"
                    new_memory = f"{before}{section_marker}{new_content}"
                    if after:
                        new_memory += f"##{after}"
                    current = new_memory
                else:
                    current += f"\n\n{section_marker}\n- {content}\n"
            else:
                # 章节不存在，创建新章节
                current += f"\n\n{section_marker}\n- {content}\n"
        else:
            # 追加到末尾
            current += f"\n- {content}\n"

        self.memory_file.write_text(current, encoding="utf-8")

    async def append_to_history(self, messages: list) -> None:
        """
        追加对话历史

        Args:
            messages: 消息列表，每个消息需要有 role 和 content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"\n## {timestamp}\n\n"

        for msg in messages:
            # 支持 Message 对象和字典
            if hasattr(msg, 'role'):
                role = msg.role
                content = msg.content
            else:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")

            if role == "user":
                entry += f"**用户**: {content}\n\n"
            elif role == "assistant":
                entry += f"**助手**: {content}\n\n"
            elif role == "system":
                entry += f"*系统*: {content}\n\n"
            elif role == "tool":
                entry += f"*工具*: {content}\n\n"

        entry += "---\n"

        # 追加到历史文件
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(entry)

    async def search_history(self, query: str, limit: int = 10) -> list[str]:
        """
        搜索对话历史

        Args:
            query: 搜索关键词
            limit: 最大返回结果数

        Returns:
            匹配的段落列表
        """
        content = self.history_file.read_text(encoding="utf-8")

        # 简单的关键词搜索（可以升级为更智能的搜索）
        results = []
        query_lower = query.lower()

        # 按段落分割
        paragraphs = content.split("\n\n")

        for para in paragraphs:
            if query_lower in para.lower():
                results.append(para.strip())
                if len(results) >= limit:
                    break

        return results

    async def get_recent_history(self, count: int = 5) -> list[str]:
        """
        获取最近的对话历史

        Args:
            count: 获取的段落数

        Returns:
            最近的对话段落列表
        """
        content = self.history_file.read_text(encoding="utf-8")

        # 按段落分割并获取最后 N 个
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        # 返回最近的段落（排除标题和分隔符）
        recent = []
        for para in reversed(paragraphs):
            if para and not para.startswith("#") and para != "---":
                recent.append(para)
                if len(recent) >= count:
                    break

        return list(reversed(recent))

    def clear_memory(self) -> None:
        """清空长期记忆（重置为默认内容）"""
        self.memory_file.write_text(
            "# SocratX 记忆\n\n"
            "这是 SocratX 的长期记忆文件，用于存储重要事实和用户偏好。\n\n"
            "## 用户信息\n\n"
            "## 重要知识\n\n"
            "## 偏好设置\n\n",
            encoding="utf-8",
        )

    def clear_history(self) -> None:
        """清空对话历史（重置为默认内容）"""
        self.history_file.write_text(
            "# SocratX 对话历史\n\n"
            "这是 SocratX 的对话历史日志，可被搜索和引用。\n\n"
            "---\n\n",
            encoding="utf-8",
        )

    def get_stats(self) -> dict:
        """获取记忆统计信息"""
        memory_content = self.memory_file.read_text(encoding="utf-8")
        history_content = self.history_file.read_text(encoding="utf-8")

        return {
            "memory_file": str(self.memory_file),
            "history_file": str(self.history_file),
            "memory_size": len(memory_content),
            "history_size": len(history_content),
            "memory_entries": memory_content.count("\n## "),
            "history_entries": history_content.count("\n## "),
        }


# 便捷函数
async def create_memory_store(workspace: str = "") -> MemoryStore:
    """
    创建 MemoryStore 的便捷函数

    Args:
        workspace: 工作区路径

    Returns:
        MemoryStore 实例
    """
    return MemoryStore(workspace or "")

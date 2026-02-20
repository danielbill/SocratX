"""
ContextBuilder - 系统提示词构建器

参考: nanobot/nanobot/agent/context.py
负责构建发送给 LLM 的完整上下文，包括系统提示词、历史消息、记忆等
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .session import Message


class ContextBuilder:
    """
    系统提示词构建器

    从以下来源构建完整的 LLM 上下文：
    1. 身份信息（时间、运行时、工作区）
    2. 系统提示词（从引导文件加载）
    3. 长期记忆（MEMORY.md）
    4. 历史消息
    5. 可用工具列表
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        workspace: str = "",
        agent_name: str = "SocratX",
    ):
        self.agent_name = agent_name
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.custom_system_prompt = system_prompt

        # 引导文件路径
        self.guidance_files = {
            "AGENTS.md": "agents.md",
            "SOUL.md": "soul.md",
            "USER.md": "user.md",
        }

    async def build(
        self,
        messages: list[Message],
        memory: str = "",
        tools: list[str] = [],
        workspace: str = "",
    ) -> list[dict]:
        """
        构建完整的 LLM 上下文

        Args:
            messages: 历史消息列表
            memory: 长期记忆内容
            tools: 可用工具摘要列表
            workspace: 工作区路径

        Returns:
            格式化的消息列表，可直接传给 LLM
        """
        # 构建系统提示词
        system_prompt = await self._build_system_prompt(
            memory=memory,
            tools=tools,
            workspace=workspace,
        )

        # 构建上下文消息列表
        context_messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 添加历史消息（限制数量以控制 token 使用）
        max_history = 50
        recent_messages = messages[-max_history:] if len(messages) > max_history else messages

        for msg in recent_messages:
            context_messages.append({
                "role": msg.role,
                "content": msg.content,
            })

        return context_messages

    async def _build_system_prompt(
        self,
        memory: str = "",
        tools: list[str] = [],
        workspace: str = "",
    ) -> str:
        """
        构建系统提示词

        Args:
            memory: 长期记忆内容
            tools: 可用工具摘要
            workspace: 工作区路径

        Returns:
            完整的系统提示词
        """
        parts = []

        # 1. 身份信息
        parts.append(self._build_identity())

        # 2. 自定义系统提示词（如果有）
        if self.custom_system_prompt:
            parts.append(f"\n{self.custom_system_prompt}")

        # 3. 引导文件内容
        guidance = await self._load_guidance_files()
        if guidance:
            parts.append(f"\n{guidance}")

        # 4. 工作区信息
        if workspace:
            parts.append(self._build_workspace_info(workspace))

        # 5. 长期记忆
        if memory:
            parts.append(f"\n## 长期记忆\n{memory}")

        # 6. 可用工具
        if tools:
            parts.append(f"\n## 可用工具\n{self._format_tools(tools)}")

        # 7. 行为指南
        parts.append(self._build_behavior_guide())

        return "\n".join(parts)

    def _build_identity(self) -> str:
        """构建身份信息"""
        now = datetime.now()
        return f"""# {self.agent_name}

你是 {self.agent_name}，一个智能 AI 助手。

**当前时间**: {now.strftime("%Y-%m-%d %H:%M:%S")}
**运行环境**: Python
**工作目录**: {self.workspace}

## 行为准则
- 使用简洁的中文回复
- 首次问候时回复"你好，我是 SocratX"
- 专业、友好、直接
"""

    async def _load_guidance_files(self) -> str:
        """
        加载引导文件内容

        按优先级加载 AGENTS.md -> SOUL.md -> USER.md

        Returns:
            引导文件内容，如果都不存在则返回空字符串
        """
        for name, filename in self.guidance_files.items():
            file_path = self.workspace / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                return f"\n## 来自 {name}\n{content}"
        return ""

    def _build_workspace_info(self, workspace: str) -> str:
        """构建工作区信息"""
        workspace_path = Path(workspace)

        parts = [f"\n## 工作区\n路径: {workspace}"]

        # 列出工作区中的关键文件/目录
        if workspace_path.exists():
            try:
                items = []
                for item in workspace_path.iterdir():
                    if not item.name.startswith("."):
                        prefix = "📁" if item.is_dir() else "📄"
                        items.append(f"  {prefix} {item.name}")

                if items:
                    parts.append("```\n" + "\n".join(items) + "\n```")
            except PermissionError:
                parts.append("(无法访问工作区)")

        return "\n".join(parts)

    def _format_tools(self, tools: list[str]) -> str:
        """格式化工具列表"""
        if not tools:
            return "无可用工具"

        return "\n".join(f"- {tool}" for tool in tools)

    def _build_behavior_guide(self) -> str:
        """构建行为指南"""
        return """
## 行为指南

1. **清晰简洁**: 回答要直接、准确，避免冗余
2. **使用工具**: 在需要时主动使用可用工具完成任务
3. **承认不确定性**: 对于不确定的信息，明确说明
4. **保护隐私**: 不要重复存储在记忆中的敏感信息
5. **上下文感知**: 根据对话历史和记忆提供连贯的回答

## 工具使用规则

- 在执行文件操作前，先确认路径的正确性
- Shell 命令执行要谨慎，避免破坏性操作
- 网络搜索时使用准确的关键词
- 如果工具执行失败，尝试分析原因并重试或寻找替代方案
"""


class ContextBuilderConfig:
    """
    ContextBuilder 配置

    用于简化 ContextBuilder 的创建
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        workspace: str = "",
        agent_name: str = "SocratX",
        enable_guidance_files: bool = True,
        max_history: int = 50,
    ):
        self.system_prompt = system_prompt
        self.workspace = workspace
        self.agent_name = agent_name
        self.enable_guidance_files = enable_guidance_files
        self.max_history = max_history

    def build(self) -> ContextBuilder:
        """创建 ContextBuilder 实例"""
        return ContextBuilder(
            system_prompt=self.system_prompt,
            workspace=self.workspace,
            agent_name=self.agent_name,
        )


# 默认系统提示词模板
DEFAULT_SYSTEM_PROMPT = """你是 SocratX，一个由 AI 驱动的智能助手。

你的使命是帮助用户高效地完成各种任务，包括但不限于：
- 编写和分析代码
- 回答技术问题
- 执行系统命令
- 搜索和整理信息
- 管理文件和目录

你拥有多种工具来辅助完成任务，请根据需要合理使用。

始终保持友好、专业和高效的服务态度。"""


# 便捷函数
async def create_context_builder(
    workspace: str = "",
    system_prompt: Optional[str] = None,
) -> ContextBuilder:
    """
    创建 ContextBuilder 的便捷函数

    Args:
        workspace: 工作区路径
        system_prompt: 自定义系统提示词

    Returns:
        ContextBuilder 实例
    """
    return ContextBuilder(
        system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        workspace=workspace,
    )

"""
AgentLoop - 核心代理处理引擎

参考: nanobot/nanobot/agent/loop.py
实现迭代的 LLM + 工具执行循环
"""

import asyncio
from datetime import datetime
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from collections import deque

from .context import ContextBuilder
from .session import SessionManager, Session, Message
from .memory import MemoryStore
from .tools.registry import ToolRegistry


@dataclass
class AgentConfig:
    """代理配置"""

    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096
    max_iterations: int = 20  # 最大工具调用迭代次数
    workspace: str = ""  # 工作区路径

    # 记忆配置
    memory_enabled: bool = True
    memory_file: str = "MEMORY.md"
    history_file: str = "HISTORY.md"

    # 会话配置
    session_ttl: int = 86400  # 会话过期时间（秒）


@dataclass
class AgentResponse:
    """代理响应"""

    content: str
    tool_calls: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)


class AgentLoop:
    """
    核心代理处理引擎

    负责处理用户消息，执行 LLM 循环，调用工具，生成响应
    """

    def __init__(
        self,
        config: AgentConfig,
        session_manager: SessionManager,
        memory_store: MemoryStore,
        tool_registry: ToolRegistry,
        context_builder: Optional[ContextBuilder] = None,
    ):
        self.config = config
        self.session_manager = session_manager
        self.memory_store = memory_store
        self.tool_registry = tool_registry
        self.context_builder = context_builder or ContextBuilder()

        # LLM 提供商（延迟初始化）
        self._llm_provider: Optional[Any] = None

    def set_llm_provider(self, provider: Any) -> None:
        """设置 LLM 提供商"""
        self._llm_provider = provider

    async def run(
        self,
        message: str,
        session_id: str,
        user_id: str = "default",
    ) -> AgentResponse:
        """
        处理用户消息的主入口

        Args:
            message: 用户消息
            session_id: 会话 ID
            user_id: 用户 ID

        Returns:
            AgentResponse: 代理响应
        """
        # 获取或创建会话
        session = self.session_manager.get_or_create(session_id, user_id)

        # 添加用户消息到会话
        user_msg = Message(role="user", content=message, timestamp=datetime.now().isoformat())
        session.add_message(user_msg)

        # 检查是否需要整合记忆（消息过多时）
        if len(session.messages) > 50:
            await self._consolidate_memory(session)

        # 构建上下文
        context_messages = await self._build_context(session)

        # 运行代理循环
        response = await self._run_agent_loop(context_messages)

        # 添加助手响应到会话
        assistant_msg = Message(
            role="assistant",
            content=response.content,
            timestamp=datetime.now().isoformat(),
            metadata={"tool_calls": response.tool_calls},
        )
        session.add_message(assistant_msg)

        # 保存会话
        self.session_manager.save(session)

        return response

    async def _run_agent_loop(self, messages: list[dict]) -> AgentResponse:
        """
        迭代的 LLM + 工具执行循环

        Args:
            messages: 上下文消息列表

        Returns:
            AgentResponse: 最终响应
        """
        messages = messages.copy()  # 避免修改原列表
        tool_results: list[dict] = []
        all_tool_calls: list[dict] = []

        for iteration in range(self.config.max_iterations):
            # 获取可用工具的 schema
            tools = self.tool_registry.get_tool_schemas()

            # 调用 LLM
            llm_response = await self._call_llm(messages, tools)

            # 检查是否有工具调用
            if llm_response.tool_calls:
                all_tool_calls.extend(llm_response.tool_calls)

                # 并行执行所有工具调用
                results = await self._execute_tools_parallel(llm_response.tool_calls)
                tool_results.extend(results)

                # 将工具调用和结果添加到消息列表
                for tool_call, result in zip(llm_response.tool_calls, results):
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call],
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result["content"],
                    })

                # 继续循环，获取 LLM 的下一步响应
                continue
            else:
                # 没有工具调用，返回最终响应
                return AgentResponse(
                    content=llm_response.content,
                    tool_calls=all_tool_calls,
                    metadata={"iterations": iteration + 1},
                )

        # 达到最大迭代次数
        return AgentResponse(
            content="达到最大迭代次数，任务可能未完成。",
            tool_calls=all_tool_calls,
            metadata={"iterations": self.config.max_iterations, "error": "max_iterations"},
        )

    async def _call_llm(self, messages: list[dict], tools: list[dict]) -> Any:
        """
        调用 LLM 提供商

        Args:
            messages: 消息列表
            tools: 工具 schema 列表

        Returns:
            LLM 响应对象
        """
        if self._llm_provider is None:
            raise RuntimeError("LLM provider not set. Call set_llm_provider() first.")

        return await self._llm_provider.chat(
            messages=messages,
            tools=tools,
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

    async def _execute_tools_parallel(self, tool_calls: list[dict]) -> list[dict]:
        """
        并行执行工具调用

        Args:
            tool_calls: 工具调用列表

        Returns:
            工具执行结果列表
        """
        tasks = [
            self._execute_single_tool(tool_call)
            for tool_call in tool_calls
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_single_tool(self, tool_call: dict) -> dict:
        """
        执行单个工具调用

        Args:
            tool_call: 工具调用信息

        Returns:
            工具执行结果
        """
        function = tool_call["function"]
        tool_name = function["name"]
        arguments = function.get("arguments", {})

        try:
            result = await self.tool_registry.execute(tool_name, arguments)
            return {
                "tool_call_id": tool_call["id"],
                "content": str(result),
                "success": True,
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call["id"],
                "content": f"Error: {str(e)}",
                "success": False,
            }

    async def _build_context(self, session: Session) -> list[dict]:
        """
        构建对话上下文

        Args:
            session: 当前会话

        Returns:
            上下文消息列表
        """
        # 获取记忆
        memory_content = ""
        if self.config.memory_enabled:
            memory_content = await self.memory_store.get_memory()

        # 使用 ContextBuilder 构建完整上下文
        return await self.context_builder.build(
            messages=session.messages,
            memory=memory_content,
            tools=self.tool_registry.get_tool_summaries(),
            workspace=self.config.workspace,
        )

    async def _consolidate_memory(self, session: Session) -> None:
        """
        整合会话记忆

        当消息过多时，将旧消息归档到 MEMORY.md/HISTORY.md

        Args:
            session: 当前会话
        """
        # 保留最近 20 条消息
        if len(session.messages) > 20:
            recent_messages = session.messages[-20:]
            old_messages = session.messages[:-20]

            # 将旧消息写入历史文件
            await self.memory_store.append_to_history(old_messages)

            # 更新会话
            session.messages = recent_messages


# 便捷函数
async def create_agent_loop(
    config: AgentConfig,
    llm_provider: Any,
) -> AgentLoop:
    """
    创建并配置 AgentLoop

    Args:
        config: 代理配置
        llm_provider: LLM 提供商

    Returns:
        配置好的 AgentLoop 实例
    """
    from .tools.registry import create_default_registry

    # 创建依赖组件
    session_manager = SessionManager()
    memory_store = MemoryStore(config.workspace)
    tool_registry = await create_default_registry()

    # 创建 AgentLoop
    loop = AgentLoop(
        config=config,
        session_manager=session_manager,
        memory_store=memory_store,
        tool_registry=tool_registry,
    )
    loop.set_llm_provider(llm_provider)

    return loop

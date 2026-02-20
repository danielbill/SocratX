"""
Tool Registry - 工具注册表

参考: nanobot/nanobot/agent/tools/registry.py
动态工具管理和执行
"""

import asyncio
from typing import Any, Optional, Callable
from .base import Tool, ToolResult, SimpleTool


class ToolRegistry:
    """
    工具注册表

    管理所有可用工具，支持动态注册和执行
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        注册工具

        Args:
            tool: 要注册的工具
        """
        self._tools[tool.name] = tool

    def register_simple(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters_schema: Optional[dict] = None,
    ) -> None:
        """
        注册简单工具

        Args:
            name: 工具名称
            description: 工具描述
            handler: 处理函数
            parameters_schema: 参数 schema
        """
        tool = SimpleTool(name, description, handler, parameters_schema)
        self.register(tool)

    def unregister(self, name: str) -> bool:
        """
        注销工具

        Args:
            name: 工具名称

        Returns:
            是否成功注销
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """
        获取工具

        Args:
            name: 工具名称

        Returns:
            Tool 或 None
        """
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        """
        检查工具是否存在

        Args:
            name: 工具名称

        Returns:
            是否存在
        """
        return name in self._tools

    def list_tools(self) -> list[str]:
        """
        列出所有工具名称

        Returns:
            工具名称列表
        """
        return list(self._tools.keys())

    def get_tool_schemas(self) -> list[dict]:
        """
        获取所有工具的 schema

        用于 LLM 函数调用

        Returns:
            OpenAI 格式的函数 schema 列表
        """
        return [tool.get_schema() for tool in self._tools.values()]

    def get_tool_summaries(self) -> list[str]:
        """
        获取工具摘要列表

        Args:
            工具摘要列表（格式: name - description）
        """
        return [
            f"{tool.name} - {tool.description}"
            for tool in self._tools.values()
        ]

    async def execute(self, name: str, arguments: dict) -> Any:
        """
        执行工具

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        result = await tool.execute(**arguments)

        if isinstance(result, ToolResult):
            if not result.success:
                raise RuntimeError(result.error or "Tool execution failed")
            return result.content

        return result


# 内置工具定义


async def _read_file(path: str, **kwargs) -> ToolResult:
    """读取文件内容"""
    from pathlib import Path

    file_path = Path(path)
    if not file_path.exists():
        return ToolResult(success=False, content="", error=f"File not found: {path}")

    try:
        content = file_path.read_text(encoding="utf-8")
        return ToolResult(success=True, content=content)
    except Exception as e:
        return ToolResult(success=False, content="", error=str(e))


async def _write_file(path: str, content: str, **kwargs) -> ToolResult:
    """写入文件内容"""
    from pathlib import Path

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_path.write_text(content, encoding="utf-8")
        return ToolResult(success=True, content=f"File written: {path}")
    except Exception as e:
        return ToolResult(success=False, content="", error=str(e))


async def _list_dir(path: str, **kwargs) -> ToolResult:
    """列出目录内容"""
    from pathlib import Path

    dir_path = Path(path)
    if not dir_path.exists():
        return ToolResult(success=False, content="", error=f"Directory not found: {path}")

    try:
        items = []
        for item in dir_path.iterdir():
            item_type = "DIR" if item.is_dir() else "FILE"
            items.append(f"{item_type}: {item.name}")

        return ToolResult(
            success=True,
            content="\n".join(items) if items else "(empty directory)",
        )
    except Exception as e:
        return ToolResult(success=False, content="", error=str(e))


async def _exec_shell(command: str, **kwargs) -> ToolResult:
    """执行 shell 命令"""
    import subprocess

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout or result.stderr or "(no output)"
        return ToolResult(
            success=result.returncode == 0,
            content=output,
            error=result.stderr if result.returncode != 0 else None,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, content="", error="Command timed out")
    except Exception as e:
        return ToolResult(success=False, content="", error=str(e))


async def _web_search(query: str, **kwargs) -> ToolResult:
    """网络搜索"""
    # 简单实现，返回搜索 URL
    # 实际应用中应集成搜索 API
    encoded_query = query.replace(" ", "+")
    url = f"https://www.google.com/search?q={encoded_query}"
    return ToolResult(
        success=True,
        content=f"Search URL: {url}\n(Integrate with search API for actual results)",
    )


async def _web_fetch(url: str, **kwargs) -> ToolResult:
    """获取网页内容"""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()

            # 限制内容长度
            content = response.text[:10000]
            if len(response.text) > 10000:
                content += "\n... (truncated)"

            return ToolResult(success=True, content=content)
    except Exception as e:
        return ToolResult(success=False, content="", error=str(e))


async def create_default_registry() -> ToolRegistry:
    """
    创建默认工具注册表

    Returns:
        包含内置工具的 ToolRegistry
    """
    registry = ToolRegistry()

    # 文件工具
    registry.register_simple(
        name="file_read",
        description="Read the contents of a file",
        handler=_read_file,
        parameters_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                },
            },
            "required": ["path"],
        },
    )

    registry.register_simple(
        name="file_write",
        description="Write content to a file",
        handler=_write_file,
        parameters_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        },
    )

    registry.register_simple(
        name="file_list",
        description="List contents of a directory",
        handler=_list_dir,
        parameters_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory",
                },
            },
            "required": ["path"],
        },
    )

    # Shell 工具
    registry.register_simple(
        name="shell_exec",
        description="Execute a shell command",
        handler=_exec_shell,
        parameters_schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
            },
            "required": ["command"],
        },
    )

    # 网络工具
    registry.register_simple(
        name="web_search",
        description="Search the web for information",
        handler=_web_search,
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
            },
            "required": ["query"],
        },
    )

    registry.register_simple(
        name="web_fetch",
        description="Fetch content from a URL",
        handler=_web_fetch,
        parameters_schema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch",
                },
            },
            "required": ["url"],
        },
    )

    return registry

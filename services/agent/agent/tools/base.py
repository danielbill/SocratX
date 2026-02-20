"""
Tool Base - 工具抽象基类

参考: nanobot/nanobot/agent/tools/base.py
定义所有工具的通用接口
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel


class ToolArgs(BaseModel):
    """工具参数基类"""
    pass


class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    content: str
    error: Optional[str] = None
    metadata: dict = {}


class Tool(ABC):
    """
    工具抽象基类

    所有工具都应该继承此类并实现 execute 方法
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            ToolResult
        """
        pass

    def get_schema(self) -> dict:
        """
        获取工具的 JSON Schema

        用于 LLM 函数调用

        Returns:
            OpenAI 格式的函数 schema
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._get_parameters_schema(),
            },
        }

    def _get_parameters_schema(self) -> dict:
        """
        获取参数 schema

        默认实现，子类可以覆盖
        """
        return {
            "type": "object",
            "properties": {},
        }


class SimpleTool(Tool):
    """
    简单工具基类

    简化工具实现的辅助类
    """

    def __init__(
        self,
        name: str,
        description: str,
        handler: callable,
        parameters_schema: Optional[dict] = None,
    ):
        self.name = name
        self.description = description
        self._handler = handler
        self._parameters_schema = parameters_schema or {
            "type": "object",
            "properties": {},
        }

    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        try:
            result = await self._handler(**kwargs)
            if isinstance(result, ToolResult):
                return result
            return ToolResult(success=True, content=str(result))
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e),
            )

    def _get_parameters_schema(self) -> dict:
        return self._parameters_schema

"""ToolBase 测试"""
import pytest
from agent.tools.base import Tool, SimpleTool, ToolResult
from agent.tools.registry import ToolRegistry


# =============================================================================
# TestToolResult - 工具结果测试
# =============================================================================


class TestToolResult:
    """ToolResult 数据类测试"""

    def test_tool_result_success(self):
        """测试成功结果"""
        result = ToolResult(success=True, content="Success content")

        assert result.success is True
        assert result.content == "Success content"
        assert result.error is None

    def test_tool_result_error(self):
        """测试错误结果"""
        result = ToolResult(success=False, content="", error="Something went wrong")

        assert result.success is False
        assert result.content == ""
        assert result.error == "Something went wrong"

    def test_tool_result_empty(self):
        """测试空结果"""
        result = ToolResult(success=True, content="")

        assert result.success is True
        assert result.content == ""
        assert result.error is None

    def test_tool_result_with_metadata(self):
        """测试带元数据的结果"""
        result = ToolResult(
            success=True,
            content="Content",
            metadata={"key": "value"},
        )

        assert result.success is True
        assert result.metadata == {"key": "value"}


# =============================================================================
# TestSimpleTool - 简单工具测试
# =============================================================================


class TestSimpleTool:
    """SimpleTool 测试"""

    @pytest.mark.asyncio
    async def test_simple_tool_init(self):
        """测试 SimpleTool 初始化"""
        async def handler(x: int, **kwargs):
            return x * 2

        tool = SimpleTool(
            name="double",
            description="Double a number",
            handler=handler,
            parameters_schema={
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Number to double"},
                },
                "required": ["x"],
            },
        )

        assert tool.name == "double"
        assert tool.description == "Double a number"
        assert tool._handler == handler

    @pytest.mark.asyncio
    async def test_simple_tool_execute(self):
        """测试 SimpleTool 执行"""
        async def handler(x: int, **kwargs):
            return f"Result: {x}"

        tool = SimpleTool(
            name="test",
            description="Test tool",
            handler=handler,
        )

        result = await tool.execute(x=42)
        # SimpleTool 返回 ToolResult
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Result: 42" in result.content

    @pytest.mark.asyncio
    async def test_simple_tool_with_error(self):
        """测试带错误的执行"""
        async def handler(x: int, **kwargs):
            raise ValueError("Test error")

        tool = SimpleTool(
            name="test",
            description="Test tool",
            handler=handler,
        )

        # SimpleTool 会捕获异常并返回 ToolResult
        result = await tool.execute(x=42)
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Test error" in result.error

    @pytest.mark.asyncio
    async def test_simple_tool_get_schema(self):
        """测试获取工具 schema"""
        async def handler(x: int, **kwargs):
            return x

        tool = SimpleTool(
            name="test",
            description="Test tool",
            handler=handler,
            parameters_schema={
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                },
            },
        )

        schema = tool.get_schema()
        assert schema is not None
        assert "name" in schema or "function" in schema


# =============================================================================
# TestToolRegistry - 工具注册表测试
# =============================================================================


class TestToolRegistry:
    """ToolRegistry 测试"""

    def test_register_simple(self):
        """测试注册简单工具"""
        registry = ToolRegistry()

        registry.register_simple(
            name="echo",
            description="Echo back the input",
            handler=lambda text, **kwargs: f"Echo: {text}",
        )

        assert registry.has("echo")
        assert "echo" in registry.list_tools()

    def test_unregister(self):
        """测试注销工具"""
        registry = ToolRegistry()

        registry.register_simple(
            name="temp",
            description="Temporary tool",
            handler=lambda **kwargs: "temp",
        )

        assert registry.has("temp")

        result = registry.unregister("temp")
        assert result is True
        assert not registry.has("temp")

    def test_unregister_not_found(self):
        """测试注销不存在的工具"""
        registry = ToolRegistry()

        result = registry.unregister("nonexistent")
        assert result is False

    def test_has_tool(self):
        """测试检查工具存在"""
        registry = ToolRegistry()

        registry.register_simple(
            name="test",
            description="Test",
            handler=lambda **kwargs: "test",
        )

        assert registry.has("test")
        assert not registry.has("nonexistent")

    def test_get_tool_schemas(self):
        """测试获取工具 schema"""
        registry = ToolRegistry()

        registry.register_simple(
            name="test",
            description="Test tool",
            handler=lambda **kwargs: "test",
            parameters_schema={
                "type": "object",
                "properties": {},
            },
        )

        schemas = registry.get_tool_schemas()
        assert len(schemas) == 1
        assert schemas[0] is not None

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """测试执行工具"""
        registry = ToolRegistry()

        async def add_handler(a, b, **kwargs):
            return a + b

        registry.register_simple(
            name="add",
            description="Add two numbers",
            handler=add_handler,
        )

        result = await registry.execute("add", {"a": 2, "b": 3})
        assert result == 5

    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """测试执行不存在的工具"""
        registry = ToolRegistry()

        with pytest.raises(ValueError, match="Tool not found"):
            await registry.execute("nonexistent", {})

    @pytest.mark.asyncio
    async def test_execute_tool_with_error(self):
        """测试执行带错误的工具"""
        registry = ToolRegistry()

        registry.register_simple(
            name="fail",
            description="Always fails",
            handler=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("Fail")),
        )

        with pytest.raises(RuntimeError, match="Fail"):
            await registry.execute("fail", {})


# =============================================================================
# TestToolRegistryList - 工具列表测试
# =============================================================================


class TestToolRegistryList:
    """工具列表测试"""

    def test_list_tools(self):
        """测试列出工具"""
        registry = ToolRegistry()

        registry.register_simple(name="tool1", description="Tool 1", handler=lambda **kwargs: "1")
        registry.register_simple(name="tool2", description="Tool 2", handler=lambda **kwargs: "2")
        registry.register_simple(name="tool3", description="Tool 3", handler=lambda **kwargs: "3")

        tools = registry.list_tools()
        assert len(tools) == 3
        assert "tool1" in tools
        assert "tool2" in tools
        assert "tool3" in tools

    def test_get_tool(self):
        """测试获取工具"""
        registry = ToolRegistry()

        registry.register_simple(
            name="test",
            description="Test",
            handler=lambda **kwargs: "test",
        )

        tool = registry.get("test")
        assert tool is not None
        assert tool.name == "test"

    def test_get_tool_not_found(self):
        """测试获取不存在的工具"""
        registry = ToolRegistry()

        tool = registry.get("nonexistent")
        assert tool is None

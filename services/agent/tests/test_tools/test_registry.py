"""工具注册表测试"""
import pytest
from agent.tools.base import ToolBase, ToolSpec, ToolParameter
from agent.tools.registry import ToolRegistry, create_default_registry


class TestToolSpec:
    """ToolSpec 测试"""

    def test_create_tool_spec(self):
        """测试创建工具规格"""
        spec = ToolSpec(
            name="test_tool",
            description="A test tool",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Parameter 1",
                    required=True,
                )
            ],
        )
        
        assert spec.name == "test_tool"
        assert spec.description == "A test tool"
        assert len(spec.parameters) == 1

    def test_to_openai_schema(self):
        """测试转换为 OpenAI schema"""
        spec = ToolSpec(
            name="search",
            description="Search the web",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True,
                )
            ],
        )
        
        schema = spec.to_openai_schema()
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "search"
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]


class TestToolBase:
    """ToolBase 测试"""

    def test_tool_base_execute(self):
        """测试工具基类执行"""
        class TestTool(ToolBase):
            async def execute(self, **kwargs):
                return f"Executed with {kwargs}"
        
        tool = TestTool()
        result = tool.execute(param1="value1")
        
        assert "Executed with" in result


class TestToolRegistry:
    """ToolRegistry 测试"""

    @pytest.fixture
    def registry(self) -> ToolRegistry:
        """创建测试用的 ToolRegistry"""
        return ToolRegistry()

    def test_register_tool(self, registry: ToolRegistry):
        """测试注册工具"""
        class TestTool(ToolBase):
            async def execute(self, **kwargs):
                return "test"
        
        tool = TestTool()
        registry.register(tool)
        
        assert "test_tool" in registry._tools

    def test_register_tool_with_name(self, registry: ToolRegistry):
        """测试注册带名称的工具"""
        class CustomTool(ToolBase):
            async def execute(self, **kwargs):
                return "custom"
        
        tool = CustomTool()
        registry.register(tool)
        
        assert "custom_tool" in registry._tools

    def test_get_tool(self, registry: ToolRegistry):
        """测试获取工具"""
        class TestTool(ToolBase):
            async def execute(self, **kwargs):
                return "test"
        
        tool = TestTool()
        registry.register(tool)
        
        retrieved = registry.get_tool("test_tool")
        assert retrieved is not None
        assert isinstance(retrieved, TestTool)

    def test_get_tool_not_found(self, registry: ToolRegistry):
        """测试获取不存在的工具"""
        tool = registry.get_tool("nonexistent")
        assert tool is None

    def test_execute_tool(self, registry: ToolRegistry):
        """测试执行工具"""
        class TestTool(ToolBase):
            async def execute(self, value: str = "default"):
                return f"Result: {value}"
        
        tool = TestTool()
        registry.register(tool)
        
        import asyncio
        result = asyncio.run(registry.execute("test_tool", {"value": "test"}))
        
        assert result == "Result: test"

    def test_execute_tool_not_found(self, registry: ToolRegistry):
        """测试执行不存在的工具"""
        import asyncio
        import pytest
        
        with pytest.raises(ValueError, match="Tool not found"):
            asyncio.run(registry.execute("nonexistent", {}))

    def test_list_tools(self, registry: ToolRegistry):
        """测试列出工具"""
        class Tool1(ToolBase):
            async def execute(self, **kwargs):
                return "tool1"
        
        class Tool2(ToolBase):
            async def execute(self, **kwargs):
                return "tool2"
        
        registry.register(Tool1())
        registry.register(Tool2())
        
        tools = registry.list_tools()
        assert len(tools) >= 2

    def test_get_tool_schemas(self, registry: ToolRegistry):
        """测试获取工具 schema"""
        class TestTool(ToolBase):
            async def execute(self, **kwargs):
                return "test"
        
        registry.register(TestTool())
        
        schemas = registry.get_tool_schemas()
        assert len(schemas) >= 1
        assert any(s["function"]["name"] == "test_tool" for s in schemas)

    def test_get_tool_summaries(self, registry: ToolRegistry):
        """测试获取工具摘要"""
        class TestTool(ToolBase):
            async def execute(self, **kwargs):
                return "test"
        
        registry.register(TestTool())
        
        summaries = registry.get_tool_summaries()
        assert len(summaries) >= 1
        assert any("test_tool" in s for s in summaries)

    def test_has_tool(self, registry: ToolRegistry):
        """测试检查工具是否存在"""
        class TestTool(ToolBase):
            async def execute(self, **kwargs):
                return "test"
        
        assert not registry.has_tool("test_tool")
        
        registry.register(TestTool())
        assert registry.has_tool("test_tool")


class TestCreateDefaultRegistry:
    """create_default_registry 测试"""

    @pytest.mark.asyncio
    async def test_create_default_registry(self):
        """测试创建默认注册表"""
        registry = await create_default_registry()
        
        assert isinstance(registry, ToolRegistry)
        assert len(registry.list_tools()) > 0

    @pytest.mark.asyncio
    async def test_default_registry_has_builtin_tools(self):
        """测试默认注册表包含内置工具"""
        registry = await create_default_registry()
        
        # 应该有一些基本工具
        tools = registry.list_tools()
        assert len(tools) > 0

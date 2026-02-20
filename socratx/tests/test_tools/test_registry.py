"""工具注册表测试"""
import pytest
import asyncio

from agent.tools.registry import ToolRegistry
from agent.tools.base import Tool


class TestToolRegistry:
    """ToolRegistry 测试"""

    def test_register_tool(self):
        """测试注册工具"""
        registry = ToolRegistry()
        
        class TestTool(Tool):
            @property
            def name(self):
                return "test_tool"
            
            @property
            def description(self):
                return "A test tool"
            
            @property
            def parameters(self):
                return {"type": "object", "properties": {}}
            
            async def execute(self, **kwargs):
                return "test result"
        
        tool = TestTool()
        registry.register(tool)
        
        assert "test_tool" in registry.tool_names
        assert registry.has("test_tool")

    def test_get_tool(self):
        """测试获取工具"""
        registry = ToolRegistry()
        
        class TestTool(Tool):
            @property
            def name(self):
                return "test_tool"
            
            @property
            def description(self):
                return "A test tool"
            
            @property
            def parameters(self):
                return {"type": "object", "properties": {}}
            
            async def execute(self, **kwargs):
                return "test result"
        
        registry.register(TestTool())
        tool = registry.get("test_tool")
        
        assert tool is not None
        assert tool.name == "test_tool"

    def test_get_tool_not_found(self):
        """测试获取不存在的工具"""
        registry = ToolRegistry()
        tool = registry.get("nonexistent")
        assert tool is None

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """测试执行工具"""
        registry = ToolRegistry()
        
        class TestTool(Tool):
            @property
            def name(self):
                return "test_tool"
            
            @property
            def description(self):
                return "A test tool"
            
            @property
            def parameters(self):
                return {"type": "object", "properties": {}}
            
            async def execute(self, **kwargs):
                return "test result"
        
        registry.register(TestTool())
        result = await registry.execute("test_tool", {})
        
        assert "test result" in result

    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """测试执行不存在的工具"""
        registry = ToolRegistry()
        result = await registry.execute("nonexistent", {})
        assert "Error" in result

    def test_list_tools(self):
        """测试列出工具"""
        registry = ToolRegistry()
        
        class TestTool(Tool):
            @property
            def name(self):
                return "test_tool"
            
            @property
            def description(self):
                return "A test tool"
            
            @property
            def parameters(self):
                return {"type": "object", "properties": {}}
            
            async def execute(self, **kwargs):
                return "test result"
        
        registry.register(TestTool())
        names = registry.tool_names
        
        assert "test_tool" in names

    def test_get_definitions(self):
        """测试获取工具定义"""
        registry = ToolRegistry()
        
        class TestTool(Tool):
            @property
            def name(self):
                return "test_tool"
            
            @property
            def description(self):
                return "A test tool"
            
            @property
            def parameters(self):
                return {"type": "object", "properties": {}}
            
            async def execute(self, **kwargs):
                return "test result"
        
        registry.register(TestTool())
        definitions = registry.get_definitions()
        
        assert len(definitions) == 1
        assert definitions[0]["function"]["name"] == "test_tool"

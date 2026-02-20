"""工具基类测试"""
import pytest
from agent.tools.base import Tool


class TestToolBase:
    """Tool 基类测试"""

    def test_tool_abstract(self):
        """测试 Tool 是抽象类"""
        class TestTool(Tool):
            @property
            def name(self):
                return "test"
            
            @property
            def description(self):
                return "test tool"
            
            @property
            def parameters(self):
                return {"type": "object", "properties": {}}
            
            async def execute(self, **kwargs):
                return "result"
        
        tool = TestTool()
        assert tool.name == "test"
        assert tool.description == "test tool"

    @pytest.mark.asyncio
    async def test_tool_execute(self):
        """测试工具执行"""
        class TestTool(Tool):
            @property
            def name(self):
                return "test"
            
            @property
            def description(self):
                return "test tool"
            
            @property
            def parameters(self):
                return {"type": "object", "properties": {}}
            
            async def execute(self, **kwargs):
                return "result"
        
        tool = TestTool()
        result = await tool.execute()
        assert result == "result"

    def test_tool_schema(self):
        """测试工具 schema"""
        class TestTool(Tool):
            @property
            def name(self):
                return "test"
            
            @property
            def description(self):
                return "test tool"
            
            @property
            def parameters(self):
                return {
                    "type": "object",
                    "properties": {
                        "arg1": {"type": "string", "description": "Argument 1"}
                    }
                }
            
            async def execute(self, **kwargs):
                return "result"
        
        tool = TestTool()
        schema = tool.to_schema()
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "test"
        assert "arg1" in schema["function"]["parameters"]["properties"]

    def test_validate_params(self):
        """测试参数验证"""
        class TestTool(Tool):
            @property
            def name(self):
                return "test"
            
            @property
            def description(self):
                return "test tool"
            
            @property
            def parameters(self):
                return {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name"}
                    },
                    "required": ["name"]
                }
            
            async def execute(self, **kwargs):
                return "result"
        
        tool = TestTool()
        
        # 缺少必需参数
        errors = tool.validate_params({})
        assert len(errors) > 0
        
        # 正确参数
        errors = tool.validate_params({"name": "test"})
        assert len(errors) == 0

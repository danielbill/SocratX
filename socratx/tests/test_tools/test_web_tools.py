"""Web 工具测试"""
import pytest
from agent.tools.registry import ToolRegistry
from agent.tools.web import WebSearchTool, WebFetchTool


@pytest.fixture
def tool_registry():
    """创建包含 web 工具的注册表"""
    registry = ToolRegistry()
    # 不实际注册，因为需要 API key
    return registry


class TestWebTools:
    """Web 工具测试"""

    def test_web_search_init(self):
        """测试 WebSearchTool 初始化"""
        tool = WebSearchTool()
        assert tool.name == "web_search"
        assert "search" in tool.description.lower()

    def test_web_fetch_init(self):
        """测试 WebFetchTool 初始化"""
        tool = WebFetchTool()
        assert tool.name == "web_fetch"
        assert "fetch" in tool.description.lower() or "url" in tool.description.lower()

    def test_web_search_schema(self):
        """测试 WebSearchTool schema"""
        tool = WebSearchTool()
        schema = tool.to_schema()
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "web_search"
        assert "query" in schema["function"]["parameters"]["properties"]

    def test_web_fetch_schema(self):
        """测试 WebFetchTool schema"""
        tool = WebFetchTool()
        schema = tool.to_schema()
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "web_fetch"
        assert "url" in schema["function"]["parameters"]["properties"]

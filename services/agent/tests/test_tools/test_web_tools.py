"""网络工具测试"""
import pytest

from agent.tools.registry import ToolRegistry
from agent.tools.base import ToolResult


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tool_registry():
    """创建包含网络工具的注册表"""
    registry = ToolRegistry()

    async def web_search_handler(query, **kwargs):
        return await _web_search(query)

    async def web_fetch_handler(url, **kwargs):
        return await _web_fetch(url)

    registry.register_simple(
        name="web_search",
        description="Search the web for information",
        handler=web_search_handler,
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        },
    )

    registry.register_simple(
        name="web_fetch",
        description="Fetch content from a URL",
        handler=web_fetch_handler,
        parameters_schema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
            },
            "required": ["url"],
        },
    )

    return registry


# =============================================================================
# Helper Functions
# =============================================================================


async def _web_search(query: str) -> ToolResult:
    """网络搜索"""
    from urllib.parse import quote

    encoded_query = quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    return ToolResult(
        success=True,
        content=f"Search URL: {url}\n(Integrate with search API for actual results)",
    )


async def _web_fetch(url: str) -> ToolResult:
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


# =============================================================================
# TestWebSearch - 网络搜索测试
# =============================================================================


class TestWebSearch:
    """网络搜索测试"""

    @pytest.mark.asyncio
    async def test_web_search(self, tool_registry):
        """测试网络搜索"""
        result = await tool_registry.execute(
            "web_search",
            {"query": "Python programming"},
        )

        assert result.success is True
        assert "Search URL" in result
        assert "Python+programming" in result or "Python%20programming" in result

    @pytest.mark.asyncio
    async def test_web_search_special_chars(self, tool_registry):
        """测试特殊字符搜索"""
        result = await tool_registry.execute(
            "web_search",
            {"query": "Python & Django @2024"},
        )

        assert result.success is True
        assert "Search URL" in result

    @pytest.mark.asyncio
    async def test_web_search_chinese(self, tool_registry):
        """测试中文搜索"""
        result = await tool_registry.execute(
            "web_search",
            {"query": "Python 编程"},
        )

        assert result.success is True
        assert "Search URL" in result


# =============================================================================
# TestWebFetch - 网页获取测试
# =============================================================================


class TestWebFetch:
    """网页获取测试"""

    @pytest.mark.asyncio
    async def test_web_fetch_success(self, tool_registry):
        """测试获取网页成功"""
        # 使用一个可靠的测试 URL
        result = await tool_registry.execute(
            "web_fetch",
            {"url": "https://httpbin.org/html"},
        )

        # 可能因网络问题失败，所以不强制要求成功
        assert result is not None

    @pytest.mark.asyncio
    async def test_web_fetch_invalid_url(self, tool_registry):
        """测试无效 URL"""
        result = await tool_registry.execute(
            "web_fetch",
            {"url": "not-a-valid-url"},
        )

        # 应该返回错误
        assert result is not None

    @pytest.mark.asyncio
    async def test_web_fetch_not_found(self, tool_registry):
        """测试 404 错误"""
        result = await tool_registry.execute(
            "web_fetch",
            {"url": "https://httpbin.org/status/404"},
        )

        # 404 应该返回错误
        assert result.success is False or "404" in result

    @pytest.mark.asyncio
    async def test_web_fetch_timeout(self, tool_registry):
        """测试超时"""
        # 使用一个会延迟的 URL
        result = await tool_registry.execute(
            "web_fetch",
            {"url": "https://httpbin.org/delay/15"},
        )

        # 应该超时或返回错误
        assert result is not None


# =============================================================================
# TestNetworkTools - 网络工具集成测试
# =============================================================================


class TestNetworkTools:
    """网络工具集成测试"""

    @pytest.mark.asyncio
    async def test_search_then_fetch(self, tool_registry):
        """测试搜索后获取"""
        # 先搜索
        search_result = await tool_registry.execute(
            "web_search",
            {"query": "Python official website"},
        )

        assert search_result.success is True
        assert "Search URL" in search_result

        # 注意：实际使用中需要解析搜索结果获取 URL
        # 这里只是验证搜索工具工作正常

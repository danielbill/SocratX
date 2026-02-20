"""文件工具测试"""
import pytest
from pathlib import Path
import asyncio

from agent.tools.registry import ToolRegistry


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tool_registry():
    """创建包含文件工具的注册表"""
    registry = ToolRegistry()

    # 注册文件工具
    from agent.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
    
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirTool())

    return registry


# =============================================================================
# TestFileTools - 文件工具测试
# =============================================================================


class TestFileTools:
    """文件工具测试"""

    @pytest.mark.asyncio
    async def test_file_write_success(self, tool_registry, tmp_path):
        """测试文件写入成功"""
        test_file = tmp_path / "test.txt"
        
        result = await tool_registry.execute(
            "write_file",
            {"path": str(test_file), "content": "hello world"}
        )
        
        assert test_file.exists()
        assert "hello world" in test_file.read_text()
        assert "Successfully wrote" in result

    @pytest.mark.asyncio
    async def test_file_read_success(self, tool_registry, tmp_path):
        """测试文件读取成功"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content", encoding='utf-8')
        
        result = await tool_registry.execute(
            "read_file",
            {"path": str(test_file)}
        )
        
        assert "test content" in result

    @pytest.mark.asyncio
    async def test_file_read_not_found(self, tool_registry, tmp_path):
        """测试文件不存在"""
        result = await tool_registry.execute(
            "read_file",
            {"path": str(tmp_path / "nonexistent.txt")}
        )
        
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_file_list_dir(self, tool_registry, tmp_path):
        """测试列出目录"""
        (tmp_path / "file1.txt").write_text("1")
        (tmp_path / "file2.txt").write_text("2")
        
        result = await tool_registry.execute(
            "list_dir",
            {"path": str(tmp_path)}
        )
        
        assert "file1.txt" in result
        assert "file2.txt" in result

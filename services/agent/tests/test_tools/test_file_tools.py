"""文件工具测试"""
import pytest
from pathlib import Path
import asyncio

from agent.tools.registry import ToolRegistry
from agent.tools.base import ToolResult


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tool_registry():
    """创建包含文件工具的注册表"""
    registry = ToolRegistry()

    # 注册文件工具（使用异步 handler）
    async def read_file_handler(path, **kwargs):
        return await _read_file(path)

    async def write_file_handler(path, content, **kwargs):
        return await _write_file(path, content)

    async def list_dir_handler(path, **kwargs):
        return await _list_dir(path)

    registry.register_simple(
        name="file_read",
        description="Read the contents of a file",
        handler=read_file_handler,
        parameters_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
            },
            "required": ["path"],
        },
    )

    registry.register_simple(
        name="file_write",
        description="Write content to a file",
        handler=write_file_handler,
        parameters_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
    )

    registry.register_simple(
        name="file_list",
        description="List contents of a directory",
        handler=list_dir_handler,
        parameters_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the directory"},
            },
            "required": ["path"],
        },
    )

    return registry


# =============================================================================
# Helper Functions
# =============================================================================


async def _read_file(path: str) -> ToolResult:
    """读取文件内容"""
    file_path = Path(path)
    if not file_path.exists():
        return ToolResult(success=False, content="", error=f"File not found: {path}")

    try:
        content = file_path.read_text(encoding="utf-8")
        return ToolResult(success=True, content=content)
    except Exception as e:
        return ToolResult(success=False, content="", error=str(e))


async def _write_file(path: str, content: str) -> ToolResult:
    """写入文件内容"""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_path.write_text(content, encoding="utf-8")
        return ToolResult(success=True, content=f"File written: {path}")
    except Exception as e:
        return ToolResult(success=False, content="", error=str(e))


async def _list_dir(path: str) -> ToolResult:
    """列出目录内容"""
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


# =============================================================================
# TestFileRead - 文件读取测试
# =============================================================================


class TestFileRead:
    """文件读取测试"""

    @pytest.mark.asyncio
    async def test_file_read_success(self, tool_registry, tmp_path):
        """测试文件读取成功"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!", encoding="utf-8")

        result = await tool_registry.execute(
            "file_read",
            {"path": str(test_file)},
        )

        assert result.success is True
        assert "Hello, World!" in result

    @pytest.mark.asyncio
    async def test_file_read_not_found(self, tool_registry, tmp_path):
        """测试文件不存在"""
        non_existent = tmp_path / "nonexistent.txt"

        with pytest.raises(RuntimeError, match="File not found"):
            await tool_registry.execute(
                "file_read",
                {"path": str(non_existent)},
            )

    @pytest.mark.asyncio
    async def test_file_read_unicode(self, tool_registry, tmp_path):
        """测试读取 Unicode 内容"""
        test_file = tmp_path / "unicode.txt"
        test_file.write_text("你好 世界！🚀", encoding="utf-8")

        result = await tool_registry.execute(
            "file_read",
            {"path": str(test_file)},
        )

        assert result.success is True
        assert "你好 世界！🚀" in result

    @pytest.mark.asyncio
    async def test_file_read_empty(self, tool_registry, tmp_path):
        """测试读取空文件"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        result = await tool_registry.execute(
            "file_read",
            {"path": str(test_file)},
        )

        assert result.success is True
        assert result == ""


# =============================================================================
# TestFileWrite - 文件写入测试
# =============================================================================


class TestFileWrite:
    """文件写入测试"""

    @pytest.mark.asyncio
    async def test_file_write_success(self, tool_registry, tmp_path):
        """测试文件写入成功"""
        test_file = tmp_path / "output.txt"

        result = await tool_registry.execute(
            "file_write",
            {"path": str(test_file), "content": "Test content"},
        )

        assert result.success is True
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == "Test content"

    @pytest.mark.asyncio
    async def test_file_write_create_dirs(self, tool_registry, tmp_path):
        """测试自动创建目录"""
        test_file = tmp_path / "subdir" / "nested" / "output.txt"

        result = await tool_registry.execute(
            "file_write",
            {"path": str(test_file), "content": "Nested content"},
        )

        assert result.success is True
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == "Nested content"

    @pytest.mark.asyncio
    async def test_file_write_overwrite(self, tool_registry, tmp_path):
        """测试覆盖已有文件"""
        test_file = tmp_path / "overwrite.txt"
        test_file.write_text("Old content", encoding="utf-8")

        result = await tool_registry.execute(
            "file_write",
            {"path": str(test_file), "content": "New content"},
        )

        assert result.success is True
        assert test_file.read_text(encoding="utf-8") == "New content"

    @pytest.mark.asyncio
    async def test_file_write_unicode(self, tool_registry, tmp_path):
        """测试写入 Unicode 内容"""
        test_file = tmp_path / "unicode.txt"

        result = await tool_registry.execute(
            "file_write",
            {"path": str(test_file), "content": "你好 世界！🚀"},
        )

        assert result.success is True
        assert test_file.read_text(encoding="utf-8") == "你好 世界！🚀"


# =============================================================================
# TestFileList - 目录列表测试
# =============================================================================


class TestFileList:
    """目录列表测试"""

    @pytest.mark.asyncio
    async def test_file_list_dir(self, tool_registry, tmp_path):
        """测试列出目录内容"""
        # 创建测试文件和目录
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "subdir").mkdir()

        result = await tool_registry.execute(
            "file_list",
            {"path": str(tmp_path)},
        )

        assert result.success is True
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result

    @pytest.mark.asyncio
    async def test_file_list_empty_dir(self, tool_registry, tmp_path):
        """测试列出空目录"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = await tool_registry.execute(
            "file_list",
            {"path": str(empty_dir)},
        )

        assert result.success is True
        assert "empty directory" in result

    @pytest.mark.asyncio
    async def test_file_list_not_found(self, tool_registry, tmp_path):
        """测试目录不存在"""
        non_existent = tmp_path / "nonexistent"

        with pytest.raises(RuntimeError, match="Directory not found"):
            await tool_registry.execute(
                "file_list",
                {"path": str(non_existent)},
            )


# =============================================================================
# TestFileOperations - 文件操作集成测试
# =============================================================================


class TestFileOperations:
    """文件操作集成测试"""

    @pytest.mark.asyncio
    async def test_write_then_read(self, tool_registry, tmp_path):
        """测试写入后读取"""
        test_file = tmp_path / "test.txt"
        content = "Test content for write and read"

        # 写入
        write_result = await tool_registry.execute(
            "file_write",
            {"path": str(test_file), "content": content},
        )
        assert write_result.success is True

        # 读取
        read_result = await tool_registry.execute(
            "file_read",
            {"path": str(test_file)},
        )
        assert read_result.success is True
        assert content in read_result

    @pytest.mark.asyncio
    async def test_multiple_files(self, tool_registry, tmp_path):
        """测试多个文件操作"""
        files = [tmp_path / f"file{i}.txt" for i in range(3)]

        # 写入多个文件
        for i, f in enumerate(files):
            result = await tool_registry.execute(
                "file_write",
                {"path": str(f), "content": f"Content {i}"},
            )
            assert result.success is True

        # 列出目录
        list_result = await tool_registry.execute(
            "file_list",
            {"path": str(tmp_path)},
        )
        assert list_result.success is True
        for f in files:
            assert f.name in list_result

        # 读取所有文件
        for i, f in enumerate(files):
            read_result = await tool_registry.execute(
                "file_read",
                {"path": str(f)},
            )
            assert f"Content {i}" in read_result

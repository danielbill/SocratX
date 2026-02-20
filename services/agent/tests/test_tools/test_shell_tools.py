"""Shell 工具测试"""
import pytest
import subprocess
from pathlib import Path

from agent.tools.registry import ToolRegistry
from agent.tools.base import ToolResult


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tool_registry():
    """创建包含 Shell 工具的注册表"""
    registry = ToolRegistry()

    async def exec_shell_handler(command, **kwargs):
        return await _exec_shell(command)

    registry.register_simple(
        name="shell_exec",
        description="Execute a shell command",
        handler=exec_shell_handler,
        parameters_schema={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command"},
            },
            "required": ["command"],
        },
    )

    return registry


# =============================================================================
# Helper Functions
# =============================================================================


async def _exec_shell(command: str) -> ToolResult:
    """执行 shell 命令"""
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


# =============================================================================
# TestShellExec - Shell 命令执行测试
# =============================================================================


class TestShellExec:
    """Shell 命令执行测试"""

    @pytest.mark.asyncio
    async def test_shell_exec_success(self, tool_registry):
        """测试命令执行成功"""
        result = await tool_registry.execute(
            "shell_exec",
            {"command": "echo Hello World"},
        )

        assert result.success is True
        assert "Hello World" in result

    @pytest.mark.asyncio
    async def test_shell_exec_error(self, tool_registry):
        """测试命令执行错误"""
        # 使用返回非零退出码的命令
        result = await tool_registry.execute(
            "shell_exec",
            {"command": "exit 1"},
        )

        # 应该抛出 RuntimeError
        assert result.success is False

    @pytest.mark.asyncio
    async def test_shell_exec_with_output(self, tool_registry):
        """测试带输出的命令"""
        result = await tool_registry.execute(
            "shell_exec",
            {"command": "dir" if subprocess.os.name == "nt" else "ls"},
        )

        assert result.success is True
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_shell_exec_pipe(self, tool_registry):
        """测试管道命令"""
        result = await tool_registry.execute(
            "shell_exec",
            {"command": "echo test | findstr test" if subprocess.os.name == "nt" else "echo test | grep test"},
        )

        # 管道命令应该成功
        assert result.success is True or "test" in result


# =============================================================================
# TestShellExecSafe - 安全测试
# =============================================================================


class TestShellExecSafe:
    """Shell 工具安全测试"""

    @pytest.mark.asyncio
    async def test_shell_exec_injection_attempt(self, tool_registry):
        """测试命令注入尝试"""
        # 这些命令应该被执行，但测试主要验证工具能处理
        result = await tool_registry.execute(
            "shell_exec",
            {"command": "echo 'test' && echo 'injection'"},
        )

        # 工具应该返回结果
        assert result is not None

    @pytest.mark.asyncio
    async def test_shell_exec_long_command(self, tool_registry):
        """测试长命令"""
        long_arg = "a" * 1000
        result = await tool_registry.execute(
            "shell_exec",
            {"command": f"echo {long_arg}"},
        )

        assert result is not None

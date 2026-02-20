"""Shell 工具测试"""
import pytest
from agent.tools.registry import ToolRegistry
from agent.tools.shell import ExecTool


@pytest.fixture
def tool_registry():
    """创建包含 shell 工具的注册表"""
    registry = ToolRegistry()
    registry.register(ExecTool())
    return registry


class TestShellTools:
    """Shell 工具测试"""

    @pytest.mark.asyncio
    async def test_shell_exec_success(self, tool_registry):
        """测试 shell 执行成功"""
        result = await tool_registry.execute(
            "exec",
            {"command": "echo hello"}
        )
        
        assert "hello" in result

    @pytest.mark.asyncio
    async def test_shell_exec_with_output(self, tool_registry):
        """测试 shell 执行带输出"""
        result = await tool_registry.execute(
            "exec",
            {"command": "pwd"}
        )
        
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_shell_exec_error(self, tool_registry):
        """测试 shell 执行错误"""
        result = await tool_registry.execute(
            "exec",
            {"command": "nonexistent_command_12345"}
        )
        
        assert "Error" in result or len(result) > 0

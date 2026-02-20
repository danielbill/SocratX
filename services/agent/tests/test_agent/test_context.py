"""ContextBuilder 测试"""
import pytest
from pathlib import Path
from datetime import datetime

from agent.context import (
    ContextBuilder,
    ContextBuilderConfig,
    DEFAULT_SYSTEM_PROMPT,
    create_context_builder,
)
from agent.session import Message


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_workspace(tmp_path):
    """创建临时工作区"""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def sample_messages():
    """示例消息列表"""
    return [
        Message(role="user", content="Hello", timestamp="2024-01-01T00:00:00"),
        Message(role="assistant", content="Hi there!", timestamp="2024-01-01T00:00:01"),
        Message(role="user", content="How are you?", timestamp="2024-01-01T00:00:02"),
    ]


@pytest.fixture
def context_builder(temp_workspace):
    """创建 ContextBuilder 实例"""
    return ContextBuilder(workspace=str(temp_workspace))


# =============================================================================
# TestContextBuilderInit - 初始化测试
# =============================================================================


class TestContextBuilderInit:
    """ContextBuilder 初始化测试"""

    def test_init_default(self, temp_workspace):
        """测试默认初始化"""
        builder = ContextBuilder(workspace=str(temp_workspace))

        assert builder.agent_name == "SocratX"
        assert builder.workspace == temp_workspace
        assert builder.custom_system_prompt is None
        assert len(builder.guidance_files) == 3

    def test_init_with_custom_prompt(self, temp_workspace):
        """测试自定义系统提示"""
        custom_prompt = "You are a custom assistant."
        builder = ContextBuilder(
            workspace=str(temp_workspace),
            system_prompt=custom_prompt,
        )

        assert builder.custom_system_prompt == custom_prompt

    def test_init_with_workspace(self, temp_workspace):
        """测试工作区设置"""
        builder = ContextBuilder(workspace=str(temp_workspace))

        assert builder.workspace == temp_workspace

    def test_init_with_agent_name(self, temp_workspace):
        """测试代理名称"""
        builder = ContextBuilder(
            workspace=str(temp_workspace),
            agent_name="CustomAgent",
        )

        assert builder.agent_name == "CustomAgent"


# =============================================================================
# TestContextBuilderBuild - 构建上下文测试
# =============================================================================


class TestContextBuilderBuild:
    """ContextBuilder 构建上下文测试"""

    @pytest.mark.asyncio
    async def test_build_empty_context(self, context_builder):
        """测试空上下文"""
        result = await context_builder.build(messages=[])

        assert isinstance(result, list)
        assert len(result) == 1  # 只有 system 消息
        assert result[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_build_with_messages(self, context_builder, sample_messages):
        """测试带消息"""
        result = await context_builder.build(
            messages=sample_messages,
        )

        # system + 3 条消息
        assert len(result) == 4
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"
        assert result[1]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_build_with_memory(self, context_builder):
        """测试带记忆"""
        memory = "User prefers dark mode."
        result = await context_builder.build(
            messages=[],
            memory=memory,
        )

        system_content = result[0]["content"]
        assert "长期记忆" in system_content
        assert memory in system_content

    @pytest.mark.asyncio
    async def test_build_with_system_prompt(self, temp_workspace):
        """测试带系统提示"""
        custom_prompt = "Custom system prompt."
        builder = ContextBuilder(
            workspace=str(temp_workspace),
            system_prompt=custom_prompt,
        )

        result = await builder.build(messages=[])

        system_content = result[0]["content"]
        assert custom_prompt in system_content

    @pytest.mark.asyncio
    async def test_build_with_tools(self, context_builder):
        """测试带工具列表"""
        tools = ["file_read - Read files", "file_write - Write files"]
        result = await context_builder.build(
            messages=[],
            tools=tools,
        )

        system_content = result[0]["content"]
        assert "可用工具" in system_content
        assert "file_read" in system_content
        assert "file_write" in system_content


# =============================================================================
# TestContextBuilderSystemPrompt - 系统提示词测试
# =============================================================================


class TestContextBuilderSystemPrompt:
    """ContextBuilder 系统提示词测试"""

    @pytest.mark.asyncio
    async def test_build_system_prompt_identity(self, context_builder):
        """测试身份信息"""
        result = await context_builder.build(messages=[])

        system_content = result[0]["content"]
        assert "SocratX" in system_content
        assert "当前时间" in system_content
        assert "运行环境" in system_content

    @pytest.mark.asyncio
    async def test_build_system_prompt_memory(self, context_builder):
        """测试记忆部分"""
        memory = "Important fact about user."
        result = await context_builder.build(
            messages=[],
            memory=memory,
        )

        system_content = result[0]["content"]
        assert "## 长期记忆" in system_content
        assert memory in system_content

    @pytest.mark.asyncio
    async def test_build_system_prompt_tools(self, context_builder):
        """测试工具部分"""
        tools = ["tool1 - Description 1", "tool2 - Description 2"]
        result = await context_builder.build(
            messages=[],
            tools=tools,
        )

        system_content = result[0]["content"]
        assert "## 可用工具" in system_content
        assert "tool1" in system_content
        assert "tool2" in system_content

    @pytest.mark.asyncio
    async def test_build_system_prompt_workspace(self, temp_workspace):
        """测试工作区信息"""
        # 创建工作区文件
        (temp_workspace / "test.txt").write_text("test")

        builder = ContextBuilder(workspace=str(temp_workspace))
        result = await builder.build(
            messages=[],
            workspace=str(temp_workspace),
        )

        system_content = result[0]["content"]
        assert "## 工作区" in system_content


# =============================================================================
# TestContextBuilderEdgeCases - 边界条件测试
# =============================================================================


class TestContextBuilderEdgeCases:
    """ContextBuilder 边界条件测试"""

    @pytest.mark.asyncio
    async def test_build_truncates_long_messages(self, temp_workspace):
        """测试截断长消息"""
        builder = ContextBuilder(workspace=str(temp_workspace))

        # 创建超过 50 条消息
        messages = [
            Message(role="user", content=f"Message {i}", timestamp="2024-01-01T00:00:00")
            for i in range(60)
        ]

        result = await builder.build(messages=messages)

        # 应该只保留最近 50 条 + system 消息
        assert len(result) == 51  # 50 条历史 + 1 条 system

    @pytest.mark.asyncio
    async def test_build_limits_history_count(self, temp_workspace):
        """测试限制历史消息数"""
        builder = ContextBuilder(workspace=str(temp_workspace))

        # 创建正好 50 条消息
        messages = [
            Message(role="user", content=f"Message {i}", timestamp="2024-01-01T00:00:00")
            for i in range(50)
        ]

        result = await builder.build(messages=messages)

        # 应该保留所有 50 条 + system 消息
        assert len(result) == 51

    @pytest.mark.asyncio
    async def test_build_handles_empty_memory(self, context_builder):
        """测试处理空记忆"""
        result = await context_builder.build(
            messages=[],
            memory="",
        )

        system_content = result[0]["content"]
        # 空记忆时不应该有"长期记忆"部分
        assert "## 长期记忆" not in system_content

    @pytest.mark.asyncio
    async def test_build_handles_empty_tools(self, context_builder):
        """测试处理空工具列表"""
        result = await context_builder.build(
            messages=[],
            tools=[],
        )

        system_content = result[0]["content"]
        # 空工具列表时不应该有"可用工具"部分
        assert "## 可用工具" not in system_content

    @pytest.mark.asyncio
    async def test_build_with_special_characters(self, context_builder):
        """测试特殊字符"""
        messages = [
            Message(
                role="user",
                content="Hello! @#$%^&*() 你好 🚀",
                timestamp="2024-01-01T00:00:00",
            )
        ]

        result = await context_builder.build(messages=messages)

        assert len(result) == 2  # system + 1 message
        assert "Hello! @#$%^&*() 你好 🚀" in result[1]["content"]


# =============================================================================
# TestContextBuilderGuidanceFiles - 引导文件测试
# =============================================================================


class TestContextBuilderGuidanceFiles:
    """ContextBuilder 引导文件测试"""

    @pytest.mark.asyncio
    async def test_load_guidance_files_exists(self, temp_workspace):
        """测试加载存在的引导文件"""
        # 创建引导文件
        agents_file = temp_workspace / "agents.md"
        agents_file.write_text("# AGENTS\nThis is agents file.")

        builder = ContextBuilder(workspace=str(temp_workspace))
        result = await builder.build(messages=[])

        system_content = result[0]["content"]
        assert "AGENTS" in system_content
        assert "This is agents file." in system_content

    @pytest.mark.asyncio
    async def test_load_guidance_files_not_exists(self, temp_workspace):
        """测试加载不存在的引导文件"""
        builder = ContextBuilder(workspace=str(temp_workspace))
        result = await builder.build(messages=[])

        system_content = result[0]["content"]
        # 不应该有引导文件内容
        assert "来自 AGENTS.md" not in system_content

    @pytest.mark.asyncio
    async def test_guidance_files_priority(self, temp_workspace):
        """测试引导文件优先级"""
        # 创建多个引导文件
        (temp_workspace / "agents.md").write_text("# AGENTS")
        (temp_workspace / "soul.md").write_text("# SOUL")
        (temp_workspace / "user.md").write_text("# USER")

        builder = ContextBuilder(workspace=str(temp_workspace))
        result = await builder.build(messages=[])

        system_content = result[0]["content"]
        # 应该只加载第一个存在的文件 (AGENTS.md)
        assert "# AGENTS" in system_content


# =============================================================================
# TestContextBuilderConfig - 配置类测试
# =============================================================================


class TestContextBuilderConfig:
    """ContextBuilderConfig 配置类测试"""

    def test_config_default(self):
        """测试默认配置"""
        config = ContextBuilderConfig()

        assert config.system_prompt is None
        assert config.workspace == ""
        assert config.agent_name == "SocratX"
        assert config.enable_guidance_files is True
        assert config.max_history == 50

    def test_config_custom(self):
        """测试自定义配置"""
        config = ContextBuilderConfig(
            system_prompt="Custom prompt",
            workspace="/tmp",
            agent_name="CustomAgent",
            enable_guidance_files=False,
            max_history=100,
        )

        assert config.system_prompt == "Custom prompt"
        assert config.workspace == "/tmp"
        assert config.agent_name == "CustomAgent"
        assert config.enable_guidance_files is False
        assert config.max_history == 100

    def test_config_build(self, temp_workspace):
        """测试配置创建实例"""
        config = ContextBuilderConfig(
            workspace=str(temp_workspace),
            agent_name="TestAgent",
        )

        builder = config.build()

        assert isinstance(builder, ContextBuilder)
        assert builder.agent_name == "TestAgent"


# =============================================================================
# TestHelperFunctions - 辅助函数测试
# =============================================================================


class TestHelperFunctions:
    """辅助函数测试"""

    @pytest.mark.asyncio
    async def test_create_context_builder(self, temp_workspace):
        """测试创建 ContextBuilder"""
        builder = await create_context_builder(
            workspace=str(temp_workspace),
        )

        assert isinstance(builder, ContextBuilder)
        assert builder.workspace == temp_workspace

    @pytest.mark.asyncio
    async def test_create_context_builder_with_prompt(self, temp_workspace):
        """测试带系统提示创建"""
        custom_prompt = "Custom prompt."
        builder = await create_context_builder(
            workspace=str(temp_workspace),
            system_prompt=custom_prompt,
        )

        assert builder.custom_system_prompt == custom_prompt

    def test_default_system_prompt(self):
        """测试默认系统提示"""
        assert "SocratX" in DEFAULT_SYSTEM_PROMPT
        assert "智能助手" in DEFAULT_SYSTEM_PROMPT


# =============================================================================
# TestFormatTools - 工具格式化测试
# =============================================================================


class TestFormatTools:
    """工具格式化测试"""

    def test_format_tools_empty(self, context_builder):
        """测试空工具列表"""
        result = context_builder._format_tools([])
        assert result == "无可用工具"

    def test_format_tools_single(self, context_builder):
        """测试单个工具"""
        result = context_builder._format_tools(["tool1 - Desc"])
        assert result == "- tool1 - Desc"

    def test_format_tools_multiple(self, context_builder):
        """测试多个工具"""
        tools = ["tool1 - Desc 1", "tool2 - Desc 2"]
        result = context_builder._format_tools(tools)

        assert "- tool1 - Desc 1" in result
        assert "- tool2 - Desc 2" in result


# =============================================================================
# TestBuildIdentity - 身份信息构建测试
# =============================================================================


class TestBuildIdentity:
    """身份信息构建测试"""

    def test_build_identity(self, context_builder):
        """测试身份信息"""
        result = context_builder._build_identity()

        assert "SocratX" in result
        assert "当前时间" in result
        assert "运行环境" in result
        assert "工作目录" in result

    def test_build_identity_with_custom_agent_name(self, temp_workspace):
        """测试自定义代理名称"""
        builder = ContextBuilder(
            workspace=str(temp_workspace),
            agent_name="CustomAgent",
        )

        result = builder._build_identity()

        assert "CustomAgent" in result

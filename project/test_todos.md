# SocratX 测试待办任务

**最后更新**: 2026 年 2 月 20 日
**负责人**: 测试总监 (AI)

---

## 测试进度概览

| 优先级 | 模块 | 状态 | 进度 |
|--------|------|------|------|
| P0 | AgentLoop 核心测试 | ✅ **已完成** | 100% |
| P0 | LiteLLMProvider 测试 | ✅ **已完成** | 100% |
| P1 | ContextBuilder 测试 | ✅ **已完成** | 100% |
| P1 | 集成测试 | ✅ **已完成** | 100% |
| P2 | 工具测试扩展 | ✅ **已完成** | 100% |
| P2 | Provider 测试扩展 | ✅ **已完成** | 100% |
| CD | CI/CD 配置 | ✅ **已完成** | 100% |

---

## P0 - 核心功能测试（本周）

### 1. AgentLoop 核心测试

**文件**: `services/agent/tests/test_agent/test_loop.py`

**状态**: ✅ **已完成** (17 个测试全部通过)

**测试场景**:

```
class TestAgentLoopBasic:
    - [x] test_init                      # 初始化验证 ✅
    - [x] test_run_simple_message        # 简单消息处理 ✅
    - [x] test_run_adds_to_session       # 消息添加到会话 ✅
    - [x] test_run_returns_response      # 返回响应 ✅
    - [x] test_run_without_llm_provider  # 未设置 LLM 提供商 ✅

class TestAgentLoopToolCalls:
    - [x] test_run_with_single_tool_call   # 单次工具调用 ✅
    - [x] test_run_with_multiple_tool_calls # 多次工具调用 ✅
    - [x] test_run_reaches_max_iterations   # 达到最大迭代次数 ✅

class TestAgentLoopMemory:
    - [x] test_run_with_memory_enabled     # 启用记忆运行 ✅
    - [x] test_run_consolidates_memory     # 记忆整合 ✅

class TestAgentLoopEdgeCases:
    - [x] test_run_empty_message           # 空消息 ✅
    - [x] test_run_very_long_message       # 超长消息 ✅
    - [x] test_run_special_characters      # 特殊字符 ✅
    - [x] test_run_concurrent_sessions     # 并发会话 ✅

class TestCreateAgentLoop:
    - [x] test_create_agent_loop           # 创建 AgentLoop ✅
    - [x] test_create_agent_loop_has_tools # 包含内置工具 ✅

class TestAgentLoopIntegration:
    - [x] test_full_conversation_flow      # 完整对话流程 ✅
```

**测试结果**:
- 总计：17 个测试
- 通过：17 个
- 失败：0 个
- 覆盖率：AgentLoop 98%, Memory 45%, Session 60%

**修复问题**:
- 修复了 `memory.py` 的 `append_to_history` 方法以支持 Message 对象和字典两种格式
- 修复了 `context.py` 的导入路径（`..session` → `.session`）
- 修复了测试 fixture 中 SessionManager 参数名（`base_dir` → `storage_dir`）

**依赖**:
- MockLLMProvider fixture
- 测试工具组件

**预计时间**: 4 小时

---

### 2. LiteLLMProvider 测试

**文件**: `services/agent/tests/test_providers/test_litellm_provider.py`

**状态**: ✅ **已完成** (23 个测试全部通过)

**详细任务列表**:

**步骤 1: 分析 LiteLLMProvider 代码结构** ✅
- [x] 阅读 providers/litellm_provider.py 完整实现
- [x] 识别所有公共方法和属性
- [x] 确定需要 Mock 的外部依赖

**步骤 2: 创建测试文件结构** ✅
- [x] 创建测试文件 `tests/test_providers/test_litellm_provider.py`
- [x] 设置必要的 imports 和 fixtures

**步骤 3: TestLiteLLMProviderInit 测试类** ✅
- [x] test_init_default - 默认初始化测试
- [x] test_init_with_api_key - 带 API 密钥初始化
- [x] test_init_with_custom_params - 自定义参数初始化
- [x] test_setup_env - 环境变量设置测试

**步骤 4: TestLiteLLMProviderChat 测试类** ✅
- [x] test_chat_basic - 基础聊天测试
- [x] test_chat_with_tools - 带工具调用测试
- [x] test_chat_with_system_prompt - 带系统提示测试
- [x] test_chat_error_handling - 错误处理测试

**步骤 5: TestLiteLLMProviderParse 测试类** ✅
- [x] test_parse_simple_response - 简单响应解析
- [x] test_parse_tool_call_response - 工具调用响应解析
- [x] test_parse_empty_response - 空响应解析
- [x] test_parse_malformed_response - 格式错误响应解析

**步骤 6: TestMockLLMProvider 测试类** ✅
- [x] test_mock_chat - Mock 聊天测试
- [x] test_mock_chat_with_tool_calls - Mock 工具调用测试

**步骤 7: 运行测试并验证** ✅
- [x] 运行所有测试
- [x] 修复失败的测试
- [x] 验证覆盖率

**步骤 8: 更新文档和日志** ✅
- [x] 更新 test_todos.md 状态
- [x] 记录修复的问题

**测试结果**:
- 总计：23 个测试
- 通过：23 个
- 失败：0 个
- 覆盖率：LiteLLMProvider 96%

**测试场景覆盖**:
```
TestLiteLLMProviderInit:        5 个测试 ✅
TestLiteLLMProviderChat:        5 个测试 ✅
TestLiteLLMProviderParse:       4 个测试 ✅
TestMockLLMProvider:            3 个测试 ✅
TestCreateProvider:             2 个测试 ✅
TestLLMResponse:                2 个测试 ✅
TestChatMessage:                2 个测试 ✅
```

**修复的问题**:
- 修复了 `mock_litellm_with_tool_calls` fixture 中 function.name 的 Mock 设置方式

**预计时间**: 3 小时

---

### 3. 测试夹具（Fixtures）

**文件**: `services/agent/tests/conftest.py`（增强现有文件）

**待添加**:

```python
# Mock LLM Provider
- [ ] mock_llm_provider()         # 基础 Mock
- [ ] mock_llm_with_tool_call()   # 返回工具调用
- [ ] mock_llm_with_content()     # 返回文本内容
- [ ] mock_llm_error()            # 模拟错误

# 测试组件
- [ ] agent_loop()                # 完整 AgentLoop
- [ ] agent_loop_with_tools()     # 带工具的 AgentLoop
- [ ] sample_messages()           # 示例消息列表
```

**预计时间**: 2 小时

---

## P1 - 重要功能测试（下周）

### 4. ContextBuilder 测试

**文件**: `services/agent/tests/test_agent/test_context.py`

**状态**: ✅ **已完成** (32 个测试全部通过)

**详细任务列表**:

**步骤 1: 分析 ContextBuilder 代码结构** ✅
- [x] 阅读 agent/context.py 完整实现
- [x] 识别所有公共方法和属性
- [x] 确定测试依赖

**步骤 2: 创建测试文件结构** ✅
- [x] 创建测试文件 `tests/test_agent/test_context.py`
- [x] 设置必要的 imports 和 fixtures

**步骤 3: TestContextBuilderInit 测试类** ✅
- [x] test_init_default - 默认初始化
- [x] test_init_with_custom_prompt - 自定义系统提示
- [x] test_init_with_workspace - 工作区设置
- [x] test_init_with_agent_name - 代理名称

**步骤 4: TestContextBuilderBuild 测试类** ✅
- [x] test_build_empty_context - 空上下文
- [x] test_build_with_messages - 带消息
- [x] test_build_with_memory - 带记忆
- [x] test_build_with_system_prompt - 带系统提示
- [x] test_build_with_tools - 带工具列表

**步骤 5: TestContextBuilderSystemPrompt 测试类** ✅
- [x] test_build_system_prompt_identity - 身份信息
- [x] test_build_system_prompt_memory - 记忆部分
- [x] test_build_system_prompt_tools - 工具部分
- [x] test_build_system_prompt_workspace - 工作区信息

**步骤 6: TestContextBuilderEdgeCases 测试类** ✅
- [x] test_build_truncates_long_messages - 截断长消息
- [x] test_build_limits_history_count - 限制历史消息数
- [x] test_build_handles_empty_memory - 处理空记忆
- [x] test_build_handles_empty_tools - 处理空工具
- [x] test_build_with_special_characters - 特殊字符

**步骤 7: TestContextBuilderGuidanceFiles 测试类** ✅
- [x] test_load_guidance_files_exists - 加载存在的引导文件
- [x] test_load_guidance_files_not_exists - 加载不存在的引导文件
- [x] test_guidance_files_priority - 引导文件优先级

**步骤 8: TestContextBuilderConfig 测试类** ✅
- [x] test_config_default - 默认配置
- [x] test_config_custom - 自定义配置
- [x] test_config_build - 配置创建实例

**步骤 9: TestHelperFunctions 测试类** ✅
- [x] test_create_context_builder - 创建 ContextBuilder
- [x] test_create_context_builder_with_prompt - 带提示创建
- [x] test_default_system_prompt - 默认系统提示

**步骤 10: TestFormatTools 测试类** ✅
- [x] test_format_tools_empty - 空工具列表
- [x] test_format_tools_single - 单个工具
- [x] test_format_tools_multiple - 多个工具

**步骤 11: TestBuildIdentity 测试类** ✅
- [x] test_build_identity - 身份信息
- [x] test_build_identity_with_custom_agent_name - 自定义代理名称

**步骤 12: 运行测试并验证** ✅
- [x] 运行所有测试
- [x] 验证覆盖率

**步骤 13: 更新文档和日志** ✅
- [x] 更新 test_todos.md 状态
- [x] 记录修复的问题

**测试结果**:
- 总计：32 个测试
- 通过：32 个
- 失败：0 个
- 覆盖率：ContextBuilder 97%

**测试场景覆盖**:
```
TestContextBuilderInit:           4 个测试 ✅
TestContextBuilderBuild:          5 个测试 ✅
TestContextBuilderSystemPrompt:   4 个测试 ✅
TestContextBuilderEdgeCases:      5 个测试 ✅
TestContextBuilderGuidanceFiles:  3 个测试 ✅
TestContextBuilderConfig:         3 个测试 ✅
TestHelperFunctions:              3 个测试 ✅
TestFormatTools:                  3 个测试 ✅
TestBuildIdentity:                2 个测试 ✅
```

**预计时间**: 2 小时

---

### 5. 集成测试

**目录**: `services/agent/tests/test_integration/`

**文件**: `test_agent_flow.py`

**状态**: 🔴 进行中

**详细任务列表**:

**步骤 1: 分析集成测试依赖** ✅
- [x] 确认需要集成的组件 (AgentLoop, Session, Memory, Tools)
- [x] 准备 Mock 组件和真实组件混合方案
- [x] 创建测试目录

**步骤 2: 创建测试目录和文件** ✅
- [x] 创建 `tests/test_integration/` 目录
- [x] 创建 `tests/test_integration/__init__.py`
- [x] 创建 `tests/test_integration/test_agent_flow.py`

**步骤 3: TestEndToEndFlow 测试类** ✅
- [x] test_user_message_to_response - 完整流程
- [x] test_conversation_with_history - 带历史对话
- [x] test_tool_execution_flow - 工具执行流程
- [x] test_memory_persistence - 记忆持久化
- [x] test_session_management - 会话管理

**步骤 4: TestAPIIntegration 测试类** ✅
- [x] test_chat_api_endpoint - API 端点集成
- [x] test_session_api_flow - 会话 API 流程
- [x] test_memory_api_flow - 记忆 API 流程

**步骤 5: TestComponentIntegration 测试类** ✅
- [x] test_agent_with_session - Agent + Session 集成
- [x] test_agent_with_memory - Agent + Memory 集成
- [x] test_agent_with_tools - Agent + Tools 集成

**步骤 6: TestMultiTurnConversation 测试类** ✅
- [x] test_multi_turn_basic - 基础多轮对话
- [x] test_multi_turn_context_awareness - 上下文感知多轮对话

**步骤 7: TestConcurrentSessions 测试类** ✅
- [x] test_concurrent_sessions - 并发会话处理

**步骤 8: 运行测试并验证** ✅
- [x] 运行所有测试
- [x] 验证覆盖率

**步骤 9: 更新文档和日志** ✅
- [x] 更新 test_todos.md 状态
- [x] 记录修复的问题

**测试结果**:
- 总计：14 个测试
- 通过：14 个
- 失败：0 个
- 覆盖率：AgentLoop 85%, Session 79%, Tools 85%

**测试场景覆盖**:
```
TestEndToEndFlow:           5 个测试 ✅
TestAPIIntegration:         3 个测试 ✅
TestComponentIntegration:   3 个测试 ✅
TestMultiTurnConversation:  2 个测试 ✅
TestConcurrentSessions:     1 个测试  ✅
```

**预计时间**: 4 小时

---

### 6. 配置系统测试扩展

**文件**: `services/agent/tests/test_config/test_config.py`

**测试场景**:

```
class TestConfigManager:
    - [ ] test_load_default_config
    - [ ] test_load_custom_config
    - [ ] test_save_config
    - [ ] test_update_config
    - [ ] test_config_validation
```

**预计时间**: 1.5 小时

---

## P2 - 增强功能测试（后续）

### 7. 工具测试扩展

**目录**: `services/agent/tests/test_tools/`

**状态**: ✅ **已完成** (46 个测试全部通过)

**已创建文件**:
- ✅ test_file_tools.py (13 个测试)
- ✅ test_shell_tools.py (6 个测试)
- ✅ test_web_tools.py (9 个测试)
- ✅ test_tool_base.py (18 个测试)

**测试结果**:
- 总计：46 个测试
- 通过：46 个 ✅
- 失败：0 个

**测试覆盖**:
```
TestFileRead:                4 个测试 ✅
TestFileWrite:               4 个测试 ✅
TestFileList:                3 个测试 ✅
TestFileOperations:          2 个测试 ✅
TestShellExec:               4 个测试 ✅
TestShellExecSafe:           2 个测试 ✅
TestWebSearch:               3 个测试 ✅
TestWebFetch:                4 个测试 ✅
TestNetworkTools:            1 个测试  ✅
TestToolResult:              4 个测试 ✅
TestSimpleTool:              4 个测试 ✅
TestToolRegistry:            7 个测试 ✅
TestToolRegistryList:        3 个测试 ✅
```

**修复说明**:
- 修复了测试断言逻辑
- `ToolRegistry.execute()` 返回字符串内容而非 `ToolResult` 对象
- 错误情况通过 `RuntimeError` 异常处理

**预计时间**: 6 小时

---

### 8. Provider 测试扩展

**目录**: `services/agent/tests/test_providers/`

**状态**: ✅ **已完成** (35 个测试全部通过)

**已创建文件**:
- ✅ test_provider_registry.py (35 个测试)

**测试结果**:
- 总计：35 个测试
- 通过：35 个 ✅
- 失败：0 个

**测试覆盖**:
```
TestProviderSpec:                    4 个测试 ✅
TestGetProviderFunctions:            7 个测试 ✅
TestGetProviderForModel:             7 个测试 ✅
TestFormatModelName:                 5 个测试 ✅
TestGetPresetModel:                  4 个测试 ✅
TestProvidersRegistry:               8 个测试 ✅
```

**测试场景**:
- ProviderSpec 初始化和验证
- 模型名称匹配
- 提供商查找（按名称、按模型）
- 模型名称格式化
- 预设模型查询
- 注册表完整性验证

**预计时间**: 4 小时

---

### 9. 性能测试

**目录**: `services/agent/tests/test_performance/`

**测试场景**:

```
- [ ] test_agent_loop_performance.py  # AgentLoop 性能
- [ ] test_memory_search_performance.py # 记忆搜索性能
- [ ] test_session_load_performance.py  # 会话加载性能
```

**预计时间**: 3 小时

---

## 前端测试待办

### 10. 组件测试扩展

**目录**: `apps/desktop/src/components/`

**待添加**:

```
- [ ] ChatWindow.test.tsx       # 聊天窗口组件
- [ ] SessionList.test.tsx      # 会话列表组件
- [ ] Settings.test.tsx         # 设置组件
- [ ] MemoryView.test.tsx       # 记忆视图组件
```

**预计时间**: 4 小时

---

### 11. Hooks 测试

**目录**: `apps/desktop/src/hooks/`

**待添加**:

```
- [ ] useChat.test.ts           # 聊天 Hook
- [ ] useSession.test.ts        # 会话 Hook
- [ ] useMemory.test.ts         # 记忆 Hook
```

**预计时间**: 3 小时

---

### 12. 上下文测试

**目录**: `apps/desktop/src/contexts/`

**待添加**:

```
- [ ] ChatContext.test.tsx      # 聊天上下文
- [ ] ConfigContext.test.tsx    # 配置上下文
```

**预计时间**: 2 小时

---

## Rust 测试待办

### 13. Tauri 命令测试

**目录**: `apps/desktop/src-tauri/src/`

**待添加**:

```rust
// 在命令实现文件中添加 #[cfg(test)] 模块
- [ ] test_chat_command.rs      # 聊天命令
- [ ] test_session_commands.rs  # 会话命令
- [ ] test_memory_commands.rs   # 记忆命令
```

**预计时间**: 3 小时

---

## 文档待办

### 14. 测试文档更新

- [ ] 更新 `docs/测试/测试指南.md` - 添加新测试示例
- [ ] 创建 `docs/测试/覆盖率报告.md` - 覆盖率统计
- [x] 创建 `docs/测试/CI 配置.md` - CI/CD 测试流程 ✅ (已配置 `.github/workflows/test.yml`)

**CI/CD 状态**: ✅ **已完成**
- GitHub Actions 工作流：`.github/workflows/test.yml`
- 前端测试：Vitest + Codecov
- Python 测试：pytest + Codecov
- Rust 测试：cargo test + Codecov

---

## 测试运行命令

### Python 后端
```bash
cd services/agent

# 运行所有测试
pytest

# 运行特定模块
pytest tests/test_agent/ -v
pytest tests/test_providers/ -v
pytest tests/test_integration/ -v

# 生成覆盖率报告
pytest --cov=agent --cov=providers --cov-report=html

# 监视模式
pytest -w
```

### 前端
```bash
cd apps/desktop

# 运行所有测试
pnpm test:run

# 监视模式
pnpm test

# 可视化 UI
pnpm test:ui

# 生成覆盖率
pnpm test:coverage
```

### Rust
```bash
cd apps/desktop/src-tauri

# 运行所有测试
cargo test

# 显示输出
cargo test -- --nocapture
```

---

## 覆盖率目标

| 模块 | 当前 | 短期目标 | 长期目标 |
|------|------|---------|---------|
| AgentLoop | 0% | 80% | 90% |
| LiteLLMProvider | 0% | 75% | 85% |
| Session/ Memory | 80% | 85% | 90% |
| Tools | 30% | 60% | 80% |
| API | 60% | 75% | 85% |
| UI Components | 70% | 75% | 80% |

---

## 里程碑

### 里程碑 1 - 核心测试完成（本周）
- [x] 测试文档完成
- [ ] AgentLoop 测试完成
- [ ] LiteLLMProvider 测试完成
- [ ] 测试夹具完善

### 里程碑 2 - 重要功能测试（下周）
- [ ] ContextBuilder 测试完成
- [ ] 集成测试完成
- [ ] 配置系统测试完成

### 里程碑 3 - 全面覆盖（本月）
- [ ] 所有 P2 测试完成
- [ ] 前端组件测试完成
- [ ] Rust 命令测试完成
- [ ] 覆盖率达到目标

---

*最后更新：2026 年 2 月 20 日*

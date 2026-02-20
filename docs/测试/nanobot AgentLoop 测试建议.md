# nanobot AgentLoop 完整测试建议

**创建日期**: 2026-02-20  
**参考架构**: nanobot AgentLoop 核心实现分析

---

## 一、测试分层策略

```
                    ╱¯¯¯¯¯¯¯¯¯¯¯╲
                   ╱  E2E 测试   ╲
                  ╱  (集成测试)    ╲
                 ╱─────────────────╲
                ╱   组件集成测试     ╲
               ╱─────────────────────╲
              ╱      单元测试          ╲
             ╱─────────────────────────╲
            ╱                           ╲
           ╱─────────────────────────────╲
```

**测试金字塔**:
- **底层**: 单元测试（最多）- 测试单个组件
- **中层**: 组件集成测试 - 测试组件间交互
- **顶层**: E2E 测试（最少）- 测试完整流程

---

## 二、核心架构组件

### 2.1 组件依赖图

```
┌─────────────────────────────────────────────────────────────┐
│                            AgentLoop                         │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ SessionManager  │  │   MemoryStore   │  │ToolRegistry │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘ │
│           └────────────────────┼───────────────────┘        │
│                                │                             │
│                     ┌──────────┴──────────┐                  │
│                     │   ContextBuilder    │                  │
│                     └──────────┬──────────┘                  │
│                                │                             │
│                     ┌──────────┴──────────┐                  │
│                     │   LiteLLMProvider   │                  │
│                     └─────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心文件清单

| 组件 | 文件路径 | 职责 |
|------|----------|------|
| **AgentLoop** | `services/agent/agent/loop.py` | 核心代理处理引擎 |
| **ContextBuilder** | `services/agent/agent/context.py` | 构建 LLM 上下文 |
| **SessionManager** | `services/agent/agent/session.py` | 会话管理 |
| **MemoryStore** | `services/agent/agent/memory.py` | 双层记忆存储 |
| **ToolRegistry** | `services/agent/agent/tools/registry.py` | 工具注册与执行 |
| **LiteLLMProvider** | `services/agent/providers/litellm_provider.py` | LLM 调用封装 |
| **FastAPI Main** | `services/agent/main.py` | API 入口 |

---

## 三、单元测试层

### 3.1 ContextBuilder 测试

**文件**: `tests/test_agent/test_context.py`

```python
class TestContextBuilder:
    # 1. 系统提示词构建
    async def test_build_system_prompt_identity(self):
        """测试身份信息正确注入"""
        
    async def test_build_system_prompt_memory(self):
        """测试长期记忆正确注入"""
        
    async def test_build_system_prompt_tools(self):
        """测试工具摘要正确格式化"""
    
    # 2. 引导文件加载
    async def test_load_guidance_agents_md(self):
        """测试 AGENTS.md 优先级最高"""
        
    async def test_load_guidance_soul_md(self):
        """测试 SOUL.md 作为备选"""
        
    async def test_load_guidance_user_md(self):
        """测试 USER.md 作为最后备选"""
    
    # 3. 上下文消息构建
    async def test_build_context_with_messages(self):
        """测试历史消息正确添加到上下文"""
        
    async def test_build_context_message_limit(self):
        """测试消息数量限制（50 条）"""
```

### 3.2 SessionManager 测试

**文件**: `tests/test_agent/test_session.py`

```python
class TestSessionManager:
    # 1. 会话创建
    async def test_get_or_create_new_session(self):
        """测试创建新会话"""
        
    async def test_get_or_create_with_session_id(self):
        """测试通过 session_id 获取会话"""
    
    # 2. 会话持久化
    async def test_save_session_jsonl(self):
        """测试会话保存为 JSONL 格式"""
        
    async def test_load_session_from_disk(self):
        """测试从磁盘加载会话"""
    
    # 3. 缓存管理
    async def test_session_cached_in_memory(self):
        """测试会话在内存中缓存"""
        
    async def test_session_cache_updated_on_save(self):
        """测试保存时会更新缓存"""
    
    # 4. 会话列表
    async def test_list_sessions(self):
        """测试列出所有会话"""
        
    async def test_list_sessions_by_user(self):
        """测试按用户筛选会话"""
```

### 3.3 MemoryStore 测试

**文件**: `tests/test_agent/test_memory.py`

```python
class TestMemoryStore:
    # 1. 记忆文件管理
    async def test_ensure_memory_files_created(self):
        """测试记忆文件自动创建"""
        
    async def test_get_memory_empty_file(self):
        """测试读取空记忆文件"""
    
    # 2. 记忆更新
    async def test_update_memory_append(self):
        """测试追加模式更新记忆"""
        
    async def test_update_memory_with_section(self):
        """测试按章节更新记忆"""
    
    # 3. 历史记录
    async def test_append_to_history(self):
        """测试追加对话历史"""
        
    async def test_search_history(self):
        """测试搜索历史记录"""
    
    # 4. 记忆整合
    async def test_consolidate_memory(self):
        """测试消息归档到历史记录"""
```

### 3.4 ToolRegistry 测试

**文件**: `tests/test_tools/test_registry.py`

```python
class TestToolRegistry:
    # 1. 工具注册
    def test_register_tool(self):
        """测试注册单个工具"""
        
    def test_register_multiple_tools(self):
        """测试注册多个工具"""
    
    # 2. 工具获取
    def test_get_tool_exists(self):
        """测试获取已注册工具"""
        
    def test_get_tool_not_exists(self):
        """测试获取不存在的工具返回 None"""
    
    # 3. 工具 Schema
    def test_get_tool_schemas(self):
        """测试获取所有工具 schema"""
        
    def test_tool_schema_format(self):
        """测试 schema 符合 OpenAI 格式"""
    
    # 4. 工具执行
    async def test_execute_tool_success(self):
        """测试工具执行成功"""
        
    async def test_execute_tool_not_found(self):
        """测试执行不存在的工具抛出异常"""
        
    async def test_execute_tool_with_error(self):
        """测试工具执行失败时的错误处理"""
```

### 3.5 LiteLLMProvider 测试

**文件**: `tests/test_providers/test_litellm.py`

```python
class TestLiteLLMProvider:
    # 1. 初始化
    def test_init_with_model(self):
        """测试通过模型名称初始化"""
        
    def test_init_with_api_key(self):
        """测试通过 API Key 初始化"""
        
    def test_init_with_base_url(self):
        """测试通过 API Base URL 初始化"""
    
    # 2. Provider 检测
    def test_detect_provider_zai(self):
        """测试检测 Z.ai provider"""
        
    def test_detect_provider_anthropic(self):
        """测试检测 Anthropic provider"""
    
    # 3. 模型名称格式化
    def test_format_model_name(self):
        """测试模型名称格式化"""
        
    def test_format_model_name_already_prefixed(self):
        """测试已带前缀的模型名称"""
    
    # 4. 响应解析
    def test_parse_response_with_content(self):
        """测试解析带内容的响应"""
        
    def test_parse_response_with_tool_calls(self):
        """测试解析带工具调用的响应"""
        
    def test_parse_response_with_usage(self):
        """测试解析 token 使用信息"""
```

---

## 四、组件集成测试层

### 4.1 AgentLoop 核心循环测试

**文件**: `tests/test_agent/test_loop.py`

```python
class TestAgentLoop:
    @pytest.fixture
    async def agent_loop(self):
        """创建配置好的 AgentLoop 实例"""
    
    # 1. 基本对话流程
    async def test_run_simple_message(self, agent_loop):
        """测试简单消息处理流程"""
        response = await agent_loop.run(
            message="你好",
            session_id="test-1",
            user_id="test-user"
        )
        assert response.content != ""
        assert response.tool_calls == []
    
    # 2. 工具调用流程
    async def test_run_with_tool_call(self, agent_loop):
        """测试 LLM 调用工具的场景"""
        response = await agent_loop.run(
            message="帮我读取文件 test.txt",
            session_id="test-2",
            user_id="test-user"
        )
        assert len(response.tool_calls) > 0
        assert response.content != ""
    
    # 3. 多轮对话
    async def test_run_conversation_history(self, agent_loop):
        """测试多轮对话历史保留"""
        await agent_loop.run("第一句话", "test-3", "user-1")
        await agent_loop.run("第二句话", "test-3", "user-1")
        response = await agent_loop.run("第三句话", "test-3", "user-1")
    
    # 4. 记忆整合
    async def test_run_memory_consolidation(self, agent_loop):
        """测试消息过多时的记忆整合"""
        for i in range(60):
            await agent_loop.run(f"消息{i}", "test-4", "user-1")
    
    # 5. 最大迭代次数保护
    async def test_run_max_iterations(self, agent_loop):
        """测试达到最大迭代次数时的处理"""
        response = await agent_loop.run(
            message="无限循环任务",
            session_id="test-5",
            user_id="test-user"
        )
        assert response.metadata.get("error") == "max_iterations"
    
    # 6. 错误处理
    async def test_run_llm_error(self, agent_loop):
        """测试 LLM 调用失败时的错误处理"""
        
    # 7. 会话持久化
    async def test_run_session_persisted(self, agent_loop):
        """测试会话被正确持久化"""
        await agent_loop.run("测试", "test-7", "user-1")
```

### 4.2 组件集成测试

```python
class TestContextBuilderIntegration:
    async def test_build_context_with_memory(self):
        """测试 ContextBuilder 正确加载 MemoryStore 的记忆"""
        
    async def test_build_context_with_tools(self):
        """测试 ContextBuilder 正确格式化 ToolRegistry 的工具"""

class TestAgentLoopSessionIntegration:
    async def test_session_created_on_first_message(self):
        """测试首次消息时创建会话"""
        
    async def test_session_loaded_on_subsequent_messages(self):
        """测试后续消息时加载已有会话"""
        
    async def test_session_messages_accumulated(self):
        """测试会话中消息累积"""
```

---

## 五、E2E 端到端测试层

### 5.1 FastAPI 端点测试

**文件**: `tests/test_api/test_chat.py`

```python
class TestChatEndpoint:
    @pytest.fixture
    def client(self):
        """创建测试用 FastAPI 测试客户端"""
    
    # 1. 基本对话
    def test_chat_simple_message(self, client):
        """测试简单对话"""
        response = client.post("/api/chat", json={"message": "你好"})
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["content"] != ""
    
    # 2. 带会话 ID
    def test_chat_with_session_id(self, client):
        """测试指定会话 ID"""
        response = client.post("/api/chat", json={
            "message": "你好",
            "session_id": "custom-session-123"
        })
        assert response.status_code == 200
    
    # 3. 带用户 ID
    def test_chat_with_user_id(self, client):
        """测试指定用户 ID"""
        response = client.post("/api/chat", json={
            "message": "你好",
            "user_id": "user-456"
        })
        assert response.status_code == 200
    
    # 4. 工具调用场景
    def test_chat_file_read(self, client, tmp_path):
        """测试文件读取工具调用"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("测试内容")
        
        response = client.post("/api/chat", json={
            "message": f"读取文件 {test_file}",
            "workspace": str(tmp_path)
        })
        assert response.status_code == 200
    
    # 5. 多轮对话
    def test_chat_conversation_flow(self, client):
        """测试多轮对话流程"""
        session_id = "multi-turn-1"
        
        r1 = client.post("/api/chat", json={
            "message": "我的名字是张三",
            "session_id": session_id
        })
        
        r2 = client.post("/api/chat", json={
            "message": "我叫什么名字？",
            "session_id": session_id
        })
        data = r2.json()
        assert "张三" in data["content"]
    
    # 6. 错误处理
    def test_chat_invalid_request(self, client):
        """测试无效请求处理"""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422
    
    # 7. 并发请求
    def test_chat_concurrent_requests(self, client):
        """测试并发请求处理"""
```

### 5.2 真实场景测试

```python
class TestRealWorldScenarios:
    """真实使用场景测试"""
    
    def test_scenario_code_review(self, client):
        """场景：代码审查"""
        
    def test_scenario_file_organization(self, client):
        """场景：文件整理"""
        
    def test_scenario_research_task(self, client):
        """场景：研究任务（多轮工具调用）"""
        
    def test_scenario_debugging_help(self, client):
        """场景：调试帮助"""
```

---

## 六、性能测试

### 6.1 基准测试

```python
class TestPerformance:
    def test_response_time_p50(self, client):
        """测试 P50 响应时间 < 2 秒"""
        
    def test_response_time_p95(self, client):
        """测试 P95 响应时间 < 5 秒"""
        
    def test_concurrent_users_10(self, client):
        """测试 10 个并发用户"""
        
    def test_memory_usage_under_load(self):
        """测试负载下的内存使用"""
```

---

## 七、测试优先级与排期

### 第一阶段：核心单元测试（1-2 天）

| 优先级 | 测试类 | 预计用例数 |
|--------|--------|-----------|
| P0 | `TestContextBuilder` | 8 |
| P0 | `TestSessionManager` | 8 |
| P0 | `TestMemoryStore` | 7 |
| P0 | `TestToolRegistry` | 9 |
| P1 | `TestLiteLLMProvider` | 9 |

### 第二阶段：集成测试（2-3 天）

| 优先级 | 测试类 | 预计用例数 |
|--------|--------|-----------|
| P0 | `TestAgentLoop` | 7 |
| P1 | `TestContextBuilderIntegration` | 2 |
| P1 | `TestAgentLoopSessionIntegration` | 3 |

### 第三阶段：E2E 场景测试（1-2 天）

| 优先级 | 测试类 | 预计用例数 |
|--------|--------|-----------|
| P0 | `TestChatEndpoint` | 7 |
| P1 | `TestRealWorldScenarios` | 4 |
| P2 | `TestPerformance` | 4 |

---

## 八、测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| `agent/loop.py` | 90% | ⚠️ 待测试 |
| `agent/context.py` | 90% | ⚠️ 待测试 |
| `agent/session.py` | 85% | ⚠️ 待测试 |
| `agent/memory.py` | 85% | ⚠️ 待测试 |
| `agent/tools/registry.py` | 90% | ⚠️ 待测试 |
| `providers/litellm_provider.py` | 80% | ⚠️ 待测试 |
| `main.py` (API) | 75% | ⚠️ 待测试 |

---

## 九、测试辅助工具

### 9.1 Mock 工具

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_llm_provider():
    """模拟 LLM Provider"""
    provider = MagicMock()
    provider.chat = AsyncMock(return_value=LLMResponse(
        content="测试响应",
        tool_calls=[],
        model="test-model",
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    ))
    return provider

@pytest.fixture
def mock_tool_registry():
    """模拟 Tool Registry"""
    registry = MagicMock()
    registry.get_tool_schemas = MagicMock(return_value=[...])
    registry.execute = AsyncMock(return_value="工具执行结果")
    return registry
```

### 9.2 测试数据工厂

```python
# tests/factories.py
from agent.session import Session, Message

class SessionFactory:
    @staticmethod
    def create(session_id="test-1", user_id="user-1", messages=None):
        return Session(
            id=session_id,
            user_id=user_id,
            messages=messages or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

class MessageFactory:
    @staticmethod
    def user_message(content="测试消息"):
        return Message(
            role="user",
            content=content,
            timestamp=datetime.now().isoformat()
        )
    
    @staticmethod
    def assistant_message(content="助手响应"):
        return Message(
            role="assistant",
            content=content,
            timestamp=datetime.now().isoformat()
        )
```

---

## 十、核心流程图

### 10.1 消息处理流程

```
用户消息 → FastAPI /api/chat → AgentLoop.run()
                                    │
                                    ├─→ SessionManager.get_or_create()
                                    ├─→ Session.add_message()
                                    ├─→ _build_context()
                                    │       │
                                    │       ├─→ MemoryStore.get_memory()
                                    │       └─→ ContextBuilder.build()
                                    │
                                    └─→ _run_agent_loop()
                                            │
                                            ├─→ ToolRegistry.get_tool_schemas()
                                            ├─→ LiteLLMProvider.chat()
                                            │
                                            ├─→ 有工具调用？
                                            │   ├─→ 是 → _execute_tools_parallel()
                                            │   │         │
                                            │   │         └─→ ToolRegistry.execute()
                                            │   │
                                            │   └─→ 否 → 返回 AgentResponse
                                            │
                                            └─→ Session.add_message()
                                                SessionManager.save()
```

### 10.2 错误处理流程

```
┌─────────────────────────────────────────────────────────────┐
│                        错误处理流程                          │
└─────────────────────────────────────────────────────────────┘

1. LLM 调用失败
   AgentLoop._call_llm()
         │
         ▼
   LiteLLMProvider.chat()
         │
         ├─→ try: acompletion() ──→ 成功 ──→ _parse_response()
         │
         └─→ except Exception ──→ logger.error()
                                   │
                                   ▼
                              返回 LLMResponse(content="Error: ...")

2. 工具执行失败
   AgentLoop._execute_single_tool()
         │
         ├─→ try: tool_registry.execute() ──→ 成功 ──→ 返回结果
         │
         └─→ except Exception ──→ 返回 {success: False, content: "Error: ..."}
                                   │
                                   ▼
                              将错误作为 tool result 传给 LLM

3. 达到最大迭代次数
   AgentLoop._run_agent_loop()
         │
         for iteration in range(max_iterations):
             │
             ├─→ 有工具调用 ──→ 执行工具 ──→ continue
             │
             └─→ 无工具调用 ──→ 返回响应
         
         循环结束 → 返回错误响应
```

---

## 十一、参考文档

- [nanobot AgentLoop 核心实现分析报告](./nanobot-AgentLoop 分析.md)
- [测试指南.md](./测试指南.md)
- [核心流程测试设计.md](./核心流程测试设计.md)

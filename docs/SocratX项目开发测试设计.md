# SocratX 项目开发测试设计

> 本文档定义 SocratX 项目的 TDD（测试驱动开发）实施方案，确保代码质量和项目可持续维护。

---

## 一、测试框架选型

| 模块 | 测试框架 | 版本 | 理由 |
|------|---------|------|------|
| **React 前端** | Vitest + React Testing Library | 最新 | Vite 原生支持，速度快，与 Vite 配置无缝集成 |
| **Tauri/Rust** | Rust 内置测试 | - | 官方推荐，无需额外配置 |
| **Python 后端** | pytest + pytest-asyncio | 7.0+ | Python 生态标准，异步支持完善 |
| **E2E 测试** | Playwright | 最新 | 跨平台 UI 自动化，支持所有主流浏览器 |

---

## 二、测试目录结构

```
SocratX/
├── apps/
│   └── desktop/
│       ├── src/
│       │   ├── components/
│       │   │   ├── chat/
│       │   │   │   ├── ChatInput.tsx
│       │   │   │   ├── ChatInput.test.tsx      # 输入框测试
│       │   │   │   ├── ChatMessage.tsx
│       │   │   │   ├── ChatMessage.test.tsx    # 消息显示测试
│       │   │   │   ├── ChatContainer.tsx
│       │   │   │   └── ChatContainer.test.tsx  # 容器组件测试
│       │   │   └── ui/
│       │   │       ├── button.tsx
│       │   │       └── button.test.tsx
│       │   ├── hooks/
│       │   │   ├── useChat.ts
│       │   │   └── useChat.test.ts
│       │   ├── contexts/
│       │   │   ├── ThemeContext.tsx
│       │   │   └── ThemeContext.test.tsx
│       │   ├── lib/
│       │   │   ├── api.ts
│       │   │   ├── api.test.ts                 # API 调用测试
│       │   │   └── utils.ts
│       │   │   └── utils.test.ts               # 工具函数测试
│       │   └── test/
│       │       └── setup.ts                    # 测试全局配置
│       └── src-tauri/
│           └── src/
│               ├── main.rs
│               ├── lib.rs                      # 包含 Rust 测试
│               ├── sidecar.rs
│               └── commands.rs
│
├── services/
│   └── agent/
│       ├── agent/
│       │   ├── loop.py
│       │   ├── context.py
│       │   ├── memory.py
│       │   ├── session.py
│       │   └── tools/
│       │       ├── registry.py
│       │       ├── file.py
│       │       ├── shell.py
│       │       └── web.py
│       ├── providers/
│       │   ├── registry.py
│       │   └── litellm_provider.py
│       ├── config/
│       │   ├── schema.py
│       │   └── loader.py
│       ├── main.py
│       └── tests/                              # Python 测试目录
│           ├── conftest.py                     # pytest 配置
│           ├── test_main.py
│           ├── test_agent/
│           │   ├── test_loop.py
│           │   ├── test_context.py
│           │   ├── test_memory.py
│           │   ├── test_session.py
│           │   └── test_tools/
│           │       ├── test_registry.py
│           │       ├── test_file.py
│           │       ├── test_shell.py
│           │       └── test_web.py
│           ├── test_providers/
│           │   └── test_litellm_provider.py
│           └── test_config/
│               └── test_schema.py
│
└── tests/
    └── e2e/                                    # E2E 测试
        ├── conftest.py
        ├── test_chat_flow.py
        └── test_settings.py
```

---

## 三、TDD 开发流程

### 3.1 红 - 绿 - 重构循环

```
┌─────────────────────────────────────────────────────────┐
│  1. 红 (Red)                                             │
│     - 先写失败的测试用例                                  │
│     - 明确需求和预期行为                                  │
│     - 测试失败是预期的                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. 绿 (Green)                                           │
│     - 写最少代码让测试通过                                │
│     - 不追求完美，先实现功能                              │
│     - 可以快速迭代                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. 重构 (Refactor)                                      │
│     - 优化代码结构，保持测试通过                          │
│     - 消除重复，提升可读性                                │
│     - 确保所有测试仍然通过                                │
└─────────────────────────────────────────────────────────┘
```

### 3.2 开发节奏

| 步骤 | 活动 | 时间占比 |
|------|------|---------|
| 1. 写测试 | 明确需求，编写失败的测试 | 30% |
| 2. 实现功能 | 写最少代码通过测试 | 40% |
| 3. 重构 | 优化代码，保持测试通过 | 30% |

---

## 四、前端测试配置（Vitest）

### 4.1 安装依赖

```bash
cd apps/desktop
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom happy-dom @vitest/ui @vitest/coverage-v8
```

### 4.2 Vite 配置

**`apps/desktop/vite.config.ts`**：

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    include: ['**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
})
```

### 4.3 测试全局配置

**`apps/desktop/src/test/setup.ts`**：

```typescript
import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// 每个测试后清理 DOM
afterEach(() => {
  cleanup()
})
```

### 4.4 测试工具函数

**`apps/desktop/src/lib/utils.test.ts`**：

```typescript
import { describe, it, expect } from 'vitest'
import { cn, formatTime, truncate } from './utils'

describe('utils', () => {
  describe('cn', () => {
    it('合并多个类名', () => {
      expect(cn('a', 'b', 'c')).toBe('a b c')
    })

    it('处理条件类名', () => {
      expect(cn('a', true && 'b', false && 'c')).toBe('a b')
    })

    it('处理 Tailwind 合并', () => {
      expect(cn('px-2', 'px-4')).toBe('px-4')
    })
  })

  describe('formatTime', () => {
    it('格式化时间戳', () => {
      const result = formatTime(1708000000000)
      expect(result).toMatch(/\d{2}:\d{2}/)
    })

    it('显示今天/昨天', () => {
      // TODO: 实现具体测试
    })
  })

  describe('truncate', () => {
    it('截断长文本', () => {
      expect(truncate('Hello World', 5)).toBe('He...')
    })

    it('不截断短文本', () => {
      expect(truncate('Hi', 10)).toBe('Hi')
    })
  })
})
```

### 4.5 测试 UI 组件

**`apps/desktop/src/components/chat/ChatInput.test.tsx`**：

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { ChatInput } from './ChatInput'

describe('ChatInput', () => {
  const defaultProps = {
    onSend: vi.fn(),
    disabled: false,
    placeholder: '输入消息...',
  }

  it('渲染输入框', () => {
    render(<ChatInput {...defaultProps} />)
    expect(screen.getByPlaceholderText('输入消息...')).toBeInTheDocument()
  })

  it('渲染发送按钮', () => {
    render(<ChatInput {...defaultProps} />)
    expect(screen.getByRole('button', { name: /发送/i })).toBeInTheDocument()
  })

  it('点击发送按钮触发回调', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.type(screen.getByPlaceholderText('输入消息...'), 'Hello')
    await user.click(screen.getByRole('button', { name: /发送/i }))

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello')
  })

  it('发送后清空输入框', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    const input = screen.getByPlaceholderText('输入消息...')
    await user.type(input, 'Hello')
    await user.click(screen.getByRole('button', { name: /发送/i }))

    expect(input).toHaveValue('')
  })

  it('禁用状态下无法发送', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} disabled />)

    expect(screen.getByRole('button', { name: /发送/i })).toBeDisabled()
  })

  it('按 Enter 键发送消息', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.type(screen.getByPlaceholderText('输入消息...'), 'Hello{Enter}')

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello')
  })

  it('Shift+Enter 换行', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    const input = screen.getByPlaceholderText('输入消息...')
    await user.type(input, 'Hello{Shift>}{Enter}{/Shift}')

    expect(defaultProps.onSend).not.toHaveBeenCalled()
    expect(input).toHaveValue('Hello\n')
  })

  it('空消息不发送', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.click(screen.getByRole('button', { name: /发送/i }))

    expect(defaultProps.onSend).not.toHaveBeenCalled()
  })

  it('处理超长消息', async () => {
    const user = userEvent.setup()
    const longMessage = 'a'.repeat(10000)
    render(<ChatInput {...defaultProps} />)

    await user.type(screen.getByPlaceholderText('输入消息...'), longMessage)
    await user.click(screen.getByRole('button', { name: /发送/i }))

    expect(defaultProps.onSend).toHaveBeenCalledWith(longMessage)
  })
})
```

### 4.6 测试 Hooks

**`apps/desktop/src/hooks/useChat.test.ts`**：

```typescript
import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useChat } from './useChat'

// Mock API
vi.mock('../lib/api', () => ({
  chatApi: {
    send: vi.fn(),
  },
}))

describe('useChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('初始状态为空', () => {
    const { result } = renderHook(() => useChat())
    
    expect(result.current.messages).toEqual([])
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe(null)
  })

  it('发送消息添加到列表', async () => {
    const { result } = renderHook(() => useChat())
    
    await act(async () => {
      await result.current.sendMessage('Hello')
    })

    expect(result.current.messages).toHaveLength(1)
    expect(result.current.messages[0]).toMatchObject({
      role: 'user',
      content: 'Hello',
    })
  })

  it('加载状态管理', async () => {
    const mockResponse = { content: 'Hi there!' }
    vi.mocked(chatApi.send).mockResolvedValueOnce(mockResponse)

    const { result } = renderHook(() => useChat())

    expect(result.current.isLoading).toBe(false)

    const sendPromise = act(async () => {
      await result.current.sendMessage('Hello')
    })

    expect(result.current.isLoading).toBe(true)

    await sendPromise
    expect(result.current.isLoading).toBe(false)
  })

  it('错误处理', async () => {
    const error = new Error('Network error')
    vi.mocked(chatApi.send).mockRejectedValueOnce(error)

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.sendMessage('Hello')
    })

    expect(result.current.error).toBe('Network error')
  })

  it('清空消息列表', async () => {
    const { result } = renderHook(() => useChat())
    
    await act(async () => {
      await result.current.sendMessage('Hello')
    })

    expect(result.current.messages).toHaveLength(1)

    act(() => {
      result.current.clearMessages()
    })

    expect(result.current.messages).toEqual([])
  })
})
```

### 4.7 测试 API 调用

**`apps/desktop/src/lib/api.test.ts`**：

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { chatApi, ChatRequest, ChatResponse } from './api'

describe('chatApi', () => {
  const mockFetch = vi.fn()
  global.fetch = mockFetch

  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('发送聊天请求', async () => {
    const mockResponse: ChatResponse = {
      content: 'Hello!',
      session_id: 'test-123',
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const request: ChatRequest = {
      message: 'Hi',
      session_id: 'test-123',
    }

    const result = await chatApi.send(request)

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/chat',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      })
    )
    expect(result).toEqual(mockResponse)
  })

  it('处理网络错误', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    await expect(
      chatApi.send({ message: 'Hi', session_id: 'test' })
    ).rejects.toThrow('Network error')
  })

  it('处理 HTTP 错误', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    })

    await expect(
      chatApi.send({ message: 'Hi', session_id: 'test' })
    ).rejects.toThrow('HTTP 500')
  })
})
```

### 4.8 package.json 脚本

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:run": "vitest run",
    "check": "tsc --noEmit && cd src-tauri && cargo check"
  }
}
```

---

## 五、Python 后端测试配置（pytest）

### 5.1 安装依赖

**`services/agent/requirements.txt`**：

```txt
# 核心依赖
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
httpx>=0.26.0
pydantic>=2.0.0
litellm>=1.0.0
python-dotenv>=1.0.0
pydantic-settings>=2.0.0

# 测试依赖
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.12.0
```

### 5.2 pytest 配置

**`services/agent/pytest.ini`**：

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --cov=agent
    --cov=providers
    --cov=config
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

### 5.3 测试夹具（conftest.py）

**`services/agent/tests/conftest.py`**：

```python
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from main import app
from agent.loop import AgentLoop
from agent.memory import MemoryStore
from agent.session import SessionManager
import httpx


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """测试客户端"""
    client = TestClient(app)
    yield client
    client.close()


@pytest.fixture
def async_client() -> Generator[httpx.AsyncClient, None, None]:
    """异步测试客户端"""
    client = httpx.AsyncClient(base_url="http://test", timeout=5.0)
    yield client
    client.aclose()


@pytest.fixture
def agent_loop() -> AgentLoop:
    """Agent 循环实例"""
    return AgentLoop(model="openai/gpt-4o")


@pytest.fixture
def memory_store(tmp_path) -> MemoryStore:
    """记忆存储实例"""
    return MemoryStore(base_dir=str(tmp_path))


@pytest.fixture
def session_manager(tmp_path) -> SessionManager:
    """会话管理器实例"""
    return SessionManager(base_dir=str(tmp_path))


@pytest.fixture
def mock_llm_response(mocker):
    """Mock LLM 响应"""
    return mocker.patch(
        'litellm.completion',
        return_value={
            'choices': [{
                'message': {'content': 'Mock response'}
            }]
        }
    )
```

### 5.4 测试 AgentLoop

**`services/agent/tests/test_agent/test_loop.py`**：

```python
import pytest
from unittest.mock import Mock, patch
from agent.loop import AgentLoop, AgentConfig
from agent.memory import MemoryStore
from agent.session import Session, SessionManager


class TestAgentLoop:
    """AgentLoop 测试"""

    @pytest.fixture
    def agent_loop(self, memory_store, session_manager) -> AgentLoop:
        """创建 AgentLoop 实例"""
        config = AgentConfig(
            model="openai/gpt-4o",
            temperature=0.7,
            max_tokens=2000,
        )
        return AgentLoop(
            config=config,
            memory=memory_store,
            session_manager=session_manager,
        )

    def test_init(self, agent_loop):
        """测试初始化"""
        assert agent_loop.config.model == "openai/gpt-4o"
        assert agent_loop.config.temperature == 0.7
        assert agent_loop.memory is not None
        assert agent_loop.session_manager is not None

    def test_process_message_returns_response(self, agent_loop, mock_llm_response):
        """测试消息处理返回响应"""
        response = agent_loop.process_message("Hello", session_id="test")
        
        assert response is not None
        assert "content" in response
        assert response["content"] == "Mock response"

    def test_process_message_adds_to_session(self, agent_loop, mock_llm_response):
        """测试消息添加到会话"""
        agent_loop.process_message("Hello", session_id="test")
        
        session = agent_loop.session_manager.get("test")
        assert session is not None
        assert len(session.messages) >= 1

    def test_process_message_with_empty_input(self, agent_loop):
        """测试空输入处理"""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            agent_loop.process_message("", session_id="test")

    def test_process_message_with_long_input(self, agent_loop, mock_llm_response):
        """测试长消息处理"""
        long_message = "a" * 10000
        response = agent_loop.process_message(long_message, session_id="test")
        
        assert response is not None

    @pytest.mark.asyncio
    async def test_run_agent_loop_without_tool_calls(self, agent_loop, mock_llm_response):
        """测试无工具调用的循环"""
        response = await agent_loop._run_agent_loop(
            messages=[{"role": "user", "content": "Hello"}],
            session_id="test",
        )
        
        assert response is not None
        assert mock_llm_response.called

    @pytest.mark.asyncio
    async def test_run_agent_loop_with_tool_calls(self, agent_loop, mocker):
        """测试有工具调用的循环"""
        # Mock LLM 返回工具调用
        mock_response = {
            'choices': [{
                'message': {
                    'content': None,
                    'tool_calls': [{
                        'id': 'call_1',
                        'function': {
                            'name': 'search',
                            'arguments': '{"query": "test"}'
                        }
                    }]
                }
            }]
        }
        mocker.patch('litellm.completion', return_value=mock_response)
        
        # Mock 工具执行
        mocker.patch('agent.tools.registry.ToolRegistry.execute', return_value="Result")
        
        response = await agent_loop._run_agent_loop(
            messages=[{"role": "user", "content": "Search for test"}],
            session_id="test",
        )
        
        assert response is not None

    def test_max_iterations_limit(self, agent_loop, mocker):
        """测试最大迭代次数限制"""
        # Mock LLM 持续返回工具调用
        mock_response = {
            'choices': [{
                'message': {
                    'content': None,
                    'tool_calls': [{'id': '1', 'function': {'name': 'test', 'arguments': '{}'}}]
                }
            }]
        }
        mocker.patch('litellm.completion', return_value=mock_response)
        
        with pytest.raises(Exception, match="Max iterations reached"):
            agent_loop.process_message("test", session_id="test")

    def test_consolidate_memory(self, agent_loop):
        """测试记忆整合"""
        # 添加多条消息
        for i in range(60):
            agent_loop.process_message(f"Message {i}", session_id="test")
        
        # 验证记忆被整合
        memory = agent_loop.memory.get_all()
        assert len(memory) > 0
```

### 5.5 测试 API 接口

**`services/agent/tests/test_api/test_chat.py`**：

```python
import pytest
from fastapi.testclient import TestClient
from main import app


class TestChatAPI:
    """聊天 API 测试"""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_chat_endpoint_success(self, client, mocker):
        """测试聊天接口成功"""
        mocker.patch('litellm.completion', return_value={
            'choices': [{'message': {'content': 'Hello!'}}]
        })

        response = client.post(
            "/api/chat",
            json={"message": "Hello", "session_id": "test-123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["content"] == "Hello!"

    def test_chat_endpoint_empty_message(self, client):
        """测试空消息"""
        response = client.post(
            "/api/chat",
            json={"message": "", "session_id": "test"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_chat_endpoint_missing_session(self, client, mocker):
        """测试缺失 session_id"""
        mocker.patch('litellm.completion', return_value={
            'choices': [{'message': {'content': 'Hello!'}}]
        })

        response = client.post(
            "/api/chat",
            json={"message": "Hello"}
        )
        
        # 应该生成新的 session_id
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data

    def test_chat_stream_endpoint(self, client, mocker):
        """测试流式聊天接口"""
        mocker.patch('litellm.completion', return_value=iter([
            {'choices': [{'delta': {'content': 'Hello'}}]},
            {'choices': [{'delta': {'content': ' World'}}]},
        ]))

        with client.stream(
            "POST",
            "/api/chat/stream",
            json={"message": "Hello"}
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"

    def test_chat_with_tool(self, client, mocker):
        """测试带工具调用的聊天"""
        # Mock LLM 返回工具调用
        mocker.patch('litellm.completion', side_effect=[
            {
                'choices': [{
                    'message': {
                        'content': None,
                        'tool_calls': [{
                            'id': 'call_1',
                            'function': {'name': 'search', 'arguments': '{"query": "test"}'}
                        }]
                    }
                }]
            },
            {
                'choices': [{'message': {'content': 'Search result'}}]
            }
        ])
        mocker.patch('agent.tools.registry.ToolRegistry.execute', return_value="Result")

        response = client.post(
            "/api/chat",
            json={"message": "Search for test", "session_id": "test"}
        )
        
        assert response.status_code == 200
```

### 5.6 测试工具模块

**`services/agent/tests/test_tools/test_file.py`**：

```python
import pytest
import os
from agent.tools.file import (
    read_file,
    write_file,
    edit_file,
    list_dir,
)


class TestFileTools:
    """文件工具测试"""

    def test_read_file(self, tmp_path):
        """测试读取文件"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")
        
        content = read_file(str(test_file))
        assert content == "Hello World"

    def test_read_file_not_found(self, tmp_path):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError):
            read_file(str(tmp_path / "nonexistent.txt"))

    def test_write_file(self, tmp_path):
        """测试写入文件"""
        test_file = tmp_path / "test.txt"
        
        write_file(str(test_file), "Hello World")
        
        assert test_file.exists()
        assert test_file.read_text() == "Hello World"

    def test_write_file_create_dirs(self, tmp_path):
        """测试创建目录"""
        test_file = tmp_path / "subdir" / "test.txt"
        
        write_file(str(test_file), "Hello World")
        
        assert test_file.exists()

    def test_edit_file(self, tmp_path):
        """测试编辑文件"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")
        
        edit_file(str(test_file), "World", "Universe")
        
        assert test_file.read_text() == "Hello Universe"

    def test_list_dir(self, tmp_path):
        """测试列出目录"""
        (tmp_path / "file1.txt").write_text("1")
        (tmp_path / "file2.txt").write_text("2")
        (tmp_path / "subdir").mkdir()
        
        files = list_dir(str(tmp_path))
        
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "subdir" in files
```

### 5.7 测试配置系统

**`services/agent/tests/test_config/test_schema.py`**：

```python
import pytest
from pydantic import ValidationError
from config.schema import Config, AgentConfig, ChannelConfig


class TestConfigSchema:
    """配置模型测试"""

    def test_agent_config_valid(self):
        """测试有效配置"""
        config = AgentConfig(
            model="openai/gpt-4o",
            temperature=0.7,
            max_tokens=2000,
        )
        
        assert config.model == "openai/gpt-4o"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000

    def test_agent_config_temperature_range(self):
        """测试温度范围"""
        with pytest.raises(ValidationError):
            AgentConfig(model="openai/gpt-4o", temperature=1.5)
        
        with pytest.raises(ValidationError):
            AgentConfig(model="openai/gpt-4o", temperature=-0.1)

    def test_agent_config_model_validation(self):
        """测试模型验证"""
        # 有效模型名称
        config = AgentConfig(model="anthropic/claude-3-5-sonnet")
        assert config.model == "anthropic/claude-3-5-sonnet"

    def test_full_config(self):
        """测试完整配置"""
        config = Config(
            agents=AgentConfig(model="openai/gpt-4o"),
            channels=ChannelConfig(),
        )
        
        assert config.agents.model == "openai/gpt-4o"
```

### 5.8 测试记忆系统

**`services/agent/tests/test_agent/test_memory.py`**：

```python
import pytest
from agent.memory import MemoryStore, Memory


class TestMemoryStore:
    """记忆存储测试"""

    @pytest.fixture
    def memory_store(self, tmp_path) -> MemoryStore:
        return MemoryStore(base_dir=str(tmp_path))

    def test_add_memory(self, memory_store):
        """测试添加记忆"""
        memory_store.add("User likes pizza")
        
        memories = memory_store.get_all()
        assert len(memories) == 1
        assert memories[0].content == "User likes pizza"

    def test_get_memory_empty(self, memory_store):
        """测试获取空记忆"""
        memories = memory_store.get_all()
        assert memories == []

    def test_search_memory(self, memory_store):
        """测试搜索记忆"""
        memory_store.add("User likes pizza")
        memory_store.add("User lives in Beijing")
        
        results = memory_store.search("pizza")
        assert len(results) == 1
        assert "pizza" in results[0].content

    def test_save_and_load(self, memory_store):
        """测试保存和加载"""
        memory_store.add("Test memory")
        memory_store.save()
        
        # 新建实例并加载
        new_store = MemoryStore(base_dir=memory_store.base_dir)
        new_store.load()
        
        memories = new_store.get_all()
        assert len(memories) == 1
```

---

## 六、Rust 测试配置

### 6.1 Cargo.toml 配置

**`apps/desktop/src-tauri/Cargo.toml`**：

```toml
[package]
name = "socratx"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "2.0", features = [] }
tauri-plugin-shell = "2.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
reqwest = { version = "0.11", features = ["json"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
tauri = { version = "2.0", features = ["test"] }

[build-dependencies]
tauri-build = "2.0"
```

### 6.2 Rust 单元测试

**`apps/desktop/src-tauri/src/lib.rs`**：

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        let result = greet("Alice");
        assert_eq!(result, "Hello, Alice!");
    }

    #[test]
    fn test_greet_empty_name() {
        let result = greet("");
        assert_eq!(result, "Hello, !");
    }
}
```

### 6.3 Tauri 命令测试

**`apps/desktop/src-tauri/src/commands.rs`**：

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tauri::test::mock_context;

    #[tokio::test]
    async fn test_chat_command() {
        let response = chat("Hello".to_string(), "test-session".to_string()).await;
        assert!(response.is_ok());
        
        let data = response.unwrap();
        assert!(!data.content.is_empty());
    }

    #[tokio::test]
    async fn test_chat_empty_message() {
        let response = chat("".to_string(), "test".to_string()).await;
        assert!(response.is_err());
    }
}
```

### 6.4 Sidecar 测试

**`apps/desktop/src-tauri/src/sidecar.rs`**：

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sidecar_config() {
        let config = SidecarConfig::default();
        assert_eq!(config.port, 8000);
        assert_eq!(config.host, "127.0.0.1");
    }

    #[tokio::test]
    async fn test_sidecar_start_stop() {
        let mut sidecar = Sidecar::new();
        
        let result = sidecar.start().await;
        assert!(result.is_ok());
        
        let stop_result = sidecar.stop().await;
        assert!(stop_result.is_ok());
    }
}
```

### 6.5 运行 Rust 测试

```bash
cd apps/desktop/src-tauri

# 运行所有测试
cargo test

# 运行特定测试
cargo test test_greet

# 显示输出
cargo test -- --nocapture

# 生成覆盖率（需要 cargo-tarpaulin）
cargo tarpaulin --out Html
```

---

## 七、E2E 测试配置（Playwright）

### 7.1 安装依赖

```bash
cd tests/e2e
pnpm init
pnpm add -D @playwright/test
npx playwright install
```

### 7.2 Playwright 配置

**`tests/e2e/playwright.config.ts`**：

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
})
```

### 7.3 E2E 测试示例

**`tests/e2e/test_chat_flow.spec.ts`**：

```typescript
import { test, expect } from '@playwright/test'

test.describe('Chat Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('发送消息并收到回复', async ({ page }) => {
    // 输入消息
    await page.getByPlaceholder('输入消息...').fill('Hello')
    
    // 点击发送
    await page.getByRole('button', { name: '发送' }).click()
    
    // 验证用户消息显示
    await expect(page.getByText('Hello')).toBeVisible()
    
    // 等待 AI 回复（Mock）
    await expect(page.getByText('Mock response')).toBeVisible()
  })

  test('空消息不发送', async ({ page }) => {
    const sendButton = page.getByRole('button', { name: '发送' })
    
    // 直接点击发送（无输入）
    await sendButton.click()
    
    // 验证没有新消息
    const messageCount = await page.getByTestId('message').count()
    expect(messageCount).toBe(0)
  })

  test('Enter 发送，Shift+Enter 换行', async ({ page }) => {
    const input = page.getByPlaceholder('输入消息...')
    
    // 输入并按 Enter
    await input.fill('Hello')
    await input.press('Enter')
    await expect(page.getByText('Hello')).toBeVisible()
    
    // 输入并按 Shift+Enter
    await input.fill('World')
    await input.press('Shift+Enter')
    
    // 验证换行
    expect(await input.inputValue()).toBe('World\n')
  })
})
```

---

## 八、测试覆盖率目标

| 模块 | 覆盖率目标 | 优先级 | 说明 |
|------|----------|--------|------|
| **核心业务逻辑** | ≥90% | P0 | AgentLoop, Memory, Session |
| **API 接口** | ≥80% | P0 | FastAPI 路由 |
| **工具函数** | ≥95% | P1 | utils, helpers |
| **UI 组件** | ≥70% | P1 | 交互组件 |
| **样式/CSS** | 不要求 | - | 视觉样式 |
| **Rust 命令** | ≥80% | P1 | Tauri IPC |

---

## 九、CI/CD 集成

### 9.1 GitHub Actions

**`.github/workflows/test.yml`**：

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Run frontend tests
        run: cd apps/desktop && pnpm test:run
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: apps/desktop/coverage/coverage-final.json
          flags: frontend

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd services/agent
          pip install -r requirements.txt
      
      - name: Run Python tests
        run: |
          cd services/agent
          pytest --cov=agent --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: services/agent/coverage.xml
          flags: backend

  test-rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
      
      - name: Cache Cargo
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      
      - name: Run Rust tests
        run: |
          cd apps/desktop/src-tauri
          cargo test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: apps/desktop/src-tauri/coverage/lcov.info
          flags: rust

  e2e-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup pnpm
        uses: pnpm/action-setup@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Start dev server
        run: |
          cd apps/desktop
          pnpm dev &
          sleep 5
      
      - name: Run E2E tests
        run: |
          cd tests/e2e
          npx playwright test
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: tests/e2e/playwright-report/
```

---

## 十、开发规范

### 10.1 测试命名规范

```typescript
// ✅ 好的命名 - 清晰描述行为
describe('ChatInput', () => {
  it('渲染输入框', () => {})
  it('点击发送按钮触发回调', () => {})
  it('禁用状态下无法发送', () => {})
  it('按 Enter 键发送消息', () => {})
  it('Shift+Enter 换行', () => {})
})

// ❌ 避免模糊命名
it('test 1', () => {})
it('should work', () => {})
it('test function', () => {})
```

### 10.2 测试独立性

```typescript
// ✅ 每个测试独立，不依赖其他测试状态
describe('ChatInput', () => {
  it('测试 A', () => {
    const { container } = render(<ChatInput />)
    // ...
  })

  it('测试 B', () => {
    const { container } = render(<ChatInput />)
    // 重新渲染，不依赖测试 A
  })
})

// ❌ 测试间依赖
describe('ChatInput', () => {
  let component
  
  it('测试 A', () => {
    component = render(<ChatInput />)
  })

  it('测试 B', () => {
    // 依赖测试 A 的结果
    expect(component).toBeDefined()
  })
})
```

### 10.3 测试数据管理

```typescript
// ✅ 使用工厂函数创建测试数据
const createMessage = (overrides = {}) => ({
  id: '1',
  role: 'user',
  content: 'Test',
  timestamp: Date.now(),
  ...overrides,
})

it('使用工厂函数', () => {
  const message = createMessage({ content: 'Custom' })
  expect(message.content).toBe('Custom')
})

// ❌ 硬编码测试数据
it('硬编码数据', () => {
  const message = {
    id: '1',
    role: 'user',
    content: 'Test',
    timestamp: 1708000000000,
  }
})
```

### 10.4 优先测试边界条件

```typescript
// 空值、边界值、异常情况
describe('边界条件', () => {
  it('处理空消息', () => {})
  it('处理 null 输入', () => {})
  it('处理 undefined', () => {})
  it('处理超长消息 (10000 字符)', () => {})
  it('处理特殊字符 (<>&"")', () => {})
  it('处理 emoji', () => {})
  it('网络错误时显示友好提示', () => {})
  it('超时处理', () => {})
})
```

---

## 十一、推荐开发顺序

### 阶段 1: 基础测试框架（第 1 周）

```
□ 配置 Vitest (前端)
□ 配置 pytest (Python)
□ 配置 Rust 测试
□ 编写测试全局配置
□ 配置 CI/CD 集成
```

### 阶段 2: 核心功能测试（第 2-3 周）

```
□ Python AgentLoop 测试
□ Python Memory 测试
□ Python Session 测试
□ Python ToolRegistry 测试
□ API 接口测试
□ 工具函数测试
```

### 阶段 3: UI 组件测试（第 4 周）

```
□ ChatInput 测试
□ ChatMessage 测试
□ ChatContainer 测试
□ useChat Hook 测试
□ ThemeContext 测试
```

### 阶段 4: 集成测试（第 5 周）

```
□ 前端 + Python 集成测试
□ Tauri IPC 测试
□ E2E 测试 (Playwright)
□ 性能测试
```

---

## 十二、常见问题

### Q1: 测试运行太慢怎么办？

**解决方案**：
- 使用 Vitest 的并行模式 (`--parallel`)
- 只运行变更测试 (`--changed`)
- 配置测试缓存
- 分离单元测试和集成测试

### Q2: Mock 太多怎么办？

**解决方案**：
- 优先测试公共 API
- 使用集成测试补充
- Mock 外部依赖，不 Mock 内部逻辑
- 定期审查 Mock 的必要性

### Q3: 测试覆盖率低怎么办？

**解决方案**：
- 优先保证核心逻辑覆盖率
- 不追求 100% 覆盖
- 关注关键路径测试
- 逐步提高，不要一次性完成

---

## 十三、参考资源

- [Vitest 文档](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [pytest 文档](https://docs.pytest.org/)
- [Playwright 文档](https://playwright.dev/)
- [Tauri 测试指南](https://v2.tauri.app/test/)
- [Rust 测试文档](https://doc.rust-lang.org/book/ch11-00-testing.html)

---

*最后更新：2026 年 2 月 20 日*

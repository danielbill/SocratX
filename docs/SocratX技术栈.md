# SocratX 技术栈

> **最后更新**: 2026 年 2 月 20 日

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│  Tauri 2 桌面应用 (Rust)                                     │
│  - 窗口管理、系统托盘、文件对话框、系统通知                    │
└─────────────────────────┬───────────────────────────────────┘
                          │ IPC (Tauri Commands)
┌─────────────────────────▼───────────────────────────────────┐
│  React 19 前端 (TypeScript)                                 │
│  - 聊天 UI、设置界面、会话管理、状态管理                      │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP (localhost:8000)
┌─────────────────────────▼───────────────────────────────────┐
│  Python Sidecar (FastAPI)                                   │
│  - AgentLoop、工具系统、LLM 集成、记忆管理                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 技术栈详情

### 前端 (apps/desktop)

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.0 | UI 框架 |
| TypeScript | 5.8 | 类型安全 |
| Tauri | 2.1 | 桌面应用框架 |
| Vite | 7.0 | 构建工具 |
| TailwindCSS | 4.1.8 | CSS 框架 |
| shadcn/ui | - | UI 组件库 (Radix UI) |
| framer-motion | 12.0 | UI 动画 |
| lucide-react | 0.468 | 图标库 |
| zustand | 5.0 | 状态管理 |
| react-markdown | 9.0 | Markdown 渲染 |
| react-syntax-highlighter | 15.6 | 代码高亮 |

**Radix UI 组件**: Dialog, Dropdown Menu, Tooltip, Label, Switch, Tabs, Scroll Area, Slot

**测试**: Vitest 4.0, @testing-library/react

### 后端 (services/agent)

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 运行时 |
| FastAPI | 0.109+ | Web 框架 |
| Uvicorn | 0.27+ | ASGI 服务器 |
| Pydantic | 2.0+ | 数据验证 |
| LiteLLM | 1.50+ | LLM 统一接口 |
| httpx | 0.26+ | HTTP 客户端 |
| python-dotenv | 1.0+ | 环境变量 |
| aiofiles | 23.0+ | 异步文件 I/O |

**测试**: pytest, pytest-asyncio, pytest-cov

**支持的 LLM 提供商**: OpenAI, Anthropic, DeepSeek, Gemini, 智谱, 通义千问, 月之暗面, MiniMax, 百川, Ollama, vLLM, Groq 等

### Rust (src-tauri)

| 技术 | 版本 | 用途 |
|------|------|------|
| Tauri | 2.0 | 桌面应用框架 |
| serde | 1.0 | 序列化 |
| tauri-build | 2.0 | 构建脚本 |

---

## 项目结构

```
SocratX/
├── apps/desktop/                # Tauri + React 桌面应用
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui 基础组件
│   │   │   └── chat/            # 对话组件
│   │   ├── contexts/            # ThemeContext
│   │   ├── lib/                 # api.ts, utils.ts
│   │   └── main.tsx
│   └── src-tauri/               # Rust 后端
│       ├── src/main.rs
│       └── Cargo.toml
│
├── services/agent/              # Python FastAPI 服务
│   ├── agent/                   # 核心代理模块
│   │   ├── loop.py             # AgentLoop
│   │   ├── context.py          # ContextBuilder
│   │   ├── session.py          # SessionManager
│   │   ├── memory.py           # MemoryStore
│   │   └── tools/              # 工具系统
│   ├── providers/              # LLM 提供商
│   ├── config/                 # 配置管理
│   ├── bus/                    # 消息总线
│   ├── main.py
│   └── requirements.txt
│
├── packages/shared/             # 共享类型定义
│
├── docs/                       # 项目文档
├── package.json                # Monorepo 根配置
└── pnpm-workspace.yaml
```

---

## 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| AgentLoop | agent/loop.py | 迭代 LLM + 工具执行循环 |
| ContextBuilder | agent/context.py | 系统提示词构建 |
| SessionManager | agent/session.py | JSONL 会话持久化 |
| MemoryStore | agent/memory.py | MEMORY.md + HISTORY.md |
| ToolRegistry | agent/tools/registry.py | 动态工具管理 |
| MessageBus | bus/queue.py | 异步消息队列 |
| LiteLLMProvider | providers/litellm_provider.py | LLM 统一接口 |

---

## API 端点

```
POST   /api/chat          # 对话
GET    /api/sessions      # 会话列表
GET    /api/sessions/{id} # 会话详情
DELETE /api/sessions/{id} # 删除会话
GET    /api/memory        # 获取记忆
POST   /api/memory        # 更新记忆
GET    /api/config        # 获取配置
POST   /api/config        # 更新配置
GET    /api/tools         # 工具列表
GET    /health            # 健康检查
```

---

## 内置工具

| 工具 | 功能 |
|------|------|
| file_read | 读取文件 |
| file_write | 写入文件 |
| file_list | 列出目录 |
| shell_exec | 执行 Shell 命令 |
| web_search | 网络搜索 |
| web_fetch | 获取网页内容 |

---

## 开发命令

```bash
pnpm install:all    # 安装所有依赖
pnpm dev            # 启动开发服务器
pnpm tauri:dev      # 启动 Tauri 开发模式
pnpm tauri:build    # 构建生产版本
pnpm test           # 运行前端测试
pnpm test:coverage  # 测试覆盖率
```

---

## 环境要求

- Node.js 18+
- pnpm 8+
- Python 3.11+
- Rust 1.70+

---

## 参考项目

- [nanobot](https://github.com/HKUDS/nanobot) - 后端架构参考
- [opcode](https://github.com/winfunc/opcode) - UI 组件参考

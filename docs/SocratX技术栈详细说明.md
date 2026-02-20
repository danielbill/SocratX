# SocratX 技术栈详细说明

> **最后更新**: 2026 年 2 月 20 日 - 基于 nanobot 架构重构

## 技术选型

```
┌──────────────────────────────────────────────┐
│          前端：Tauri 2 + React + TypeScript   │
├──────────────────────────────────────────────┤
│          后端：Python FastAPI                 │
├──────────────────────────────────────────────┤
│          AI 集成：LiteLLM (15+ 提供商)        │
└──────────────────────────────────────────────┘
```

---

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     用户界面层                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │  React 19 + TypeScript                            │  │
│  │  - 对话界面                                        │  │
│  │  - 文件浏览器                                      │  │
│  │  - 设置面板                                        │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ IPC / HTTP (localhost)
┌────────────────────▼────────────────────────────────────┐
│                     系统适配层                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Tauri 2 (Rust)                                   │  │
│  │  - 系统 API 封装（文件/网络/通知）                   │  │
│  │  - Python Sidecar 管理                             │  │
│  │  - 窗口管理                                        │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP / Stdio
┌────────────────────▼────────────────────────────────────┐
│                     AI 服务层                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Python FastAPI                                   │  │
│  │  - AI API 调用（OpenAI/Claude/...）                 │  │
│  │  - 对话状态管理                                    │  │
│  │  - 文件读写操作                                    │  │
│  │  - 工具调用（搜索/代码执行/...）                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 技术栈详情

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 19.0 | UI 框架 |
| **TypeScript** | 5.8 | 类型安全 |
| **Tauri** | 2.1 | 桌面应用框架 |
| **Vite** | 7.0 | 构建工具 |
| **TailwindCSS** | 4.1.8 | 样式方案 |
| **shadcn/ui** | - | UI 组件库 (Radix UI) |
| **framer-motion** | 12.0 | UI 动画 |
| **lucide-react** | 0.468 | 图标库 |
| **zustand** | 5.0 | 状态管理 |
| **react-markdown** | 9.0 | Markdown 渲染 |
| **react-syntax-highlighter** | 15.6 | 代码高亮 |

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 运行时 |
| **FastAPI** | 0.109+ | Web 框架 |
| **Uvicorn** | 0.27+ | ASGI 服务器 |
| **Pydantic** | 2.0+ | 数据验证 |
| **HTTPX** | 0.26+ | HTTP 客户端 |
| **LiteLLM** | 1.50+ | AI 统一接口（15+ 提供商） |
| **python-dotenv** | 1.0+ | 环境变量 |
| **aiofiles** | 23.0+ | 异步文件 I/O |

### 系统技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Rust** | 1.75+ | Tauri 后端 |
| **Cargo** | - | Rust 包管理 |
| **PyInstaller** | 6.x | Python 打包 |

### 包管理/构建工具

| 技术 | 版本 | 用途 |
|------|------|------|
| **pnpm** | 9.x | 包管理 + Monorepo 工作空间 |
| **Node.js** | 20.x+ | JavaScript 运行时 |

---

## 项目结构

> 基于 nanobot 架构重构

```
SocratX/
├── apps/
│   └── desktop/                      # Tauri 桌面应用
│       ├── src/
│       │   ├── components/
│       │   │   ├── ui/               # shadcn/ui 基础组件
│       │   │   │   ├── button.tsx
│       │   │   │   ├── card.tsx
│       │   │   │   ├── textarea.tsx
│       │   │   │   └── scroll-area.tsx
│       │   │   └── chat/             # 对话组件
│       │   │       ├── ChatContainer.tsx
│       │   │       ├── ChatInput.tsx
│       │   │       └── ChatMessage.tsx
│       │   ├── contexts/
│       │   │   └── ThemeContext.tsx  # 主题管理
│       │   ├── lib/
│       │   │   ├── api.ts            # Tauri API 封装
│       │   │   └── utils.ts          # 工具函数
│       │   └── main.tsx
│       └── src-tauri/                # Tauri (Rust) 源码
│           ├── src/
│           │   ├── main.rs           # Rust 入口
│           │   └── lib.rs            # Tauri 命令
│           ├── Cargo.toml            # Rust 依赖
│           └── tauri.conf.json       # Tauri 配置
│
├── services/
│   └── agent/                        # Python AI 服务 (基于 nanobot)
│       ├── agent/                    # 核心代理模块
│       │   ├── loop.py               # AgentLoop - 迭代 LLM + 工具循环
│       │   ├── context.py            # ContextBuilder - 系统提示词
│       │   ├── session.py            # SessionManager - JSONL 持久化
│       │   ├── memory.py             # MemoryStore - 双层记忆
│       │   └── tools/                # 工具系统
│       │       ├── base.py           # Tool 抽象基类
│       │       └── registry.py       # 工具注册表 (6个内置工具)
│       ├── providers/                # LLM 提供商
│       │   ├── registry.py           # 15+ 提供商注册表
│       │   └── litellm_provider.py   # LiteLLM 实现
│       ├── config/                   # 配置管理
│       │   ├── schema.py             # Pydantic 配置模型
│       │   └── loader.py             # 配置加载器
│       ├── bus/                      # 消息总线
│       │   ├── events.py             # Inbound/OutboundMessage
│       │   └── queue.py              # MessageBus 异步队列
│       ├── main.py                   # FastAPI 入口
│       └── requirements.txt          # Python 依赖
│
├── packages/
│   └── shared/                       # 共享代码
│       └── src/index.ts              # TypeScript 类型定义
│
├── docs/                             # 文档
│   ├── 技术栈说明.md
│   ├── 基于nanobot的架构设计.md
│   ├── 基于opcode的界面设计.md
│   └── SocratX项目开发测试设计.md
│
├── package.json                      # 根目录 - pnpm workspace 配置
├── pnpm-workspace.yaml               # pnpm Monorepo 配置
├── project_todos.md                  # 项目待办事项
└── README.md
```

### pnpm Workspace 配置

**根目录 `package.json`**:
```json
{
  "name": "socratx",
  "private": true,
  "scripts": {
    "install:all": "pnpm install && pnpm run install:python",
    "install:python": "pip install -r services/agent/requirements.txt",
    "dev": "pnpm --filter @socratx/desktop tauri dev",
    "build": "pnpm --filter @socratx/desktop tauri build"
  }
}
```

**`pnpm-workspace.yaml`**:
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

---

## 核心依赖

### 前端 (`apps/desktop/package.json`)

```json
{
  "name": "@socratx/desktop",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "tauri": "tauri"
  },
  "dependencies": {
    "react": "^19",
    "react-dom": "^19",
    "@tauri-apps/api": "^2",
    "@tauri-apps/plugin-fs": "^2",
    "@tauri-apps/plugin-shell": "^2"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "@vitejs/plugin-react": "^4",
    "tailwindcss": "^4",
    "typescript": "^5.8",
    "vite": "^7"
  }
}
```

### Rust (`apps/desktop/src-tauri/Cargo.toml`)

```toml
[package]
name = "socratx"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = "2.0"
tauri-plugin-shell = "2.0"
tauri-plugin-fs = "2.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

[build-dependencies]
tauri-build = "2.0"
```

### Python (`services/agent/requirements.txt`)

```txt
# Web 框架
fastapi>=0.109.0
uvicorn[standard]>=0.27.0

# HTTP 客户端
httpx>=0.26.0

# 数据验证
pydantic>=2.0.0
pydantic-settings>=2.0.0

# AI/LLM
litellm>=1.50.0

# 环境变量
python-dotenv>=1.0.0

# 工具库
aiofiles>=23.0.0
```

**说明**：LiteLLM 提供统一的 AI 接口，支持 15+ 提供商（OpenAI, Claude, DeepSeek, Gemini, 智谱, 通义千问, Kimi, MiniMax, 百川, Ollama, vLLM 等）。

**内置工具**：
- `file_read` / `file_write` / `file_list` - 文件操作
- `shell_exec` - Shell 命令执行
- `web_search` / `web_fetch` - 网络搜索和获取

---

## 开发流程

### 环境准备

```bash
# 1. 安装 Node.js 20+
# https://nodejs.org

# 2. 安装 pnpm
npm install -g pnpm

# 3. 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 4. 安装 Python 3.11+
# https://python.org
```

### 一键安装

```bash
# 克隆项目
git clone https://github.com/yourname/socratx.git
cd socratx

# 一键安装所有依赖（前端 + Python）
pnpm run install:all
```

### 开发模式

```bash
# 终端 1: 启动 Python 服务
cd services/agent
uvicorn main:app --reload --port 8000

# 终端 2: 启动 Tauri 开发服务器
pnpm run dev
```

### 构建打包

```bash
# Windows
pnpm run build --target x86_64-pc-windows-msvc

# macOS
pnpm run build --target x86_64-apple-darwin
pnpm run build --target aarch64-apple-darwin

# Linux
pnpm run build --target x86_64-unknown-linux-gnu
```

---

## API 设计

### Python FastAPI 端点

```python
# services/agent/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SocratX Agent API", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str = "default"
    model: str | None = None
    stream: bool = False

class ChatResponse(BaseModel):
    content: str
    session_id: str
    model: str
    tool_calls: list[ToolCall] = []
    usage: dict | None = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """处理用户对话请求 (通过 AgentLoop)"""
    # 使用 AgentLoop 处理消息
    response = await agent_loop.run(req.message, req.session_id, req.user_id)
    return ChatResponse(
        content=response.content,
        session_id=req.session_id,
        model=config.agent.model,
        tool_calls=response.tool_calls,
    )

# 会话管理
@app.get("/api/sessions")
async def list_sessions(user_id: str | None = None, limit: int = 100):
    """获取会话列表"""

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""

# 记忆管理
@app.get("/api/memory")
async def get_memory():
    """获取长期记忆 (MEMORY.md)"""

@app.post("/api/memory")
async def update_memory(content: str, section: str | None = None):
    """更新长期记忆"""

# 配置管理
@app.get("/api/config")
async def get_config():
    """获取当前配置"""

@app.post("/api/config")
async def update_config(updates: dict):
    """更新配置"""

# 工具列表
@app.get("/api/tools")
async def list_tools():
    """列出可用工具"""

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
```

### Tauri 命令

```rust
// apps/desktop/src-tauri/src/commands.rs
use tauri::CommandScope;

#[tauri::command]
async fn chat(message: String, session_id: String) -> Result<String, String> {
    // 调用 Python 服务
    let client = reqwest::Client::new();
    let resp = client
        .post("http://localhost:8000/api/chat")
        .json(&serde_json::json!({
            "message": message,
            "session_id": session_id
        }))
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let data: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
    Ok(data["reply"].as_str().unwrap().to_string())
}
```

### React 调用

```tsx
// apps/desktop/src/App.tsx
import { invoke } from "@tauri-apps/api/core";

async function handleChat(message: string) {
  const reply = await invoke("chat", {
    message,
    sessionId: "session-1"
  });
  console.log("AI:", reply);
}
```

---

## 打包发布

### PyInstaller 配置

```python
# services/agent/pyinstaller.spec
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['main.py'],
    hiddenimports=collect_submodules('openai'),
    ...
)
```

### Tauri Sidecar 配置

```json
// apps/desktop/src-tauri/tauri.conf.json
{
  "bundle": {
    "resources": ["../../services/agent/dist/*"],
    "externalBin": ["../../services/agent/dist/agent"]
  }
}
```

### pnpm 打包脚本

```bash
# scripts/build.sh

# 1. 打包 Python 服务
cd services/agent
pyinstaller --onefile --name agent main.py

# 2. 构建前端
cd ../../apps/desktop
pnpm run build

# 3. 构建 Tauri 应用
pnpm run tauri build
```

### 根目录一键打包

```json
// package.json
{
  "scripts": {
    "build": "pnpm run build:python && pnpm run build:tauri",
    "build:python": "cd services/agent && pyinstaller --onefile --name agent main.py",
    "build:tauri": "pnpm --filter @socratx/desktop tauri build"
  }
}
```

```bash
# 一键打包
pnpm run build
```

---

## 平台支持

| 平台 | 状态 | 备注 |
|------|------|------|
| **Windows 10/11 (x64)** | ✅ 支持 | 主要开发平台 |
| **macOS 11+ (Intel)** | ✅ 支持 | 需要 Apple Developer 签名 |
| **macOS 11+ (Apple Silicon)** | ✅ 支持 | M1/M2/M3 原生支持 |
| **Linux (Ubuntu 20.04+)** | ✅ 支持 | AppImage/Deb 格式 |

---

## 核心架构模式

### 1. AgentLoop (参考 nanobot)

```
用户消息 → SessionManager → ContextBuilder → LLMProvider
                                              ↓
                                    ┌─────────────────┐
                                    │ 工具调用?        │
                                    └─────────────────┘
                                         ↓ Yes
                                    ToolRegistry.execute()
                                         ↓
                                    工具结果追加到 messages
                                         ↓
                                    继续下一轮 LLM (最多 20 次)
                                         ↓ No
                                    返回最终响应
```

### 2. 双层记忆系统 (参考 nanobot)

- **MEMORY.md** - 长期事实记忆（用户信息、偏好、重要知识）
- **HISTORY.md** - 可搜索对话日志（Grep 可搜索）

### 3. 消息总线 (参考 nanobot)

```
InboundMessage → MessageBus → AgentLoop → OutboundMessage → Channel
```

### 4. 工具注册表 (参考 nanobot)

```python
registry = ToolRegistry()
registry.register_simple("file_read", "Read file content", handler)
await registry.execute("file_read", {"path": "/path/to/file"})
```

## 参考项目

| 项目 | 链接 | 参考 |
|------|------|------|
| **nanobot** | [HKUDS/nanobot](https://github.com/HKUDS/nanobot) | 后端架构、AgentLoop、工具系统、消息总线 |
| **opcode** | [winfunc/opcode](https://github.com/winfunc/opcode) | UI 组件、shadcn/ui 集成、布局模式 |

### 为什么选 pnpm？

| 对比项 | pnpm | npm | Bun |
|--------|------|-----|-----|
| **Monorepo 支持** | 🟢 最好 | 🟡 基础 | 🟢 好 |
| **安装速度** | 🟢 快 | 🟡 慢 | 🚀 最快 |
| **磁盘占用** | 🟢 硬链接共享 | 🔴 重复复制 | 🟢 硬链接共享 |
| **稳定性** | 🟢 成熟（2016 年） | 🟢 最成熟 | 🟡 较新（2022 年） |
| **兼容性** | 🟢 100% npm 兼容 | 🟢 100% | 🟡 大部分 |

**pnpm 优势**：
- 节省磁盘空间（依赖硬链接共享）
- Monorepo `--filter` 语法简洁
- 性能稳定，企业广泛使用
- 100% npm 兼容，踩坑少

### 为什么选 Tauri 2？

| 对比项 | Tauri 2 | Electron |
|--------|---------|----------|
| 包体积 | ~10 MB | ~100 MB+ |
| 内存占用 | 低 | 高 |
| 安全性 | Rust 后端 | JS 后端 |
| 性能 | 原生 Webview | 内置 Chromium |

### 为什么选 Python？

| 维度 | Python | Go | Node.js |
|------|--------|-----|---------|
| AI 生态 | 🟢 最强 | 🟡 较弱 | 🟡 中等 |
| 开发效率 | 🟢 高 | 🟡 中 | 🟢 高 |
| 部署难度 | 🟡 中 | 🟢 低 | 🟢 低 |
| 扩展性 | 🟢 强 | 🟢 强 | 🟡 中 |

### 为什么选 FastAPI？

- **异步支持**：原生 `async/await`
- **自动文档**：Swagger UI 自动生成
- **类型安全**：Pydantic 数据验证
- **高性能**：Starlette 底层，性能接近 Node.js

### 为什么选 LiteLLM？

| 对比项 | LiteLLM | 原生调用 | LangChain |
|--------|---------|----------|-----------|
| **学习成本** | 🟢 低 | 🟡 中 | 🟠 高 |
| **代码量** | 🟢 少 | 🟡 多 | 🟠 多 |
| **模型切换** | 🟢 改一行 | 🔴 改多行 | 🟢 改配置 |
| **依赖体积** | 🟢 小 | 🟢 小 | 🟠 大 |
| **模型支持** | 🟢 100+ | 🟡 单一 | 🟢 丰富 |

**LiteLLM 优势**：
- 统一接口调用 100+ AI 模型（OpenAI, Claude, Gemini, Ollama 等）
- 输出格式一致，切换模型只需改 `model` 参数
- 原生支持流式输出、异常处理、成本追踪
- 集成可观测性（Langfuse, Helicone 等）
- 比 LangChain 更轻量，专注 AI 调用

**示例**：
```python
from litellm import completion

# OpenAI
completion(model="openai/gpt-4o", messages=[...])

# Claude
completion(model="anthropic/claude-3-5-sonnet", messages=[...])

# Ollama 本地模型
completion(model="ollama/llama3", messages=[...])
```

### 为什么选 pnpm 而不是 Bun？

| 考量 | pnpm | Bun |
|------|------|-----|
| **稳定性** | 🟢 8 年历史，企业验证 | 🟡 2 年历史，还在验证 |
| **Tauri 生态** | 🟢 官方文档主要用 | 🟡 社区示例较少 |
| **兼容性** | 🟢 100% npm 兼容 | 🟡 少数包有问题 |
| **Windows 支持** | 🟢 成熟 | 🟡 还在完善 |
| **速度** | 🟢 快 | 🚀 更快 |

**结论**：pnpm 在稳定性、兼容性、生态支持上更优，适合 SocratX 这种需要长期维护的项目。

---

## 技术决策说明

### 移动端（未来）

```
React Native (Android/iOS)
       │
       │ HTTP
       ▼
Python FastAPI (云端部署)
```

### 插件系统

```
Python 插件接口
├── Tool 接口（工具调用）
├── Model 接口（模型切换）
└── Storage 接口（数据存储）
```

### 本地模型

```
Ollama / LM Studio
       │
       │ HTTP API
       ▼
Python FastAPI (统一接口)
```

---

## 后续扩展

---

## 参考资源

- [Tauri 2 文档](https://v2.tauri.app/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)
- [LiteLLM 文档](https://docs.litellm.ai/)
- [pnpm 文档](https://pnpm.io/)
- [nanobot GitHub](https://github.com/HKUDS/nanobot)
- [opcode GitHub](https://github.com/winfunc/opcode)
- [shadcn/ui 文档](https://ui.shadcn.com/)


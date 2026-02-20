# 基于 Nanobot 的 SocratX 架构设计

> 本文档基于对 [nanobot](https://github.com/HKUDS/nanobot) 项目的研究，为 SocratX 内核设计提供参考。

---

## 一、Nanobot 项目概述

### 1.1 项目定位

| 维度 | 详情 |
|------|------|
| **名称** | nanobot-ai |
| **定位** | 超轻量级个人 AI 助手（OpenClaw 极简版） |
| **代码规模** | ~4,000 行（比 OpenClaw 小 99%） |
| **核心语言** | Python 3.11+ |
| **AI 集成** | LiteLLM（统一 15+ 提供商） |
| **多平台** | Slack, Telegram, Discord, 飞书，钉钉，QQ 等 |
| **包管理** | pip/uv（pyproject.toml） |
| **License** | MIT |

### 1.2 核心特点

- **超轻量**：~4,000 行核心代码，99% 小于 OpenClaw 的 43 万行
- **研究友好**：代码简洁可读，易于修改和扩展
- **快速启动**：最小资源占用，快速启动
- **易于使用**：一键部署（`pip install nanobot-ai`）

### 1.3 核心功能

- 📈 24/7 实时市场分析
- 🚀 全栈软件工程师能力
- 📅 智能日常管理器
- 📚 个人知识助手
- 🔌 MCP（模型上下文协议）支持
- 🔑 多 LLM 提供商（OpenAI, Anthropic, DeepSeek, Qwen, MiniMax 等）
- 💬 多平台支持（Slack, Email, QQ, Discord, 飞书，Telegram）
- 🧠 记忆系统（知识持久化）
- ⏰ 自然语言任务调度

---

## 二、Nanobot 项目结构

```
nanobot/
├── nanobot/              # 核心代理代码（约 3,689 行）
│   ├── agent/           # 核心代理组件
│   │   ├── loop.py      # 主 AgentLoop - 核心处理引擎
│   │   ├── context.py   # ContextBuilder - 构建系统提示词
│   │   ├── memory.py    # MemoryStore - 长期记忆系统
│   │   ├── skills.py    # SkillsLoader - 技能管理
│   │   ├── subagent.py  # SubagentManager - 后台任务执行
│   │   └── tools/       # 工具实现
│   │       ├── base.py       # Tool 抽象基类
│   │       ├── registry.py   # ToolRegistry 动态工具管理
│   │       ├── filesystem.py # 文件操作
│   │       ├── shell.py      # Shell 命令执行
│   │       ├── web.py        # 网络搜索和获取
│   │       ├── message.py    # 发送消息到聊天频道
│   │       ├── spawn.py      # 生成子代理
│   │       ├── cron.py       # 定时任务
│   │       └── mcp.py        # MCP（模型上下文协议）支持
│   ├── channels/        # 平台桥接实现
│   │   ├── base.py      # BaseChannel 抽象接口
│   │   ├── manager.py   # ChannelManager - 协调所有频道
│   │   ├── slack.py     # Slack Socket 模式
│   │   ├── telegram.py  # Telegram Bot API
│   │   ├── discord.py   # Discord Gateway
│   │   ├── whatsapp.py  # WhatsApp（通过桥接）
│   │   ├── feishu.py    # 飞书 WebSocket
│   │   ├── email.py     # IMAP/SMTP 邮件
│   │   ├── qq.py        # QQ 机器人
│   │   ├── mochat.py    # Mochat (Claw IM)
│   │   └── dingtalk.py  # 钉钉 Stream
│   ├── bus/             # 消息总线，用于解耦通信
│   │   ├── events.py    # InboundMessage, OutboundMessage 数据类
│   │   └── queue.py     # MessageBus - 异步队列系统
│   ├── providers/       # LLM 提供商抽象
│   │   ├── base.py              # LLMProvider 抽象接口
│   │   ├── registry.py          # ProviderSpec 注册表（15+ 提供商）
│   │   ├── litellm_provider.py  # 基于 LiteLLM 的多提供商
│   │   ├── openai_codex_provider.py  # OpenAI Codex OAuth 支持
│   │   └── transcription.py     # 音频转录（Groq Whisper）
│   ├── config/          # 配置管理
│   │   ├── schema.py    # Pydantic 配置模型
│   │   └── loader.py    # 配置加载/保存
│   ├── session/         # 会话管理
│   │   └── manager.py   # SessionManager - 对话持久化
│   ├── cron/            # 定时任务
│   │   ├── service.py   # CronService - 任务执行
│   │   └── types.py     # CronJob, CronSchedule 类型
│   ├── heartbeat/       # 心跳服务
│   │   └── service.py   # 定期健康检查
│   ├── cli/             # CLI 命令
│   │   └── commands.py  # Typer CLI 定义
│   ├── skills/          # 内置技能
│   └── utils/           # 辅助函数
├── bridge/              # JavaScript/TypeScript 桥接（WhatsApp 等）
└── tests/               # 测试套件
```

---

## 三、Nanobot 核心组件

### 3.1 AgentLoop（核心引擎）

**文件**：`nanobot/agent/loop.py`

| 方法 | 用途 |
|------|------|
| `run()` | 处理入站消息的主循环 |
| `_run_agent_loop()` | 迭代的 LLM + 工具执行循环 |
| `_process_message()` | 处理单条消息及会话管理 |
| `_consolidate_memory()` | 将旧消息归档到 MEMORY.md/HISTORY.md |
| `process_direct()` | 直接消息处理（CLI/cron 使用） |

### 3.2 ContextBuilder（上下文构建）

**文件**：`nanobot/agent/context.py`

从以下来源构建系统提示词：
- 身份（时间、运行时、工作区）
- 引导文件（AGENTS.md、SOUL.md、USER.md 等）
- 长期记忆（MEMORY.md）
- 技能（始终加载 + 可用技能摘要）

### 3.3 ToolRegistry（工具注册表）

**文件**：`nanobot/agent/tools/registry.py`

**内置工具**：

| 类别 | 工具 |
|------|------|
| 文件操作 | `read_file`、`write_file`、`edit_file`、`list_dir` |
| Shell | `exec`（执行命令） |
| 网络 | `web_search`、`web_fetch` |
| 消息传递 | `message`（发送到聊天频道） |
| 子代理 | `spawn`（后台任务） |
| 调度 | `cron`（定时任务） |
| MCP | 来自 MCP 服务器的动态工具 |

### 3.4 SubagentManager（子代理管理器）

**文件**：`nanobot/agent/subagent.py`

生成轻量级后台代理：
- 隔离的上下文、专注的系统提示词
- 无 message/spawn 工具（防止垃圾消息）
- 结果通过总线上的系统消息广播

### 3.5 MemoryStore（记忆存储）

**文件**：`nanobot/agent/memory.py`

双层记忆系统：
- `MEMORY.md` - 长期事实（用户信息、偏好）
- `HISTORY.md` - Grep 可搜索的对话日志

### 3.6 SessionManager（会话管理器）

**文件**：`nanobot/session/manager.py`

- JSONL 持久化，存储于 `~/.nanobot/sessions/`
- 会话键：`channel:chat_id`
- 内存缓存 + 磁盘持久化

---

## 四、Nanobot 桥接系统（多平台支持）

### 4.1 BaseChannel（抽象接口）

**文件**：`nanobot/channels/base.py`

所有频道实现的抽象接口：
- `start()` - 连接到平台并监听消息
- `stop()` - 断开连接并清理
- `send(msg)` - 发送出站消息
- `is_allowed(sender_id)` - 权限检查
- `_handle_message()` - 将消息转发到总线

### 4.2 ChannelManager（频道管理器）

**文件**：`nanobot/channels/manager.py`

协调所有启用的频道：
- 从配置初始化频道
- 启动/停止所有频道
- 将出站消息分发到正确的频道

### 4.3 支持的频道

| 频道 | 协议 | 主要特性 |
|------|------|----------|
| **Telegram** | Bot API（HTTP 轮询） | 代理支持、媒体 |
| **Slack** | Socket 模式 | 线程回复、Markdown 转换 |
| **Discord** | Gateway WebSocket | 基于意图的过滤 |
| **WhatsApp** | 桥接（WebSocket） | 二维码登录、媒体转录 |
| **飞书** | WebSocket | 事件订阅 |
| **Email** | IMAP/SMTP | 轮询、自动回复 |
| **QQ** | Bot SDK | 基于 OpenID |
| **Mochat** | Socket.IO | 提及处理 |
| **钉钉** | Stream API | 员工 ID 认证 |

### 4.4 消息流（频道 → 代理）

```
用户发送消息
    ↓
Channel._handle_message()（权限检查）
    ↓
bus.publish_inbound(InboundMessage)
    ↓
AgentLoop 从总线消费
    ↓
AgentLoop 处理并响应
    ↓
bus.publish_outbound(OutboundMessage)
    ↓
ChannelManager.dispatch_outbound()
    ↓
Channel.send() → 平台
```

---

## 五、Nanobot LLM 提供商系统

### 5.1 Provider Registry（提供商注册表）

**文件**：`nanobot/providers/registry.py`

支持 15+ 提供商。每个 `ProviderSpec` 包含：
- `name` - 配置字段名
- `keywords` - 模型名称关键字（用于匹配）
- `env_key` - LiteLLM 环境变量
- `litellm_prefix` - 模型路由前缀
- `is_gateway` / `is_local` - 提供商类型标志
- `detect_by_key_prefix` - 通过 API 密钥自动检测
- `is_oauth` - 基于 OAuth 的提供商

**支持的提供商**：
OpenRouter、AiHubMix、Anthropic、OpenAI、OpenAI Codex (OAuth)、GitHub Copilot (OAuth)、DeepSeek、Gemini、智谱、DashScope (通义)、月之暗面 (Kimi)、MiniMax、vLLM (本地)、Groq

### 5.2 LiteLLMProvider

**文件**：`nanobot/providers/litellm_provider.py`

- 带前缀的模型名称解析
- 环境变量设置
- 工具调用支持（OpenAI 格式）
- 模型特定参数覆盖

### 5.3 OpenAICodexProvider

**文件**：`nanobot/providers/openai_codex_provider.py`

基于 OAuth 的 OpenAI Codex 提供商（绕过 API 密钥）。

---

## 六、Nanobot 代理循环（主执行流程）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. AgentLoop.run() - 主循环                                  │
│    - 从 bus.inbound 队列消费                                 │
│    - 处理每条消息                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. _process_message()                                        │
│    - 检查斜杠命令（/new、/help）                              │
│    - 获取/创建会话（键：channel:chat_id）                     │
│    - 如需要则整合记忆（>50 条消息）                           │
│    - 构建上下文（历史 + 记忆 + 技能）                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. _run_agent_loop() - 迭代的 LLM + 工具执行                 │
│    ┌─────────────────────────────────────────────────────┐   │
│    │ 当迭代 < max_iterations（默认 20）时：               │   │
│    │   - 使用 messages + tools 调用 LLM                   │   │
│    │   - 如果 response.has_tool_calls：                    │   │
│    │       - 并行执行所有工具                              │   │
│    │       - 将结果添加到 messages                         │   │
│    │       - 继续循环                                      │   │
│    │   - 否则：break（最终响应）                           │   │
│    └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 响应处理                                                  │
│    - 将用户/助手消息添加到会话                               │
│    - 将会话保存到磁盘（JSONL）                               │
│    - 将 OutboundMessage 发布到总线                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. ChannelManager.dispatch_outbound()                        │
│    - 按名称获取频道                                          │
│    - Channel.send() → 平台                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 七、Nanobot 配置系统

配置存储于 `~/.nanobot/config.json`（基于 Pydantic）：

```python
Config:
  - agents:（model、temperature、max_tokens、workspace 等）
  - channels:（telegram、slack、discord、whatsapp 等）
  - providers:（openrouter、anthropic、deepseek 等）
  - tools:（网络搜索、exec、MCP 服务器、工作区限制）
  - gateway:（host、port）
```

**模型匹配逻辑**：
1. 通过模型关键字匹配（如 "deepseek" → DeepSeek 提供商）
2. 回退：优先网关（OpenRouter、AiHubMix）

---

## 八、Nanobot 关键设计模式

| 模式 | 说明 |
|------|------|
| **消息总线解耦** | Channel 和 AgentLoop 通过异步队列通信 |
| **Provider 抽象** | 统一接口支持多 LLM（基于 LiteLLM） |
| **每对话一会话** | `channel:chat_id` 隔离会话 |
| **双层记忆** | MEMORY.md (长期) + HISTORY.md (日志) |
| **工具注册表** | 动态加载/执行工具 |
| **子代理系统** | 后台任务隔离执行 |
| **MCP 支持** | 动态扩展工具生态 |

---

## 九、完整数据流

```
用户输入
    ↓
Channel 接收 → InboundMessage(channel, sender_id, chat_id, content, media)
    ↓
MessageBus.publish_inbound()
    ↓
AgentLoop.consume_inbound()
    ↓
SessionManager.get_or_create(channel:chat_id)
    ↓
ContextBuilder.build_messages(history, memory, skills, current_message)
    ↓
LLMProvider.chat(messages, tools) → LLMResponse(content, tool_calls)
    ↓
    ┌─────────────────────────────────────┐
    │ 如果有工具调用：                      │
    │   ToolRegistry.execute(tool_name, args) → result
    │   将工具结果添加到 messages
    │   继续 LLM 循环                        │
    └─────────────────────────────────────┘
    ↓
Session.add_message("user", content)
Session.add_message("assistant", response, tools_used)
SessionManager.save(session)
    ↓
MessageBus.publish_outbound(OutboundMessage)
    ↓
ChannelManager.dispatch_outbound() → Channel.send()
    ↓
用户收到响应
```

---

## 十、SocratX vs Nanobot 对比

| 维度 | Nanobot | SocratX (建议) |
|------|---------|---------------|
| **目标场景** | 服务器/云端部署 | 桌面应用 (本地优先) |
| **UI 交互** | CLI + 聊天平台 | Tauri 桌面 GUI |
| **多平台** | 10+ 聊天平台 | 桌面应用 + 未来扩展 |
| **AI 调用** | Python LiteLLM | Python LiteLLM (Sidecar) |
| **系统集成** | 有限 | Tauri Rust API (强) |
| **打包方式** | pip/uv | Tauri + PyInstaller |
| **配置方式** | 配置文件 + CLI | GUI 设置 + 配置文件 |
| **记忆存储** | Markdown 文件 | Markdown + 数据库 (可选) |
| **系统通知** | 无 | Tauri 通知 API |

---

## 十一、SocratX 内核架构设计

### 11.1 整体架构

```
┌──────────────────────────────────────────────┐
│  Tauri 主应用 (Rust)                          │
│  - 窗口管理                                   │
│  - 系统托盘                                   │
│  - 文件对话框                                 │
│  - 通知                                       │
│  - 系统 API 调用                               │
└─────────────────────┬────────────────────────┘
                      │ IPC 通信 (Tauri Commands)
┌─────────────────────▼────────────────────────┐
│  React 前端 (TypeScript)                      │
│  - 聊天 UI                                    │
│  - 设置界面                                   │
│  - 会话管理                                   │
│  - 记忆可视化                                 │
│  - 状态管理 (Zustand/Context)                 │
└─────────────────────┬────────────────────────┘
                      │ HTTP (localhost)
┌─────────────────────▼────────────────────────┐
│  Python Sidecar (FastAPI + LiteLLM)          │ ← 参考 nanobot
│  ├── main.py                 # FastAPI 入口   │
│  ├── agent/                                        │
│  │   ├── loop.py           # AgentLoop 核心    │
│  │   ├── context.py        # ContextBuilder    │
│  │   ├── memory.py         # MemoryStore       │
│  │   ├── session.py        # SessionManager    │
│  │   └── tools/                                  │
│  │       ├── registry.py   # ToolRegistry      │
│  │       ├── file.py       # 文件工具          │
│  │       ├── shell.py      # Shell 工具        │
│  │       ├── web.py        # 网络工具          │
│  │       └── mcp.py        # MCP 支持          │
│  ├── providers/                                  │
│  │   ├── registry.py       # LLM 提供商注册    │
│  │   └── litellm_provider.py # LiteLLM 实现    │
│  └── config/                                     │
│      ├── schema.py         # Pydantic 配置     │
│      └── loader.py         # 配置加载/保存     │
└──────────────────────────────────────────────┘
```

### 11.2 核心模块设计

| 模块 | Nanobot 参考 | SocratX 适配 |
|------|-------------|-------------|
| **会话管理** | `session/manager.py` (JSONL) | 保留，存储位置改为应用数据目录 |
| **记忆系统** | MEMORY.md + HISTORY.md | 保留，用 Markdown 格式 |
| **工具系统** | ToolRegistry + 内置工具 | 保留 + 扩展 Tauri 系统 API |
| **上下文构建** | ContextBuilder | 保留，增加 GUI 配置 |
| **子代理** | SubagentManager | 保留，用于后台任务 |
| **MCP 支持** | MCP 客户端 | 保留，扩展工具生态 |
| **LLM 提供商** | LiteLLMProvider | 直接使用 LiteLLM |

### 11.3 推荐项目结构

```
SocratX/
├── apps/
│   └── desktop/                    # Tauri 应用
│       ├── src/                    # React 前端
│       │   ├── components/
│       │   │   ├── Chat/           # 聊天界面
│       │   │   ├── Settings/       # 设置界面
│       │   │   ├── Memory/         # 记忆可视化
│       │   │   └── Sidebar/        # 侧边栏
│       │   ├── stores/             # 状态管理
│       │   ├── hooks/              # 自定义 Hooks
│       │   └── types/              # TypeScript 类型
│       └── src-tauri/              # Tauri Rust 后端
│           ├── src/
│           │   ├── main.rs
│           │   ├── sidecar.rs      # Sidecar 管理
│           │   └── commands.rs     # IPC 命令
│           ├── tauri.conf.json
│           └── Cargo.toml
│
├── services/
│   └── agent/                      # Python Sidecar
│       ├── agent/
│       │   ├── loop.py             # AgentLoop 核心引擎
│       │   ├── context.py          # ContextBuilder
│       │   ├── memory.py           # MemoryStore
│       │   ├── session.py          # SessionManager
│       │   └── tools/
│       │       ├── registry.py     # ToolRegistry
│       │       ├── base.py         # Tool 抽象基类
│       │       ├── file.py         # 文件工具
│       │       ├── shell.py        # Shell 工具
│       │       ├── web.py          # 网络工具
│       │       └── mcp.py          # MCP 支持
│       ├── providers/
│       │   ├── registry.py         # LLM 提供商注册
│       │   └── litellm_provider.py # LiteLLM 实现
│       ├── config/
│       │   ├── schema.py           # Pydantic 配置模型
│       │   └── loader.py           # 配置加载/保存
│       ├── main.py                 # FastAPI 入口
│       ├── requirements.txt
│       └── pyproject.toml
│
├── packages/                       # 共享包
│   └── types/                      # TypeScript 类型定义
│
├── pnpm-workspace.yaml
├── package.json
├── pnpm-lock.yaml
└── docs/
    ├── 技术栈说明.md
    └── 基于 nanobot 的架构设计.md
```

### 11.4 差异化设计

| 特性 | Nanobot | SocratX |
|------|---------|---------|
| **配置方式** | `~/.nanobot/config.json` + CLI | GUI 设置 + 配置文件 |
| **记忆存储** | Markdown 文件 | Markdown + 数据库 (可选) |
| **工具调用** | Python 原生 | Python + Tauri Rust API |
| **系统通知** | 无 | Tauri 通知 API |
| **文件访问** | Python 文件系统 | Tauri FS API + Python |
| **打包部署** | pip 安装 | 一键安装 exe/dmg |
| **多语言支持** | 有限 | i18n 完整支持 |
| **主题切换** | 无 | 深色/浅色主题 |

---

## 十二、实施建议

### 12.1 第一阶段：核心框架

1. **初始化项目结构**
   - 创建 pnpm workspace
   - 配置 Tauri 2 + React 前端
   - 配置 Python Sidecar

2. **实现 AgentLoop 核心**
   - 基于 nanobot 的 `agent/loop.py`
   - 适配 Tauri IPC 通信
   - 实现基础对话功能

3. **实现会话管理**
   - 基于 nanobot 的 `session/manager.py`
   - JSONL 持久化
   - 多会话支持

### 12.2 第二阶段：工具系统

1. **实现 ToolRegistry**
   - 基于 nanobot 的 `tools/registry.py`
   - 内置工具：文件、Shell、网络

2. **集成 LiteLLM**
   - 基于 nanobot 的 `providers/litellm_provider.py`
   - 支持 OpenAI, Claude, Gemini, Ollama

3. **实现 MCP 支持**
   - 基于 nanobot 的 `tools/mcp.py`
   - 动态扩展工具生态

### 12.3 第三阶段：GUI 与优化

1. **React 前端开发**
   - 聊天界面
   - 设置界面
   - 记忆可视化

2. **Tauri 集成**
   - Sidecar 管理
   - 系统通知
   - 文件对话框

3. **性能优化**
   - 流式输出
   - 上下文压缩
   - 缓存策略

---

## 十三、关键文件参考

### Nanobot 关键文件

| 文件 | 用途 | SocratX 参考 |
|------|------|-------------|
| `nanobot/__main__.py` | 主入口点 | `services/agent/main.py` |
| `nanobot/agent/loop.py` | 核心代理处理引擎 | `services/agent/agent/loop.py` |
| `nanobot/agent/context.py` | 系统提示词构建 | `services/agent/agent/context.py` |
| `nanobot/channels/manager.py` | 频道协调 | （不需要，用 Tauri 替代） |
| `nanobot/bus/queue.py` | 消息总线实现 | `services/agent/bus/queue.py` |
| `nanobot/providers/registry.py` | LLM 提供商注册表 | `services/agent/providers/registry.py` |
| `nanobot/config/schema.py` | 配置模型 | `services/agent/config/schema.py` |
| `nanobot/session/manager.py` | 会话持久化 | `services/agent/session/manager.py` |

### SocratX 新增文件

| 文件 | 用途 |
|------|------|
| `apps/desktop/src-tauri/src/sidecar.rs` | Sidecar 启动与管理 |
| `apps/desktop/src-tauri/src/commands.rs` | Tauri IPC 命令 |
| `apps/desktop/src/components/Chat/` | 聊天界面组件 |
| `apps/desktop/src/stores/` | 状态管理 |

---

## 十四、总结

### Nanobot 核心价值

- **~4,000 行**核心代码（比 OpenClaw 小 99%）
- **15+ LLM 提供商**通过统一的 LiteLLM 接口
- **多平台支持**（Slack, Telegram, Discord, 飞书，钉钉，QQ 等）
- **完整 Agent 功能**（工具调用、记忆系统、子代理、MCP）
- **简洁架构**（消息总线、Provider 抽象、会话隔离）

### SocratX 借鉴要点

1. **AgentLoop 核心引擎**：迭代 LLM + 工具执行循环
2. **消息总线解耦**：Channel 和 AgentLoop 通过异步队列通信
3. **双层记忆系统**：MEMORY.md (长期) + HISTORY.md (日志)
4. **ToolRegistry 动态工具管理**：内置工具 + MCP 扩展
5. **SessionManager 会话隔离**：每对话一会话
6. **LiteLLM 统一接口**：支持 100+ AI 模型
7. **SubagentManager 子代理**：后台任务隔离执行

### SocratX 差异化优势

- **桌面应用体验**：Tauri 原生 GUI，优于 CLI/聊天平台
- **系统集成能力**：Tauri Rust API 调用系统功能
- **本地优先**：数据本地存储，隐私安全
- **一键安装**：打包为 exe/dmg，用户无需技术背景
- **多语言支持**：完整 i18n，支持中文优先

---

## 参考资源

- [Nanobot GitHub](https://github.com/HKUDS/nanobot)
- [Nanobot PyPI](https://pypi.org/project/nanobot-ai/)
- [LiteLLM 文档](https://docs.litellm.ai/)
- [Tauri 2 文档](https://v2.tauri.app/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

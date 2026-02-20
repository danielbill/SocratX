本文档用于记录构建、完善整个项目开发测试打包发布环境的待办事项。
本文档不记录任何开发任务

> **最后更新**: 2026 年 2 月 20 日 - 测试框架完成

---

## 项目当前状态

### 已完成 ✅

**Monorepo 架构**
- [x] pnpm workspace 配置完成
- [x] 根 package.json 配置完成
- [x] 项目结构：apps/, services/, packages/, docs/

**前端 (apps/desktop)**
- [x] React 19 + TypeScript + Vite 7 配置
- [x] Tauri 2 配置 (src-tauri/)
- [x] 基础组件目录：components/chat/, components/ui/
- [x] 上下文：contexts/ThemeContext.tsx
- [x] Hooks: hooks/useChat.ts, hooks/useAgent.ts
- [x] 工具函数：lib/api.ts, lib/utils.ts
- [x] 测试框架：Vitest + React Testing Library
- [x] 测试示例：utils, api, ChatInput, ChatMessage

**后端 (services/agent)**
- [x] FastAPI 入口 (main.py)
- [x] AgentLoop 核心 (agent/loop.py)
- [x] ContextBuilder (agent/context.py)
- [x] SessionManager (agent/session.py)
- [x] MemoryStore (agent/memory.py)
- [x] 工具系统基类 (agent/tools/base.py, registry.py)
- [x] 消息总线 (bus/events.py, queue.py)
- [x] LLM 提供商 (providers/litellm_provider.py, registry.py)
- [x] 配置系统 (config/schema.py, loader.py)
- [x] 测试框架：pytest + pytest-asyncio
- [x] 测试示例：config, memory, session, tools, API

**测试与 CI/CD**
- [x] Rust 测试配置
- [x] GitHub Actions 工作流
- [x] 测试文档（docs/测试指南.md）

**共享包 (packages/shared)**
- [x] TypeScript 类型定义占位

**文档**
- [x] 技术栈说明.md
- [x] 基于 nanobot 的架构设计.md
- [x] SocratX 项目开发测试设计.md
- [x] 测试指南.md
- [x] 测试/核心流程测试设计.md

---

### 进行中 🚧

- [ ] 前端 UI 组件实现（参考 opcode）
- [ ] Python 工具实现（文件、Shell、网络）

---

### 已完成 ✅（新增）

**测试框架**
- [x] Vitest 配置（前端）
  - [x] `apps/desktop/vite.config.ts` - Vitest 配置
  - [x] `apps/desktop/src/test/setup.ts` - 测试全局设置
  - [x] `apps/desktop/package.json` - 测试脚本
- [x] 前端测试示例
  - [x] `src/lib/utils.test.ts` - 工具函数测试
  - [x] `src/lib/api.test.ts` - API 调用测试
  - [x] `src/components/chat/ChatInput.test.tsx` - 输入框组件测试
  - [x] `src/components/chat/ChatMessage.test.tsx` - 消息组件测试
- [x] pytest 配置（Python）
  - [x] `services/agent/pytest.ini` - pytest 配置
  - [x] `services/agent/requirements.txt` - 测试依赖
  - [x] `services/agent/tests/conftest.py` - 测试夹具
- [x] Python 测试示例
  - [x] `tests/test_config/test_schema.py` - 配置系统测试
  - [x] `tests/test_agent/test_memory.py` - 记忆系统测试
  - [x] `tests/test_agent/test_session.py` - 会话管理测试
  - [x] `tests/test_tools/test_registry.py` - 工具注册表测试
  - [x] `tests/test_api/test_chat.py` - API 接口测试
- [x] Rust 测试配置
  - [x] `apps/desktop/src-tauri/Cargo.toml` - dev-dependencies
  - [x] `apps/desktop/src-tauri/src/lib.rs` - 单元测试
- [x] CI/CD GitHub Actions
  - [x] `.github/workflows/test.yml` - 测试工作流
- [x] 测试文档
  - [x] `docs/测试指南.md` - 测试使用指南

### 搭建前端架构 todo list

- [ ] 创建 `stores/` 目录 - Zustand 状态管理
  - [ ] `stores/chat.ts` - 对话状态管理
  - [ ] `stores/session.ts` - 会话状态管理
  - [ ] `stores/settings.ts` - 设置状态管理
  - [ ] `stores/memory.ts` - 记忆状态管理

- [ ] 创建 `components/layout/` 目录 - 布局组件
  - [ ] `Titlebar.tsx` - 自定义标题栏（参考 opcode CustomTitlebar）
  - [ ] `Sidebar.tsx` - 侧边栏（会话列表、项目浏览）
  - [ ] `MainLayout.tsx` - 主布局容器

- [ ] 创建 `components/settings/` 目录 - 设置界面
  - [ ] `SettingsPanel.tsx` - 设置面板主组件
  - [ ] `ProviderConfig.tsx` - LLM 提供商配置
  - [ ] `ToolConfig.tsx` - 工具配置界面

- [ ] 创建 `components/memory/` 目录 - 记忆可视化
  - [ ] `MemoryView.tsx` - MEMORY.md 查看/编辑
  - [ ] `HistoryView.tsx` - HISTORY.md 查看搜索

- [ ] 创建 `components/tools/` 目录 - 工具管理
  - [ ] `ToolRegistry.tsx` - 工具列表展示
  - [ ] `MCPManager.tsx` - MCP 服务器管理

- [ ] 创建 `hooks/` 目录 - 自定义 Hooks
  - [ ] `useChat.ts` - 对话 Hook
  - [ ] `useAgent.ts` - Agent 通信 Hook
  - [ ] `useTheme.ts` - 主题 Hook

- [ ] 创建 `types/` 目录 - 类型定义
  - [ ] `agent.ts` - Agent 相关类型
  - [ ] `session.ts` - 会话类型
  - [ ] `config.ts` - 配置类型

- [ ] 扩展 `lib/` 目录
  - [ ] `lib/agent.ts` - Agent API 客户端

---

### 搭建后端架构 todo list

- [x] Phase 1: Python 后端核心（已完成）
  - [x] `agent/loop.py` - AgentLoop 核心引擎
  - [x] `agent/context.py` - ContextBuilder
  - [x] `agent/session.py` - SessionManager
  - [x] `agent/memory.py` - MemoryStore
  - [x] `agent/tools/` - 工具系统（base.py, registry.py）
  - [x] `providers/` - LLM 提供商（registry.py, litellm_provider.py）
  - [x] `config/` - 配置系统（schema.py, loader.py）
  - [x] `bus/` - 消息总线（events.py, queue.py）
  - [x] `main.py` - FastAPI 入口更新

- [ ] Phase 2: Python 后端扩展
  - [ ] `agent/subagent.py` - SubagentManager 子代理管理
  - [ ] `agent/tools/file.py` - 文件工具扩展
  - [ ] `agent/tools/shell.py` - Shell 工具扩展
  - [ ] `agent/tools/web.py` - 网络工具扩展
  - [ ] `agent/tools/mcp.py` - MCP 支持
  - [ ] `agent/tools/cron.py` - 定时任务
  - [ ] `agent/tools/spawn.py` - 子代理生成
  - [ ] `cron/` - 定时任务服务
    - [ ] `service.py`
    - [ ] `types.py`
  - [ ] `heartbeat/` - 心跳服务
    - [ ] `service.py`

- [ ] Phase 3: 后端集成测试
  - [ ] 安装依赖验证
  - [ ] 启动服务验证
  - [ ] API 端点测试

---

### 搭建测试框架 todo list

> **状态**: ✅ 已完成 - 2026 年 2 月 20 日

**前端测试（Vitest）**
- [x] 安装 Vitest 和相关依赖
- [x] 配置 vite.config.ts
- [x] 创建 src/test/setup.ts
- [x] 编写 utils.test.ts
- [x] 编写 api.test.ts
- [x] 编写 ChatInput.test.tsx
- [x] 编写 ChatMessage.test.tsx

**Python 测试（pytest）**
- [x] 添加 pytest 依赖到 requirements.txt
- [x] 创建 pytest.ini 配置
- [x] 创建 tests/conftest.py 夹具
- [x] 编写 test_config/test_schema.py
- [x] 编写 test_agent/test_memory.py
- [x] 编写 test_agent/test_session.py
- [x] 编写 test_tools/test_registry.py
- [x] 编写 test_api/test_chat.py

**Rust 测试**
- [x] 配置 Cargo.toml dev-dependencies
- [x] 编写 lib.rs 单元测试

**CI/CD**
- [x] 创建 .github/workflows/test.yml
- [x] 配置前端测试任务
- [x] 配置 Python 测试任务
- [x] 配置 Rust 测试任务

**文档**
- [x] 编写 docs/测试指南.md

---

### 后续测试任务

- [ ] E2E 测试（Playwright）
- [ ] 前端组件测试覆盖率提升到 80%+
- [ ] Python 后端测试覆盖率提升到 90%+
- [ ] Tauri 集成测试

### 部署与打包 todo list

- [ ] 开发环境配置
  - [ ] 配置环境变量模板（.env.example）
  - [ ] 编写开发启动脚本

- [ ] 生产构建
  - [ ] Tauri 打包配置
  - [ ] Python 打包（PyInstaller）

- [ ] 安装包制作
  - [ ] Windows (.exe)
  - [ ] macOS (.dmg)
  - [ ] Linux (.AppImage)

---


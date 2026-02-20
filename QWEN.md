# SocratX

本地优先的 AI 助手桌面应用。

## 技术栈

- **前端**: Tauri 2 + React 19 + TypeScript + TailwindCSS 4
- **后端**: Python FastAPI + LiteLLM
- **架构**: Monorepo (pnpm workspace)

## 快速开始

```bash
pnpm install:all    # 安装依赖
pnpm tauri:dev      # 启动开发
```

## 项目结构

```
apps/desktop/        # Tauri 桌面应用
services/agent/      # Python AI 服务
packages/shared/     # 共享类型
docs/                # 文档
```

## 核心文档

| 文件                                                      | 内容         |
| --------------------------------------------------------- | ------------ |
| [SocratX技术栈.md](docs/SocratX技术栈.md)                 | 技术规格     |
| [基于nanobot的架构设计.md](docs/基于nanobot的架构设计.md) | 后端架构参考 |
| [基于opcode的界面设计.md](docs/基于opcode的界面设计.md)   | UI 设计参考  |
| [项目环境待办事项](project/env_todos.md)                  |              |
[项目计划](project/plan.md)
[项目开发待办任务](project/develop_todos.md)
[项目测试待办任务](project/test_todos.md)

## 核心模块

- `services/agent/agent/loop.py` - AgentLoop (LLM + 工具循环)
- `services/agent/agent/session.py` - SessionManager (JSONL 持久化)
- `services/agent/agent/memory.py` - MemoryStore (MEMORY.md + HISTORY.md)
- `services/agent/agent/tools/registry.py` - 工具注册表
- `services/agent/providers/` - 15+ LLM 提供商

## API 端点

```
POST   /api/chat          # 对话
GET    /api/sessions      # 会话列表
DELETE /api/sessions/{id} # 删除会话
GET    /api/memory        # 获取记忆
POST   /api/memory        # 更新记忆
GET    /api/config        # 获取配置
GET    /health            # 健康检查
```

## 环境要求

- Node.js 18+
- pnpm 8+
- Python 3.11+
- Rust 1.70+

## 参考项目
- 后端架构：[nanobot](https://github.com/HKUDS/nanobot) 
本地代码：D:\github\nanobot

- 界面实现：- [opcode](https://github.com/winfunc/opcode) 
本地代码：D:\github\opcode


## 你的默认角色

[SocratX测试总监](docs/提示词/项目测试总监.md)

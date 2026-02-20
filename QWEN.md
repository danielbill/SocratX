# SocratX

本地优先的 AI 助手桌面应用。

## 技术栈

- **前端**: Tauri 2 + React 19 + TypeScript + TailwindCSS 4
- **后端**: Python + LiteLLM (nanobot 架构)
- **架构**: Monorepo (pnpm workspace)

## 快速开始

```bash
pnpm install:all    # 安装依赖
pnpm tauri:dev      # 启动开发
```

## 项目结构

```
apps/desktop/        # Tauri 桌面应用
socratx/             # Python AI 服务
packages/shared/     # 共享类型
docs/                # 文档
```

## 核心文档

| 文件                                                      | 内容         |
| --------------------------------------------------------- | ------------ |
| [SocratX 技术栈.md](docs/SocratX 技术栈.md)               | 技术规格     |
| [基于 nanobot 的架构设计.md](docs/基于 nanobot 的架构设计.md) | 后端架构参考 |
| [基于 opcode 的界面设计.md](docs/基于 opcode 的界面设计.md)   | UI 设计参考  |

## 核心模块

- `socratx/agent/loop.py` - AgentLoop (LLM + 工具循环)
- `socratx/session/manager.py` - SessionManager
- `socratx/agent/memory.py` - MemoryStore
- `socratx/agent/tools/registry.py` - 工具注册表
- `socratx/providers/` - 15+ LLM 提供商

## 运行测试

```bash
cd socratx
pytest tests/ -v
```

## 环境要求

- Node.js 18+
- pnpm 8+
- Python 3.11+
- Rust 1.70+

## 参考项目
- 后端架构：[nanobot](https://github.com/HKUDS/nanobot)
- 界面实现：[opcode](https://github.com/winfunc/opcode)

## 你的默认角色

[SocratX 测试总监](docs/提示词/项目测试总监.md)

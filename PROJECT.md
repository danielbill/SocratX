# SocratX 项目设置

> **最后更新**: 2026 年 2 月 20 日

## 快速开始

```bash
# 安装所有依赖
pnpm install:all

# 启动开发环境
pnpm tauri:dev
```

## 项目结构

```
SocratX/
├── apps/desktop/          # Tauri 2 + React 桌面应用
├── services/agent/        # Python FastAPI (基于 nanobot)
├── packages/shared/       # 共享类型定义
├── docs/                  # 项目文档
├── package.json           # Monorepo 根配置
└── pnpm-workspace.yaml
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 19 + TypeScript + Tauri 2 |
| UI | shadcn/ui + TailwindCSS 4 |
| 后端 | Python FastAPI + LiteLLM |
| 测试 | Vitest + pytest |

## 开发命令

```bash

命令	说明
pnpm install:all	安装所有依赖（首次使用）
pnpm run dev	只启动前端 Vite 开发服务器
pnpm tauri:build	构建生产版本桌面应用
pnpm run check	TypeScript + Rust 类型检查
pnpm run test	运行前端测试
cd apps/desktop && pnpm run test	运行桌面应用测试
pnpm tauri:dev
```

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


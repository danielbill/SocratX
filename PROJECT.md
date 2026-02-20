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
├── socratx/               # Python 后端 (基于 nanobot)
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
| 后端 | Python + LiteLLM (nanobot 架构) |
| 测试 | Vitest + pytest |

## 开发命令

| 命令 | 说明 |
|------|------|
| `pnpm install:all` | 安装所有依赖（首次使用） |
| `pnpm run dev` | 只启动前端 Vite 开发服务器 |
| `pnpm tauri:build` | 构建生产版本桌面应用 |
| `pnpm run check` | TypeScript + Rust 类型检查 |
| `pnpm run test` | 运行前端测试 |
| `cd apps/desktop && pnpm run test` | 运行桌面应用测试 |
| `pnpm tauri:dev` | 启动 Tauri 开发环境 |
| `cd socratx && pytest` | 运行后端测试 |

## 后端服务

### 运行测试
```bash
cd socratx
pytest tests/ -v
```

### 配置
配置文件位于 `~/.nanobot/config.json`

### 环境变量
```bash
NANOBOT_AGENTS__DEFAULTS__MODEL=zhipu/glm-4.7
NANOBOT_PROVIDERS__ZHIPU__API_KEY=your-api-key
```

## 环境要求

- Node.js 18+
- pnpm 8+
- Python 3.11+
- Rust 1.70+

## 参考项目
- 后端架构：[nanobot](https://github.com/HKUDS/nanobot)
- 界面实现：[opcode](https://github.com/winfunc/opcode)


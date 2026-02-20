OpenCode 技术栈分析
核心架构
层级	技术
运行时	Bun (替代 Node.js)
语言	TypeScript 5.8+
包管理	Bun + Turborepo (monorepo)
构建工具	Vite 7.0+
前端技术
模块	技术栈
UI 框架	SolidJS 1.9+
样式	TailwindCSS 4.0+
状态管理	Solid Primitives
Markdown	Marked + Shiki
虚拟列表	Virtua
桌面应用
平台	技术
框架	Tauri 2.0+ (Rust 后端)
前端	SolidJS + Vite
插件	Tauri Plugins (clipboard, dialog, shell, store, notification, etc.)
后端/核心服务
功能	技术
Web 框架	Hono
AI 集成	Vercel AI SDK (ai 包)
模型支持	OpenAI, Anthropic, Google, Groq, Bedrock, etc.
数据库	Drizzle ORM (SQLite)
验证	Zod
文件监听	Parcel Watcher
终端 UI	@opentui/core
项目结构
packages/
├── opencode      # 核心 CLI (Bun + TUI)
├── desktop       # 桌面应用 (Tauri + SolidJS)
├── app           # 共享应用逻辑
├── ui            # 共享 UI 组件
├── web           # Web 前端
├── console       # 控制台相关
├── sdk           # SDK (JS)
├── plugin        # 插件系统
└── ...
关键特点
Bun 优先：全栈使用 Bun 运行时
SolidJS：比 React 更轻量高性能
Tauri 2.0：替代 Electron，更小的包体积
AI 中立：支持 20+ AI 提供商
Monorepo：Turborepo 管理多包
TUI + GUI：同时支持终端和图形界面
# 基于 opcode 的 SocratX 界面设计

## 概述

本文档基于 [opcode](https://github.com/winfunc/opcode) 项目的成熟设计模式，为 SocratX 定义完整的界面设计方案。

**opcode 本地路径**: `D:\github\opcode`

## 设计原则

### 1. 简洁优先
- 界面元素最小化，突出核心功能（AI 对话）
- 使用空白区域提升可读性
- 避免不必要的装饰元素

### 2. 响应式布局
- 支持不同窗口尺寸
- 灵活的组件排列方式

### 3. 深色模式优先
- 默认使用深色主题，减轻视觉疲劳
- 支持浅色模式切换

---

## 全局设计系统

### 颜色规范

**来源**: `opcode\src\styles.css` + TailwindCSS v4

```css
/* 浅色模式 */
--color-background: 0 0% 100%;           /* #ffffff */
--color-foreground: 222.2 84% 4.9%;      /* #1a1a1a */
--color-card: 0 0% 100%;                /* #ffffff */
--color-card-foreground: 222.2 84% 4.9%;  /* #1a1a1a */
--color-primary: 222.2 47.4% 11.2%;      /* #1e3a5f */
--color-primary-foreground: 210 40% 98%;   /* #fafafa */

/* 深色模式 */
--color-background: 222.2 84% 4.9%;      /* #1a1a1a */
--color-foreground: 210 40% 98%;          /* #fafafa */
--color-card: 222.2 84% 4.9%;             /* #1a1a1a */
--color-card-foreground: 210 40% 98%;    /* #fafafa */
--color-primary: 210 40% 98%;             /* #3b82f6 */
--color-primary-foreground: 222.2 47.4% 11.2%; /* #eff6ff */
```

### 字体系统

```css
/* 字体家族 */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;

/* 字体大小 */
--font-size-xs: 0.75rem;      /* 12px - caption */
--font-size-sm: 0.875rem;     /* 14px - body-small */
--font-size-base: 1rem;       /* 16px - body */
--font-size-lg: 1.125rem;      /* 18px - body-large */
--font-size-xl: 1.25rem;       /* 20px - h3 */
--font-size-2xl: 1.5rem;       /* 24px - h2 */
--font-size-3xl: 1.875rem;     /* 30px - h1 */
```

### 间距系统

```css
/* 间距单位 */
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;     /* 24px */
--spacing-xl: 2rem;      /* 32px */
```

### 圆角

```css
--radius-sm: 0.25rem;    /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
```

---

## 页面布局

### 主窗口布局

**来源**: `opcode\src\App.tsx`

```
┌────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────┐ │
│  │ SocratX                    [主题] [设置]      │ │  ← CustomTitlebar
│  └─────────────────────────────────────────────┘ │
├────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────┬───────────────────────────┐  │
│  │                 │                           │  │
│  │   会话列表        │    对话区域              │  │
│  │   (可收起)        │                           │  │
│  │                 │  ┌─────────────────────┐  │  │
│  │ ┌─────────────┐ │  │                     │  │  │
│  │ │ Session 1   │ │  │   消息列表滚动区    │  │  │
│  │ ├─────────────┤ │  │                     │  │  │
│  │ │ Session 2   │ │  │  ┌─────────────────┐  │  │  │
│  │ ├─────────────┤ │  │  │ 消息气泡       │  │  │  │
│  │ │ Session 3   │ │  │  │                 │  │  │  │
│  │ └─────────────┘ │  │  └─────────────────┘  │  │  │
│  │                 │  │                     │  │  │
│  │ [+ 新建会话]    │  │  ┌─────────────────┐  │  │  │
│  │                 │  │  │ 输入框           │  │  │  │
│  │                 │  │  └─────────────────┘  │  │  │
│  │                 │  │                     │  │  │
│  └─────────────────┴───────────────────────────┘  │
│                                                   │
└────────────────────────────────────────────────┘
```

### 响应式断点

- **默认**: 侧边栏 + 主内容区
- **< 768px**: 侧边栏可折叠，使用抽屉式导航

---

## 组件设计

### 1. 消息气泡 (ChatMessage)

**来源**: `opcode\src\components\SessionList.tsx` + `opcode\src\components\claude-code-session\MessageList.tsx`

#### 设计规范

| 状态 | 样式 | 颜色 |
|------|------|------|
| **用户消息** | 右对齐，圆角矩形 | `bg-primary text-primary-foreground` |
| **AI 消息** | 左对齐，圆角矩形 | `bg-muted` |
| **系统消息** | 居中，小字号，半透明 | `text-muted-foreground text-xs italic` |

#### 代码结构

```tsx
// 参考: opcode/src/components/claude-code-session/MessageList.tsx
interface MessageProps {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

// 样式规范
const messageStyles = {
  user: `
    justify-end
    max-w-[80%]
    bg-primary
    text-primary-foreground
    rounded-lg
    p-3
  `,
  assistant: `
    justify-start
    max-w-[80%]
    bg-muted
    rounded-lg
    p-3
  `,
  system: `
    justify-center
    text-xs
    text-muted-foreground
    italic
    my-2
  `
}
```

#### 交互状态

- **悬停**: 轻微放大 (scale-105)
- **代码块**: 语法高亮 + 复制按钮
- **引用**: 左侧竖线 + 缩进

---

### 2. 会话列表 (SessionList)

**来源**: `opcode\src\components\SessionList.tsx`

#### 设计规范

```
┌─────────────────────────────────────┐
│  📅 项目路径                          │
│  ├─────────────────────────────────┤  │
│  │ Session 1              [时钟]      │  │
│  │ "第一条消息预览..."                │  │
│  │ 2024年2月20日        [12]        │  │
│  ├─────────────────────────────────┤  │
│  │ Session 2              [时钟]      │  │
│  │ "如何使用 Python..."                │  │
│  │ 2024年2月19日                     │  │
│  └─────────────────────────────────┘  │
│  [<] [1] [2] [>]                      │  ← 分页控件
└─────────────────────────────────────┘
```

#### 卡片布局

- 每页显示 **12 条**会话
- 使用 `framer-motion` 做入场动画
- 悬停效果: `hover:bg-accent/50`

#### 关键元素

```tsx
// 参考 opcode 的 SessionList 实现
<Card
  className="p-3 hover:bg-accent/50 transition-all duration-200 cursor-pointer"
  onClick={() => onSessionClick(session)}
>
  {/* 头部: 图标 + 日期 */}
  <div className="flex items-center justify-between mb-2">
    <Clock className="h-4 w-4 text-primary shrink-0 mt-0.5" />
    <span>{formatDate(session.created_at)}</span>
  </div>

  {/* 首条消息预览 */}
  <p className="text-sm text-muted-foreground line-clamp-2">
    {session.first_message}
  </p>

  {/* 底部: Session ID */}
  <p className="text-xs text-muted-foreground font-mono">
    {session.id.slice(-8)}
  </p>
</Card>
```

---

### 3. 输入框 (ChatInput)

**来源**: `opcode\src\components\FloatingPromptInput.tsx`

#### 设计规范

```
┌──────────────────────────────────────────┐
│  ┌────────────────────────────────────┐    │
│  │ 输入你的问题... (Enter 发送)           │    │  ← Textarea
│  │                                       │    │
│  │                                       │    │
│  └────────────────────────────────────┘    │
│                              [发送图标]    │
└──────────────────────────────────────────┘
```

#### 特性

- **自动高度**: 最小 60px，最大 200px
- **快捷键**:
  - `Enter` - 发送
  - `Shift + Enter` - 换行
  - `Ctrl/Cmd + K` - 清空输入
- **字符计数**: 可选显示当前字符数
- **粘贴处理**: 自动清理格式

#### 代码实现

```tsx
<Textarea
  value={input}
  onChange={(e) => setInput(e.target.value)}
  onKeyDown={(e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }}
  placeholder="输入你的问题... (Enter 发送, Shift+Enter 换行)"
  className="min-h-[60px] max-h-[200px] resize-none"
/>
```

---

### 4. 自定义标题栏 (CustomTitlebar)

**来源**: `opcode\src\components\CustomTitlebar.tsx`

```
┌────────────────────────────────────────────────┐
│  ● ● ●                              SocratX    [⚙] [≡] │
└────────────────────────────────────────────────┘
     ↑            ↑          ↑         ↑
  窗口控制      标题      快捷操作    关闭
```

#### 功能按钮

| 图标 | 功能 | 快捷键 |
|------|------|--------|
| ⚙ | 设置面板 | - |
| ≡ | 使用统计 | - |
| 🌙 | 主题切换 | Ctrl/Cmd + Shift + T |

---

### 5. 设置面板 (Settings)

**来源**: `opcode\src\components\Settings.tsx`

#### 分组结构

```
┌─────────────────────────────────────┐
│  设置                          [×]   │
├─────────────────────────────────────┤
│  🎨 外观                            │
│     ├─ 主题: ◉ 深色 ○ 浅色 ○ 跟随系统    │
│     └─ 字体大小: ○ 小 ○ 中 ○ 大              │
│                                         │
│  🤖 AI 模型                          │
│     ├─ 提供商: ○ OpenAI ○ Claude ○ 本地  │
│     └─ 模型: gpt-4o ▼                    │
│                                         │
│  🔌 API 配置                         │
│     ┌─────────────────────────────┐   │
│     │ API Key: ••••••••••••••••     │   │
│     │ [测试连接]                     │   │
│     └─────────────────────────────┘   │
│                                         │
│  [保存]                               │
└─────────────────────────────────────┘
```

---

## 动画效果

**来源**: `opcode` 使用 `framer-motion`

### 入场动画

```tsx
// Session 卡片入场
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, delay: index * 0.05 }}
>
  <Card>...</Card>
</motion.div>
```

### 交互动画

- **按钮悬停**: `hover:scale-105 transition-transform duration-200`
- **卡片点击**: `active:scale-95 transition-transform duration-100`
- **页面切换**: `AnimatePresence mode="popLayout"`

---

## 状态管理

**来源**: `opcode\src\contexts\` + `zustand`

### 状态结构

```typescript
// 参考 opcode 的状态管理模式
interface AppState {
  // 主题
  theme: 'light' | 'dark' | 'system'
  setTheme: (theme: Theme) => void

  // 会话
  sessions: Session[]
  currentSessionId: string | null

  // 消息
  messages: Record<string, Message[]>

  // UI 状态
  sidebarOpen: boolean
  isLoading: boolean
}
```

### Zustand Store 模式

```typescript
// 参考 opcode 的使用方式
import { create } from 'zustand'

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,

  sendMessage: async (content: string) => {
    set({ isLoading: true })
    // API 调用
    set({ isLoading: false })
  },

  clearMessages: () => set({ messages: [] })
}))
```

---

## 图标系统

**来源**: `opcode` 使用 `lucide-react`

### 常用图标

| 功能 | 图标 | 说明 |
|------|------|------|
| 时钟 | `Clock` | 会话时间戳 |
| 消息 | `MessageSquare` | 消息数量 |
| 设置 | `Settings` | 设置入口 |
| 发送 | `Send` | 发送按钮 |
| 机器人 | `Bot` | AI 标识 |
| 文件夹 | `FolderCode` | 项目浏览 |

---

## 可访问性

### 键盘导航

| 快捷键 | 功能 |
|--------|------|
| `Ctrl/Cmd + K` | 清空输入框 |
| `Ctrl/Cmd + Shift + T` | 切换主题 |
| `Escape` | 关闭对话框 |
| `Tab` / `Shift+Tab` | 焦点导航 |

### 语义化 HTML

```tsx
<nav aria-label="主导航">
  <ul role="list">
    <li><button aria-label="新建会话">+</button></li>
  </ul>
</nav>

<main role="main" aria-label="对话区域">
  {/* 消息列表 */}
</main>

<aside aria-label="会话历史">
  {/* 会话列表 */}
</aside>
```

---

## 响应式设计

### 窗口尺寸适配

| 宽度 | 布局 |
|------|------|
| > 1200px | 侧边栏 + 主内容 + 可选信息面板 |
| 768px - 1200px | 侧边栏 + 主内容 |
| < 768px | 移动端布局，侧边栏折叠 |

### 组件适配

```css
/* 响应式消息宽度 */
.message-bubble {
  max-width: 80%;
}

@media (max-width: 640px) {
  .message-bubble {
    max-width: 95%;
  }
}

/* 响应式侧边栏 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    inset-y: 0;
    z-index: 50;
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
  }
}
```

---

## 性能优化

### 虚拟滚动

**来源**: `opcode` 使用 `@tanstack/react-virtual`

```tsx
// 用于大量消息列表
import { useVirtualizer } from '@tanstack/react-virtual'

const { virtualItems, getTotalSize } = useVirtualizer({
  count: messages.length,
  getScrollElement: () => scrollRef.current,
  estimateSize: () => 100, // 预估每条消息高度
  overscan: 5,
})
```

### 代码分割

```typescript
// 路由级代码分割
const ChatContainer = lazy(() => import('./components/ChatContainer'))
const Settings = lazy(() => import('./components/Settings'))
```

---

## 开发指南

### 新增组件步骤

1. **确定组件类型**
   - UI 基础组件 → `components/ui/`
   - 功能组件 → `components/features/`

2. **从 opcode 参考模式**
   - 查找类似功能的实现
   - 复用样式和交互模式

3. **保持一致性**
   - 使用相同的颜色变量
   - 遵循相同的命名约定
   - 复用动画效果

### 样式指南

```tsx
// 导入工具函数
import { cn } from "@/lib/utils"

// 组合 className
<div className={cn(
  "base-styles",
  condition && "conditional-styles",
  props.className
)} />
```

---

## 参考文件映射

| SocratX 组件 | opcode 参考文件 |
|-------------|---------------|
| ChatMessage.tsx | `src/components/claude-code-session/MessageList.tsx` |
| SessionList.tsx | `src/components/SessionList.tsx` |
| ChatInput.tsx | `src/components/FloatingPromptInput.tsx` |
| CustomTitlebar.tsx | `src/components/CustomTitlebar.tsx` |
| Settings.tsx | `src/components/Settings.tsx` |
| ThemeContext.tsx | `src/contexts/ThemeContext.tsx` |
| api.ts | `src/lib/api.ts` |

---

## 截图示例

待补充：实际界面截图

### 颜色板

```
主色 (深色模式):
- Primary: #3b82f6 (蓝色)
- Background: #1a1a1a (深灰)
- Card: #1a1a1a (深灰)
- Foreground: #fafafa (浅灰)

强调色:
- Destructive: #ef4444 (红色)
- Warning: #f59e0b (橙色)
- Success: #22c55e (绿色)
```

---

**文档版本**: v1.0
**最后更新**: 2025-02-20
**参考项目**: opcode v0.2.1

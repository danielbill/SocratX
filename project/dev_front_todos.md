# SocratX 前端开发计划

> **最后更新**: 2026 年 2 月 20 日
> **负责人**: 前端开发工程师
> **参考**: [前端美化方案](../docs/前端美化方案.md)

---

## 开发进度概览

| 阶段 | 模块 | 状态 | 进度 |
|------|------|------|------|
| P0 | 基础 UI 组件补全 | 🟢 **已完成** | 100% |
| P0 | 布局重构 (Titlebar + Sidebar) | 🟢 **已完成** | 100% |
| P1 | 标签页系统 | 🔴 待开始 | 0% |
| P2 | 高级样式效果 | 🔴 待开始 | 0% |
| P2 | 主题系统增强 | 🔴 待开始 | 0% |

---

## P0 - 基础 UI 组件补全

**目录**: `apps/desktop/src/components/ui/`

**状态**: 🟢 **已完成**

### 详细任务列表

**步骤 1: 创建模态框组件**
- [x] 创建 `dialog.tsx`
- [x] Dialog.Root - 根容器
- [x] Dialog.Trigger - 触发按钮
- [x] Dialog.Content - 内容区
- [x] Dialog.Header - 头部
- [x] Dialog.Title - 标题
- [x] Dialog.Description - 描述
- [x] Dialog.Footer - 底部
- [ ] 编写 `dialog.test.tsx`

**步骤 2: 创建下拉菜单组件**
- [x] 创建 `dropdown-menu.tsx`
- [x] DropdownMenu.Root
- [x] DropdownMenu.Trigger
- [x] DropdownMenu.Content
- [x] DropdownMenu.Item
- [x] DropdownMenu.Separator
- [ ] 编写 `dropdown-menu.test.tsx`

**步骤 3: 创建选择器组件**
- [x] 创建 `select.tsx`
- [x] Select.Root
- [x] Select.Trigger
- [x] Select.Content
- [x] Select.Item
- [ ] 编写 `select.test.tsx`

**步骤 4: 创建提示框组件**
- [x] 创建 `tooltip.tsx`
- [x] Tooltip.Root
- [x] Tooltip.Trigger
- [x] Tooltip.Content
- [x] TooltipSimple 简易封装
- [ ] 编写 `tooltip.test.tsx`

**步骤 5: 创建通知组件**
- [ ] 创建 `toast.tsx`
- [ ] Toast.Provider
- [ ] Toast.Root
- [ ] Toast.Title
- [ ] Toast.Description
- [ ] Toast.Action
- [ ] ToastViewport
- [ ] 编写 `toast.test.tsx`

**步骤 6: 创建其他组件**
- [x] 创建 `switch.tsx` - 开关组件
- [x] 创建 `tabs.tsx` - 标签页组件
- [x] 创建 `badge.tsx` - 徽章组件
- [x] 创建 `slider.tsx` - 滑块组件
- [x] 创建 `separator.tsx` - 分割线
- [x] 创建 `label.tsx` - 标签组件
- [ ] 编写对应测试文件

**步骤 7: 更新文档**
- [x] 更新 dev_front_todos.md 状态
- [ ] 更新组件使用文档

**预计时间**: 2 小时

---

## P0 - 布局重构 (RP-001 启动桌面)

**目录**: `apps/desktop/src/components/layout/`

**状态**: 🟢 **已完成** - 满足 RP-001 目标

### 详细任务列表

**步骤 1: 创建自定义标题栏**
- [x] 创建 `layout/Titlebar.tsx`
- [x] Header 点击可拖拽窗口 (data-tauri-drag-region)
- [x] 窗口控制按钮功能实现 (最小化/最大化/关闭)
- [x] 窗口控制按钮移到右侧
- [ ] 导航菜单 (Settings, Agents, Memory...)
- [ ] 深色模式切换按钮
- [x] 配置 Tauri 窗口 (decorations: false)
- [x] 配置 Tauri capabilities 权限
- [ ] 编写 `Titlebar.test.tsx`

**参考**: `D:\github\opcode\src\components\CustomTitlebar.tsx`

**步骤 2: 创建侧边栏**
- [ ] 创建 `layout/Sidebar.tsx`
- [ ] 会话列表展示
- [ ] 新建会话按钮
- [ ] 搜索框
- [ ] 收藏会话分组
- [ ] 侧边栏收起/展开切换
- [ ] 编写 `Sidebar.test.tsx`

**步骤 3: 创建主布局**
- [x] 创建 `layout/MainLayout.tsx`
- [x] 整合 Titlebar + Sidebar + MainContent
- [x] 响应式布局
- [ ] 拖拽调整侧边栏宽度 (可选)
- [ ] 编写 `MainLayout.test.tsx`

**步骤 4: 更新 App.tsx**
- [x] 移除原生 header
- [x] 使用 MainLayout 替换现有布局
- [ ] 配置路由 (如需要)

**步骤 5: 配置 Tauri 窗口**
- [x] 更新 `src-tauri/tauri.conf.json`
- [x] 设置 `decorations: false`
- [x] 设置窗口尺寸和最小尺寸
- [ ] 配置窗口透明度 (可选)

**步骤 6: 更新文档**
- [x] 更新 dev_front_todos.md 状态
- [ ] 记录布局组件使用方法

**预计时间**: 4 小时

---

## P1 - 标签页系统

**目录**: `apps/desktop/src/contexts/`, `apps/desktop/src/components/layout/`

**状态**: 🔴 待开始

### 详细任务列表

**步骤 1: 创建 TabContext**
- [ ] 创建 `contexts/TabContext.tsx`
- [ ] Tab 类型定义 (chat, agent, project...)
- [ ] 标签增删改查方法
- [ ] 活动标签状态
- [ ] 标签持久化到 localStorage
- [ ] 最大标签数限制 (20)
- [ ] 编写 `TabContext.test.tsx`

**参考**: `D:\github\opcode\src\contexts\TabContext.tsx`

**步骤 2: 创建 TabManager 组件**
- [ ] 创建 `layout/TabManager.tsx`
- [ ] 标签栏展示
- [ ] 标签项 (关闭按钮、状态指示、图标)
- [ ] Framer Motion 拖拽排序
- [ ] 标签切换动画
- [ ] 编写 `TabManager.test.tsx`

**参考**: `D:\github\opcode\src\components\TabManager.tsx`

**步骤 3: 快捷键支持**
- [ ] Ctrl+T - 新建标签
- [ ] Ctrl+W - 关闭当前标签
- [ ] Ctrl+Tab - 切换到下一个标签
- [ ] Ctrl+Shift+Tab - 切换到上一个标签
- [ ] Ctrl+数字 - 切换到指定标签

**步骤 4: 标签内容区**
- [ ] 创建 `layout/TabContent.tsx`
- [ ] 根据标签类型渲染不同内容
- [ ] 标签状态保持

**步骤 5: 集成到主布局**
- [ ] 将 TabManager 集成到 MainLayout
- [ ] 更新路由逻辑

**步骤 6: 更新文档**
- [ ] 更新 dev_front_todos.md 状态
- [ ] 记录快捷键列表

**预计时间**: 3 小时

---

## P2 - 高级样式效果

**目录**: `apps/desktop/src/styles.css`, `apps/desktop/src/components/ui/`

**状态**: 🔴 待开始

### 详细任务列表

**步骤 1: Shimmer Hover 效果**
- [ ] 添加 @keyframes shimmer 到 styles.css
- [ ] 创建 .shimmer-hover 工具类
- [ ] 应用到按钮和卡片组件
- [ ] 测试动画性能

**步骤 2: Trailing Border 效果**
- [ ] 添加 @keyframes rotate 到 styles.css
- [ ] 创建 .trailing-border 工具类
- [ ] 创建 conic-gradient 边框样式
- [ ] 应用到特殊卡片组件

**步骤 3: 扫描线动画**
- [ ] 创建扫描线 keyframes
- [ ] 创建 .scan-line 工具类
- [ ] 应用到加载状态

**步骤 4: 自定义滚动条**
- [ ] 添加 ::-webkit-scrollbar 样式
- [ ] 深色模式滚动条样式
- [ ] 浏览器兼容性测试

**步骤 5: 更新文档**
- [ ] 更新 dev_front_todos.md 状态
- [ ] 记录样式效果使用方法

**预计时间**: 2 小时

---

## P2 - 主题系统增强

**目录**: `apps/desktop/src/contexts/`

**状态**: 🔴 待开始

### 详细任务列表

**步骤 1: 升级 ThemeContext**
- [ ] 扩展 ThemeContext.tsx
- [ ] 添加预设主题 (dark, gray, light, custom)
- [ ] OKLCH 颜色空间支持
- [ ] 主题切换动画

**参考**: `D:\github\opcode\src\contexts\ThemeContext.tsx`

**步骤 2: 创建主题编辑器**
- [ ] 创建 `components/settings/ThemeEditor.tsx`
- [ ] 颜色拾色器
- [ ] 实时预览
- [ ] 保存/删除自定义主题

**步骤 3: 主题持久化**
- [ ] 保存到 localStorage
- [ ] 启动时加载保存的主题
- [ ] 主题导入/导出功能

**步骤 4: 更新样式系统**
- [ ] 迁移到 OKLCH 颜色空间
- [ ] 更新 styles.css
- [ ] 更新 Tailwind 配置

**步骤 5: 更新文档**
- [ ] 更新 dev_front_todos.md 状态
- [ ] 记录主题系统使用方法

**预计时间**: 3 小时

---

## 设置界面开发

**目录**: `apps/desktop/src/components/settings/`

**状态**: 🔴 待开始

### 详细任务列表

**步骤 1: 创建设置面板**
- [ ] 创建 `SettingsPanel.tsx` - 主设置面板
- [ ] 创建 `ProviderConfig.tsx` - LLM 提供商配置
- [ ] 创建 `ToolConfig.tsx` - 工具配置
- [ ] 创建 `ThemeSettings.tsx` - 主题设置
- [ ] 创建 `GeneralSettings.tsx` - 通用设置

**步骤 2: 设置数据持久化**
- [ ] 连接后端 API
- [ ] 保存/加载配置
- [ ] 配置验证

**步骤 3: 更新文档**
- [ ] 更新 dev_front_todos.md 状态

**预计时间**: 2 小时

---

## 里程碑

### 里程碑 1 - 基础布局完成 (本周)
- [x] P0 基础 UI 组件补全
- [x] P0 布局重构完成
- [x] 自定义标题栏显示
- [x] **RP-001 修复任务**
  - [x] Header 点击可拖拽窗口
  - [x] 窗口控制按钮功能实现 (最小化/最大化/关闭)
  - [x] 窗口控制按钮移到右侧
  - [x] 配置 Tauri capabilities 权限

### 里程碑 2 - 核心功能 (下周)
- [ ] P1 标签页系统
- [ ] 设置界面完成
- [ ] 多主题支持

### 里程碑 3 - 完善体验 (第三周)
- [ ] P2 高级样式效果
- [ ] P2 主题系统增强
- [ ] 细节优化

---

## 开发命令

```bash
# 开发模式
pnpm tauri:dev

# 测试
pnpm test
pnpm test:ui
pnpm test:coverage

# 构建
pnpm tauri:build
```

---

## 参考资源

**参考项目**:
- **opcode**: `D:\github\opcode`
  - `src/components/CustomTitlebar.tsx`
  - `src/components/TabManager.tsx`
  - `src/contexts/ThemeContext.tsx`
  - `src/contexts/TabContext.tsx`
  - `src/styles.css`

**组件库**:
- shadcn/ui: https://ui.shadcn.com/
- Radix UI: https://www.radix-ui.com/
- Framer Motion: https://www.framer.com/motion/

---

*最后更新：2026 年 2 月 20 日*

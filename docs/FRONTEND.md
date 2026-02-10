# MathVideo 前端开发指南

## 目录结构

```
frontend/
├── app/                        # Next.js App Router
│   ├── globals.css             # 全局样式 + CSS 变量主题
│   ├── layout.tsx              # 根布局 (ThemeProvider)
│   ├── page.tsx                # 首页 (生成表单 + 项目列表)
│   └── projects/
│       └── [slug]/
│           ├── page.tsx             # 服务端入口 (thin wrapper)
│           └── ProjectPageClient.tsx # 项目详情页 (客户端组件)
├── components/
│   ├── GenerateForm.tsx        # 生成表单 (拖拽上传 + 快速示例)
│   ├── LogViewer.tsx           # WebSocket 实时日志 (macOS 风格标题栏)
│   ├── VideoPlayer.tsx         # 视频播放器 (毛玻璃控制栏)
│   ├── StoryboardEditor.tsx    # 分镜编辑器
│   ├── ProjectList.tsx         # 项目列表 (骨架屏 + Dialog 删除)
│   ├── RefinerPanel.tsx        # 视觉优化面板
│   ├── SetupWizard.tsx         # Tauri 环境检测向导
│   ├── ThemeProvider.tsx       # next-themes 主题包装
│   ├── ThemeToggle.tsx         # 明暗切换按钮
│   └── ui/                     # shadcn/ui 基础组件
│       ├── badge.tsx           # 标签 (含 success/warning 变体)
│       ├── button.tsx          # 按钮 (CVA 多变体)
│       ├── card.tsx            # 卡片
│       ├── dialog.tsx          # 对话框 (替代 window.confirm)
│       ├── input.tsx           # 输入框
│       ├── progress.tsx        # 进度条
│       ├── scroll-area.tsx     # 滚动区域
│       ├── separator.tsx       # 分隔线
│       ├── skeleton.tsx        # 骨架屏
│       ├── switch.tsx          # 开关
│       ├── tabs.tsx            # 标签页
│       ├── textarea.tsx        # 多行输入
│       └── tooltip.tsx         # 提示框
├── lib/
│   ├── api.ts                  # API 客户端 (Tauri 感知)
│   ├── types.ts                # 统一类型定义
│   └── utils.ts                # cn() 工具函数
├── src-tauri/                  # Tauri v2 桌面端 (Rust)
│   ├── Cargo.toml
│   ├── tauri.conf.json         # 窗口 / CSP / Shell 作用域
│   ├── capabilities/
│   │   └── default.json        # 权限声明
│   ├── icons/                  # 全平台图标 (ICO/ICNS/PNG)
│   └── src/
│       ├── main.rs             # 入口 + 插件注册
│       ├── env_checker.rs      # 环境检测 (conda/ffmpeg)
│       └── backend_manager.rs  # FastAPI 进程管理
├── next.config.js              # 双模式配置 (Web / Tauri)
├── tailwind.config.js          # CSS 变量主题 + 动画
└── package.json
```

## 技术栈

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | Next.js | 16.1.5 | App Router, `'use client'` |
| 语言 | TypeScript | 5.3 | 严格模式 |
| 样式 | Tailwind CSS | 3.4.1 | CSS 变量语义化 Token |
| 组件库 | shadcn/ui | 手动集成 | CVA + Radix UI + cn() |
| 动画 | framer-motion | 12.x | 页面切换 + AnimatePresence |
| 主题 | next-themes | 0.4.x | class 策略, 支持系统跟随 |
| 图标 | lucide-react | 0.312 | 轻量 SVG 图标 |
| 桌面端 | Tauri v2 | 2.10 | Rust 后端 + WebView |
| 代码编辑 | Monaco Editor | 4.6 | 可选，脚本查看 |

## 设计系统

### 主题方案 — Notion × Apple 融合风

通过 CSS 变量实现明暗双主题，无需硬编码颜色值。

**浅色模式 (Notion 风)**
- 白色背景 + 柔和灰色边框
- 蓝紫色主色 (`hsl(236, 84%, 67%)`)
- 通透感卡片和导航

**深色模式 (Apple 风)**
- 纯黑背景 (`hsl(0, 0%, 7%)`)
- 蓝色主色 (`hsl(221, 83%, 69%)`)
- 毛玻璃效果 (backdrop-blur-xl)

### CSS 变量 Token

| Token | 用途 | 浅色值示例 | 深色值示例 |
|-------|------|-----------|-----------|
| `--background` | 页面背景 | #FFFFFF | #121212 |
| `--foreground` | 主文本色 | #1A1A1A | #FAFAFA |
| `--primary` | 主色调 | 蓝紫 | 蓝色 |
| `--card` | 卡片背景 | #FFFFFF | #1A1A1A |
| `--muted` | 次要背景 | #F5F5F5 | #262626 |
| `--accent` | 强调色 | 浅蓝 | 蓝灰 |
| `--destructive` | 危险/错误 | 红色 | 红色 |
| `--success` | 成功 | 绿色 | 绿色 |
| `--warning` | 警告 | 橙色 | 橙色 |

### 工具 CSS 类

```css
.glass         /* 毛玻璃效果 (backdrop-blur-xl) */
.glass-strong  /* 加强毛玻璃 (backdrop-blur-2xl) */
```

### 字体

| 用途 | 字体 |
|------|------|
| 英文 UI | Inter |
| 中文内容 | Noto Sans SC (思源黑体) |
| 代码/日志 | JetBrains Mono |

## 组件说明

### GenerateForm
- 拖拽 / 点击上传图片，实时预览缩略图
- Badge 快速示例 (点击自动填充)
- Switch 控制"自动渲染"开关
- 调用 `startGeneration()` 提交

### LogViewer
- macOS 风格标题栏 (红/黄/绿圆点)
- WebSocket 实时日志，按 emoji 前缀分级着色
- 自动滚动到底部，`animate-fade-in` 新条目动画

### ProjectList
- 骨架屏 (Skeleton) 加载状态
- Dialog 组件替代 `window.confirm` 删除确认
- 悬停显示操作按钮 (group-hover)
- Badge 标注渲染状态

### VideoPlayer
- Card 包装 + 毛玻璃控制栏
- 进度条悬停显示拖动点
- 悬停缩放播放/暂停按钮

### StoryboardEditor
- 拖动手柄图标 + Badge 章节编号
- Input 编辑标题，支持回车保存
- 未保存状态显示 Warning Badge

### RefinerPanel
- 三步工作流：视觉分析 → 应用建议 → 重新渲染
- 自定义建议输入框
- 分析结果橙色高亮卡片

### SetupWizard (Tauri 专属)
- 环境检测向导 (conda / mathvideo 环境 / ffmpeg)
- 进度条 + 逐项状态标识
- 未安装项显示安装指南链接
- 检测通过后自动跳转主界面

## API 层

### 端点总览

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/projects/` | 项目列表 |
| DELETE | `/api/projects/{slug}` | 删除项目 |
| GET | `/api/projects/{slug}/storyboard` | 获取分镜 |
| PUT | `/api/projects/{slug}/storyboard` | 更新分镜 |
| GET | `/api/projects/{slug}/videos` | 视频列表 |
| GET | `/api/projects/{slug}/scripts` | 脚本列表 |
| POST | `/api/generate/` | 启动生成任务 |
| WS | `/api/generate/ws/{task_id}` | 实时日志 |
| POST | `/api/refiner/{slug}/critique/{section_id}` | 视觉分析 |
| POST | `/api/refiner/{slug}/refine` | 代码优化 |
| POST | `/api/refiner/{slug}/render/{section_id}` | 重新渲染 |

### Tauri 感知

`lib/api.ts` 通过检测 `window.__TAURI__` 自动切换 URL 基址：

| 场景 | API | WebSocket | 静态文件 |
|------|-----|-----------|---------|
| Web (代理) | `/api` | `ws://localhost:8000` | `/static` |
| Tauri | `http://localhost:8000/api` | `ws://localhost:8000` | `http://localhost:8000/static` |

### 类型定义

所有类型集中在 `lib/types.ts`，包括：
- `Project`, `ProjectListResponse` — 项目数据
- `Section`, `Storyboard` — 分镜结构
- `VideoInfo`, `ScriptInfo` — 媒体资源
- `GenerateRequest`, `GenerateResponse` — 生成任务
- `LogMessage`, `GenerateStatus` — WebSocket 消息
- `CritiqueResponse`, `RefineRequest`, `RefineResponse` — 优化流程
- `TabType` — 页面标签类型

## 开发

### 启动

```bash
# Web 模式
cd frontend && npm run dev        # http://localhost:3000

# Tauri 桌面端开发 (需要 Rust)
cd frontend && npm run tauri:dev
```

### 代理配置

Web 模式下 `next.config.js` 的 `rewrites` 将 `/api/*` 和 `/static/*` 代理到 `:8000`。
Tauri 模式下 `rewrites` 不生效，前端直接请求 `http://localhost:8000`。

### CORS

后端 (`backend/main.py`) 允许以下 origin：
- `http://localhost:3000` — Next.js 开发
- `tauri://localhost` — Tauri macOS
- `https://tauri.localhost` — Tauri Windows/Linux

### 添加新 shadcn 组件

1. 在 `components/ui/` 下创建文件
2. 使用 `cn()` 合并 className
3. 使用 CVA 定义变体
4. 用 Radix UI 原语实现交互逻辑

### React Strict Mode

已关闭 (`reactStrictMode: false`)，避免 WebSocket 在开发模式下双重连接。

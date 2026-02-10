# MathVideo 部署指南

## 部署方式

| 方式 | 适用场景 | 说明 |
|------|---------|------|
| **Tauri 桌面端** | 终端用户 | 打包为 .msi (Windows) / .dmg (macOS)，内置进程管理 |
| **Web 开发** | 开发者 | Next.js + FastAPI 分离运行 |
| **CLI** | 脚本/批量 | `python -m mathvideo "主题" --render` |

---

## 1. 前置依赖

### 所有模式通用

| 依赖 | 版本 | 安装方式 | 用途 |
|------|------|---------|------|
| Conda | Miniconda 或 Anaconda | [miniconda.io](https://docs.conda.io/en/latest/miniconda.html) | Python 环境管理 |
| Python | 3.10+ | `conda create -n mathvideo python=3.10` | 核心运行时 |
| ffmpeg | 6+ | `conda install ffmpeg` 或系统安装 | Manim 视频合成 |
| pdflatex | 任意 | 可选，MiKTeX / TeX Live | LaTeX 公式渲染（有自动回退） |

### Tauri 桌面端额外依赖

| 依赖 | 版本 | 安装方式 |
|------|------|---------|
| Rust | 1.80+ | [rustup.rs](https://rustup.rs/) 或 `winget install Rustlang.Rust.MSVC` |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| Visual Studio Build Tools | 2022 | Windows 专需，Rust 编译链接器 |
| Xcode Command Line Tools | 最新 | macOS 专需，`xcode-select --install` |

### Python 环境设置

```bash
# 创建 conda 环境
conda create -n mathvideo python=3.10 -y
conda activate mathvideo

# 安装 Python 依赖
pip install -r requirements.txt

# 验证
python -c "import manim; print(manim.__version__)"
ffmpeg -version
```

### 环境变量 (.env)

在项目根目录创建 `.env` 文件：

```bash
# 必填 — Claude API
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL_NAME=claude-opus-4-5-20251101      # 默认值

# 可选 — Gemini 视觉反馈
GEMINI_API_KEY=AIza...
GEMINI_VISION_MODEL_NAME=gemini-3-pro-preview

# 可选 — 图标下载
ICONFINDER_API_KEY=...
```

---

## 2. Web 开发模式

### 启动

```bash
# 终端 1 — 后端 (端口 8000)
conda activate mathvideo
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 终端 2 — 前端 (端口 3000)
cd frontend && npm install && npm run dev
```

或使用启动脚本：

```bash
# Windows
.\start-dev.ps1

# macOS / Linux
./start-dev.sh
```

### 访问

- 前端界面: http://localhost:3000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 工作原理

```
浏览器 (:3000) → Next.js rewrites → FastAPI (:8000)
                   /api/*  ──────────→ /api/*
                   /static/* ────────→ /static/*
```

WebSocket 日志连接直连后端 `ws://localhost:8000/api/generate/ws/{task_id}`。

---

## 3. Tauri 桌面端

### 架构

```
┌─────────────────────────────────────────┐
│              Tauri Shell (Rust)          │
│                                         │
│  ┌────────────┐     ┌───────────────┐   │
│  │  WebView    │────→│ Tauri Commands│   │
│  │  (Next.js)  │     │               │   │
│  └────────────┘     │ env_checker   │   │
│       │              │ backend_mgr   │   │
│       │              └───────┬───────┘   │
│       │                      │           │
│       ▼                      ▼           │
│  localhost:3000      conda subprocess    │
│  (standalone)        FastAPI :8000       │
└─────────────────────────────────────────┘
```

| 模块 | 文件 | 功能 |
|------|------|------|
| env_checker | `src-tauri/src/env_checker.rs` | 检测 conda / mathvideo 环境 / ffmpeg |
| backend_manager | `src-tauri/src/backend_manager.rs` | 启动/停止/检查 FastAPI 进程 |
| SetupWizard | `components/SetupWizard.tsx` | 首次启动环境检测 UI |

### 开发

```bash
cd frontend
npm run tauri:dev
```

此命令同时启动 Next.js 开发服务器和 Tauri WebView。Rust 代码修改后自动热重载。

### 构建安装包

```bash
cd frontend
npm run tauri:build
```

产出位置：
- **Windows**: `src-tauri/target/release/bundle/msi/MathVideo_*.msi`
- **macOS**: `src-tauri/target/release/bundle/dmg/MathVideo_*.dmg`

### Shell 作用域 (安全)

Tauri 的 Shell 插件通过 `tauri.conf.json` 的 `scope` 限制可执行命令：

| 作用域 ID | 命令 | 用途 |
|-----------|------|------|
| `conda-run` | `conda run -n mathvideo ...` | 运行 Python 命令 |
| `python-module` | `python -m ...` | 运行 Python 模块 |
| `conda-check` | `conda info --json` | 检测 conda 环境 |
| `ffmpeg-check` | `ffmpeg -version` | 检测 ffmpeg |

### CSP 策略

```
default-src 'self';
connect-src 'self' http://localhost:8000 ws://localhost:8000;
img-src 'self' http://localhost:8000 data:;
media-src 'self' http://localhost:8000;
```

---

## 4. CLI 模式

```bash
conda activate mathvideo

# 基本用法
python -m mathvideo "勾股定理" --render

# 带图片输入
python -m mathvideo "题目描述" --image ./img.png --render

# 指定输出目录
python -m mathvideo "主题" --render --output ./custom_output/
```

输出目录结构：

```
output/<slug>/
├── storyboard.json          # 分镜数据
├── inputs/                  # 用户上传的图片副本
├── assets/                  # SVG 图标
├── scripts/                 # section_1.py, section_2.py ...
└── media/videos/            # Manim 渲染的 MP4
```

---

## 5. CI/CD — GitHub Actions

### 工作流文件

`.github/workflows/build-tauri.yml`

### 触发条件

- Push 到 `main` 分支
- Pull Request 到 `main` 分支
- 手动触发 (`workflow_dispatch`)

### 构建矩阵

| 平台 | Runner | 目标架构 | 产出格式 |
|------|--------|---------|---------|
| Windows | `windows-latest` | x86_64 | .msi |
| macOS Intel | `macos-13` | x86_64 | .dmg |
| macOS Apple Silicon | `macos-latest` | aarch64 | .dmg |

### 流程

1. Checkout 代码
2. 安装 Rust (stable) + 缓存
3. 安装 Node.js 20 + npm 缓存
4. `npm install` 前端依赖
5. `npx tauri build` 构建产出
6. 上传 Artifact (msi / dmg)

### 手动运行

GitHub → Actions → Build Tauri App → Run workflow

---

## 6. 故障排查

### 前端无法连接后端

1. 确认后端运行在 `:8000`：`curl http://localhost:8000/health`
2. Web 模式检查 `next.config.js` 的 rewrites 是否正确
3. Tauri 模式检查 CSP 是否包含 `http://localhost:8000`

### WebSocket 断连

- WebSocket 直连后端，不经过 Next.js 代理
- 后端有 30 秒心跳 (ping/pong)，网络不稳定时可能断连
- 前端 LogViewer 会自动处理断连后的重连

### Manim 渲染失败

1. 检查 ffmpeg：`ffmpeg -version`
2. 检查 Python 环境：`conda activate mathvideo && python -c "import manim"`
3. 手动测试单个脚本：`manim -ql output/<slug>/scripts/section_1.py Section1Scene`
4. 确保环境变量 `PYTHONPATH` 包含项目根目录

### Tauri 构建失败

- **Windows**: 确认已安装 Visual Studio Build Tools 2022 (C++ 工作负载)
- **macOS**: `xcode-select --install`
- **Rust 版本**: 需要 1.80+，`rustup update stable`
- **依赖缓存**: 清除后重试 `cd src-tauri && cargo clean`

### 视频无法播放

1. 文件是否存在：`ls output/<slug>/media/videos/`
2. 浏览器控制台是否有 CORS 错误
3. 后端静态文件挂载是否正确 (`/static/` → `output/`)

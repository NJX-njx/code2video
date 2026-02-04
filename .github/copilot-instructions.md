# MathVideo AI 编码助手指南

本指南帮助 AI 助手高效理解和维护 `mathvideo` 项目——一个利用 LLM (Claude Opus 4.5) 和 Manim 自动生成数学讲解视频的端到端系统。

## 1. 系统架构

### 1.1 核心 Pipeline
```
用户输入 → Planner → AssetManager → Coder → Manim渲染 → [Critic视觉分析] → [Refiner优化] → 输出视频
```

| Agent | 文件 | 职责 |
|-------|------|------|
| Planner | `mathvideo/agents/planner.py` | 生成 `storyboard.json` (3-5章节) |
| AssetManager | `mathvideo/agents/asset_manager.py` | 下载/生成 SVG 图标资源 |
| Coder | `mathvideo/agents/coder.py` | 生成 Manim Python 代码 |
| Critic | `mathvideo/agents/critic.py` | 视觉模型 (Gemini 3 Pro) 分析视频帧 |
| Refiner | `mathvideo/agents/coder.py:refine_code` | 根据视觉反馈优化代码 |

### 1.2 双入口架构
- **CLI**: `python -m mathvideo "主题" --render` (核心逻辑在 `mathvideo/cli.py`)
- **Web**: FastAPI 后端 (`backend/`) + Next.js 前端 (`frontend/`)

### 1.3 输出目录结构 (严格遵循)
```
output/<topic_slug>/
├── storyboard.json      # 分镜剧本
├── assets/              # SVG 图标资源
├── scripts/             # section_1.py, section_2.py...
└── media/videos/        # Manim 渲染输出
```

## 2. 开发规范

### 2.1 语言与注释
- **强制中文**: 所有代码注释、文档字符串、视频文本必须使用中文
- **注释风格**: 解释"为什么"，保持详细

### 2.2 Manim 代码生成 (CRITICAL)
```python
# 必须继承 TeachingScene
from mathvideo.manim_base import TeachingScene, LIGHT_BLUE, LIGHT_YELLOW

class Section1Scene(TeachingScene):
    def construct(self):
        # 首行必须调用 setup_layout
        self.setup_layout(title="标题", lecture_notes=["笔记1", "笔记2"])
        
        # 使用网格定位 (A-J行, 1-10列), 禁止 .to_edge()/.to_corner()
        self.place_at_grid(circle, "E5", scale_factor=0.8)
        self.place_in_area(triangle, "B2", "H8", scale_factor=0.9)
```

- **颜色**: 仅使用 `manim_base.py` 定义的别名 (`LIGHT_BLUE`, `LIGHT_YELLOW`, `CYAN`, `NAVY`...)
- **LaTeX 回退**: 系统自动处理，直接使用 `MathTex`，无需手动检测

### 2.3 LLM Prompt 模板
所有 LLM 调用的 prompt 集中在 `mathvideo/agents/prompts.py`，修改生成行为时优先编辑此文件。

## 3. 常用命令

```bash
# CLI 完整生成
conda activate mathvideo
python -m mathvideo "勾股定理" --render
python -m mathvideo "题目描述" --image ./img.png --render

# 手动调试单个脚本 (必须在项目根目录)
manim -qm output/<slug>/scripts/section_1.py Section1Scene

# 启动 Web 开发环境 (需要两个终端)
# 终端1 - 后端 (端口 8000)
conda run -n mathvideo python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
# 终端2 - 前端 (端口 3000)
cd frontend && npm run dev

# API 测试
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI
```

## 4. Web 架构要点

### 4.1 实时日志 WebSocket
- 端点: `ws://localhost:8000/api/generate/ws/{task_id}`
- 后端 `broadcast_log()` 会等待 WebSocket 连接建立后再发送日志 (解决竞态条件)

### 4.2 静态文件
- 后端挂载 `output/` 为 `/static/`
- 视频访问: `/static/{slug}/media/videos/section_1/480p15/Section1Scene.mp4`

### 4.3 前端代理
`frontend/next.config.js` 将 `/api/*` 代理到后端 8000 端口

## 5. 关键文件索引

| 文件 | 职责 |
|------|------|
| `mathvideo/manim_base.py` | **核心**: TeachingScene、Grid 系统、颜色别名、LaTeX 回退 |
| `mathvideo/agents/prompts.py` | 所有 LLM prompt 模板 |
| `mathvideo/config.py` | API Keys、模型配置 (读取 `.env`) |
| `backend/api/generate.py` | 生成任务 API + WebSocket 广播 |
| `frontend/components/LogViewer.tsx` | WebSocket 日志组件 |

## 6. 环境配置

```bash
# .env 必填项
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL_NAME=claude-opus-4-5-20251101
GEMINI_API_KEY=AIza...
GEMINI_VISION_MODEL_NAME=gemini-3-pro-preview
```

Conda 环境: `mathvideo` (Python 3.10+, manim, ffmpeg, langchain)

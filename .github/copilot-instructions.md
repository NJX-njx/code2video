# MathVideo AI 编码助手指南

利用 Claude Opus 4.5 + Manim 自动生成数学讲解视频的端到端系统。

## 1. 架构概览

### Pipeline
```
用户输入 → Router → Planner(按类型) → AssetManager → Coder(按模式) → Manim渲染 → [Critic] → [Refiner] → 视频
```

| Agent | 文件 | 模型 | 职责 |
|-------|------|------|------|
| **Router** | `mathvideo/agents/router.py` | Claude (temp=0.1) | 分类任务类型（knowledge/geometry/problem/proof） |
| Planner | `mathvideo/agents/planner.py` | Claude (temp=0.7) | 按任务类型选择 Prompt，生成 `storyboard.json` |
| AssetManager | `mathvideo/agents/asset_manager.py` | Claude (temp=0.3) | 分析需要的图标关键词，下载/生成 SVG |
| Coder | `mathvideo/agents/coder.py` | Claude (temp=0.5) | 按 Section 模式生成 Manim 代码；`fix_code`(temp=0.2) 修复渲染错误 |
| Critic | `mathvideo/agents/critic.py` | Gemini 3 Pro → Claude 回退 | FFmpeg 提取帧 → 视觉模型分析布局/几何 |
| Refiner | `mathvideo/agents/coder.py:refine_code` | Claude (temp=0.3) | 根据 Critic 反馈调整视觉参数 |

### 任务类型与 Section 模式
| 任务类型 | Section 模式 | Planner Prompt | Coder Prompt | 说明 |
|----------|-------------|----------------|--------------|------|
| `knowledge` | 独立模式 | `PLANNER_PROMPT` | `CODER_PROMPT` | 知识点讲解，各 Section 互不依赖 |
| `geometry` | **递进模式** | `PLANNER_GEOMETRY_PROMPT` | `CODER_SEQUENTIAL_PROMPT` | 几何题解答，Section 间传递构图上下文 |
| `problem` | 独立模式 | `PLANNER_PROMPT` | `CODER_PROMPT` | 应用题（非几何），各步骤独立 |
| `proof` | **递进模式** | `PLANNER_PROOF_PROMPT` | `CODER_SEQUENTIAL_PROMPT` | 证明题，逐步推导连贯 |

**递进模式关键**: Coder 接收上一 Section 的完整代码作为上下文。Planner 为每个 Section 标注 `inherited_objects`（继承对象）和 `new_objects`（新增对象），Coder 据此在新 Section 中先用 `self.add()` 静默重建继承对象，再动画展示新对象。

### Skill 注入系统
| 组件 | 文件 | 说明 |
|------|------|------|
| SkillManager | `mathvideo/agents/skill_manager.py` | 按任务类型加载 `.md`/`.yaml` 技能文件 |
| 技能目录 | `mathvideo/skills/{common,geometry,knowledge,problem,proof}/` | 分类型存储最佳实践和代码模式 |

**工作原理**: `load_skills(task_type)` 加载 `common/` + `{task_type}/` 目录下所有技能文件，拼接为文本注入到 Planner 和 Coder 的 Prompt 末尾。新增技能只需在对应目录下添加 `.md` 文件即可。

### 双入口
- **CLI**: `python -m mathvideo "主题" --render`（入口 `mathvideo/cli.py`）
- **Web**: FastAPI 后端 `backend/`(:8000) + Next.js 前端 `frontend/`(:3000)

### 输出目录结构（严格遵循）
```
output/<topic_slug>/
├── storyboard.json      # Planner 输出
├── inputs/              # 用户上传的图片副本
├── assets/              # SVG 图标（AssetManager）
├── scripts/             # section_1.py, section_2.py...（Coder 输出）
└── media/videos/        # Manim 渲染的 MP4
```

## 2. 关键代码约定

### 强制中文
所有代码注释、docstring、视频文本、LLM prompt 均使用中文。注释要详细解释"为什么"。

### LLM 调用模式
- **统一入口**: `mathvideo/llm_client.py` 的 `get_llm(temperature)` 返回 `ClaudeDirectChat`（自封装的 LangChain `BaseChatModel`，直接用 `requests` 调 Anthropic API，绕过 SDK 版本问题）
- **链式调用**: 所有 Agent 使用 `ChatPromptTemplate | llm | OutputParser` 的 LangChain 管道模式
- **Prompt 集中管理**: 所有模板在 `mathvideo/agents/prompts.py`，修改 LLM 行为时**优先编辑此文件**
  - `ROUTER_PROMPT` — 任务分类（4 种类型）
  - `PLANNER_PROMPT` — 通用知识点/应用题 storyboard
  - `PLANNER_GEOMETRY_PROMPT` — 几何题递进 storyboard（含 `inherited_objects`/`new_objects`）
  - `PLANNER_PROOF_PROMPT` — 证明题逻辑链 storyboard
  - `CODER_PROMPT` — 独立模式代码生成
  - `CODER_SEQUENTIAL_PROMPT` — 递进模式代码生成（接收 `previous_code`）
  - `FIX_CODE_PROMPT` / `REFINE_CODE_PROMPT` / `ASSET_PROMPT` / `CRITIC_PROMPT` — 辅助 Prompt
- **技能注入**: `mathvideo/agents/skill_manager.py` 的 `load_skills(task_type)` 按类型加载 `mathvideo/skills/` 下的技能文件，追加到 Prompt 末尾
- **视觉模型**: `mathvideo/gemini_native.py` 封装 Gemini 原生 API（非 OpenAI 兼容），Critic 使用 Gemini 优先、Claude 回退的双模型策略

### Manim 代码生成规则（CRITICAL）
生成的脚本必须遵循以下模式，否则渲染会失败或布局错乱：

```python
# 必须先导入 TeachingScene（触发 LaTeX 回退补丁和猴子补丁）
from mathvideo.manim_base import TeachingScene
from manim import *

class Section1Scene(TeachingScene):
    def construct(self):
        lines = ["笔记1", "笔记2"]
        self.setup_layout("标题", lines)    # 首行必须调用
        
        self.highlight_line(0)              # 高亮讲义笔记，同步动画进度
        circle = Circle(color=BLUE)
        self.place_in_area(circle, 'B2', 'H8', scale_factor=0.9)  # 网格定位
        self.play(Create(circle))
        self.wait(1)
```

**核心规则**:
- 继承 `TeachingScene`，`construct()` 首行调用 `self.setup_layout(title, lecture_notes)`
- **网格定位系统**: 右侧 10×10 网格 (行 A-J, 列 1-10)，A1=左上角，J10=右下角
  - `self.place_at_grid(obj, 'E5')` — 小对象单点定位
  - `self.place_in_area(obj, 'A1', 'C3')` — 大对象/组合区域定位（自动缩放）
  - `self.fit_to_screen(obj)` — 安全兜底
  - **禁止** `.to_edge()`, `.to_corner()` 或绝对坐标
- **标签定位**: 先 `place_in_area` 放几何体，再用 `self.add_side_label(polygon, side_idx, text)` / `self.add_vertex_label()` / `self.add_right_angle_mark()` 添加标签。**禁止**先 `next_to` 再 `place_at_grid`（会覆盖位置）
- **类名约定**: `section_data['id']` 如 `"section_1"` → 类名 `Section1Scene`（`coder.py` 自动重命名）
- **颜色**: 仅用 `manim_base.py` 预定义的别名 (`LIGHT_BLUE`, `LIGHT_YELLOW`, `CYAN`, `NAVY`, `BROWN`, `VIOLET` 等)
- **LaTeX 回退**: `manim_base.py` 检测 `pdflatex` 可用性，不可用时猴子补丁 `manim.MathTex` 为 `Text` 子类。直接使用 `MathTex`，无需手动处理
- **LLM 兼容性**: `TeachingScene` 提供多个别名方法（`grid_to_coords`, `grid_anchor`, `get_grid_position`）和 `VGroup.arrange_in_circle` 猴子补丁，提高 LLM 生成代码的成功率

### 错误修复循环
渲染失败时 `cli.py` 自动调用 `fix_code(code, error)` 重试最多 3 次。渲染成功后若启用 `USE_VISUAL_FEEDBACK`，进入 Critic→Refiner 循环（仅重试 1 次）。

## 3. 开发命令

```bash
# CLI 生成（必须在项目根目录）
conda activate mathvideo
python -m mathvideo "勾股定理" --render
python -m mathvideo "题目描述" --image ./img.png --render

# 手动调试单个 Manim 脚本（PYTHONPATH 必须包含项目根目录）
manim -ql output/<slug>/scripts/section_1.py Section1Scene

# Web 开发（两个终端）
conda run -n mathvideo python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
cd frontend && npm run dev    # http://localhost:3000

# API
curl http://localhost:8000/health
curl http://localhost:8000/docs   # Swagger UI
```

## 4. Web 架构

### 后端路由（FastAPI）
| 路由 | 文件 | 说明 |
|------|------|------|
| `POST /api/generate/` | `backend/api/generate.py` | 启动生成任务，返回 `task_id`=slug |
| `WS /api/generate/ws/{task_id}` | 同上 | 实时日志推送（心跳 30s，支持 ping/pong） |
| `GET/DELETE /api/projects/` | `backend/api/projects.py` | 项目 CRUD |
| `POST /api/refiner/{slug}/critique` | `backend/api/refiner.py` | 手动触发视觉分析 |
| `/static/{path}` | 静态文件 | 挂载 `output/` 提供视频访问 |

### 关键实现细节
- **WebSocket 竞态**: `run_generation()` 先等待最多 5 秒让 WebSocket 连接建立，再开始广播日志
- **子进程**: Web 端通过 `asyncio.create_subprocess_shell` 执行 `conda run -n mathvideo python -u -m mathvideo ...`，实时读取 stdout 按 emoji 判断日志级别
- **前端代理**: `frontend/next.config.js` 的 `rewrites` 将 `/api/*` 和 `/static/*` 代理到 `:8000`
- **React Strict Mode 关闭**: 避免 WebSocket 在开发模式下双重挂载

### 前端组件
| 组件 | 职责 |
|------|------|
| `GenerateForm` | 输入表单（文本+图片上传） |
| `LogViewer` | WebSocket 实时日志 |
| `VideoPlayer` | 视频播放 |
| `StoryboardEditor` | 分镜编辑 |
| `RefinerPanel` | 手动触发优化 |
| `ProjectList` | 项目列表 |

## 5. 关键文件索引

| 文件 | 说明 |
|------|------|
| `mathvideo/manim_base.py` | **核心 937 行**: TeachingScene、Grid 定位、颜色别名、LaTeX 回退、LLM 猴子补丁 |
| `mathvideo/agents/prompts.py` | 所有 LLM prompt 模板（Planner/Coder/Fix/Asset/Critic/Refine） |
| `mathvideo/agents/router.py` | Router Agent — 任务类型分类（knowledge/geometry/problem/proof） |
| `mathvideo/agents/skill_manager.py` | Skill 加载器 — 按类型注入技能到 Prompt |
| `mathvideo/skills/` | 技能文件目录（common/, geometry/, knowledge/, problem/, proof/） |
| `mathvideo/llm_client.py` | Claude API 封装（`ClaudeDirectChat` 继承 LangChain `BaseChatModel`） |
| `mathvideo/gemini_native.py` | Gemini 原生 API 封装（`generateContent` 端点） |
| `mathvideo/config.py` | 所有配置项（从 `.env` 读取），含功能开关 `USE_VISUAL_FEEDBACK` / `USE_ASSETS` |
| `mathvideo/utils.py` | `make_slug()` — 生成可控长度的项目 slug（截断+sha1 哈希） |

## 6. 环境与配置

```bash
# Conda 环境: mathvideo (Python 3.10+)
# 核心依赖: manim>=0.18, langchain, requests, json5, python-dotenv, opencv-python
# 系统依赖: ffmpeg (Manim 必需), pdflatex (可选，有回退)

# .env 必填
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL_NAME=claude-opus-4-5-20251101    # 默认值

# .env 可选
GEMINI_API_KEY=AIza...                         # 启用视觉反馈
GEMINI_VISION_MODEL_NAME=gemini-3-pro-preview  # 默认值
ICONFINDER_API_KEY=...                         # 启用真实图标下载
```

## 7. 注意事项

- **Slug 生成**: `make_slug(text, extra=image_hint)` 会截断长文本并追加 sha1[:8]，同一输入始终生成相同 slug
- **JSON 容错**: `planner.py` 使用 `json5.loads` + 引号修复 + LLM 二次修复的三级回退解析 storyboard
- **Manim 渲染质量**: CLI 使用 `-ql`（480p15），视频路径为 `media/videos/{script_name}/480p15/{ClassName}.mp4`
- **导入顺序**: 生成的脚本必须先 `from mathvideo.manim_base import TeachingScene` 再 `from manim import *`，确保猴子补丁生效
- **项目尚未实现**: `backend/api/generate.py` 的 `regenerate_section` 端点标记为 TODO

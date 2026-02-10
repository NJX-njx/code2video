# MathVideo 后端架构文档

> 最后更新: 2026-02-10

## 1. 系统总览

MathVideo 是一个利用 LLM (Claude Opus 4.5) + Manim 自动生成数学讲解视频的端到端系统。系统包含两个入口：CLI 命令行和 Web API，共享核心的 Agent Pipeline。

### 1.1 总体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户入口                                     │
│                                                                     │
│  CLI (python -m mathvideo)          Web (FastAPI :8000 + Next.js)   │
│      mathvideo/cli.py                   backend/main.py             │
└──────────┬──────────────────────────────────┬───────────────────────┘
           │                                  │
           ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     核心 Agent Pipeline                              │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │  Router  │──▶│ Planner  │──▶│  Asset   │──▶│  Coder   │        │
│  │          │   │          │   │ Manager  │   │          │        │
│  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘        │
│                                                     │              │
│                             ┌────────────────────────┤              │
│                             │                        ▼              │
│                       ┌─────┴─────┐          ┌──────────┐          │
│                       │  Refiner  │◀─────────│  Critic  │          │
│                       └───────────┘          └──────────┘          │
│                                                                     │
│  支撑层:  SkillManager │ LLMClient │ GeminiNative │ TeachingScene  │
└─────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      输出 (output/<slug>/)                          │
│                                                                     │
│  storyboard.json │ scripts/*.py │ media/videos/ │ final_video.mp4  │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Pipeline 执行流程

```
用户输入(文本+图片) → Router(分类任务) → Planner(生成分镜) → 项目重命名
     → AssetManager(图标资产) → Coder(逐节生成代码) → Manim渲染
     → [Fix 重试最多3次] → [Critic 视觉分析] → [Refiner 优化]
     → 视频合并 → final_video.mp4
```

## 2. 目录结构

```
code2video/
├── mathvideo/                    # 核心包
│   ├── __init__.py               # 包入口，导出公共 API
│   ├── __main__.py               # `python -m mathvideo` 入口
│   ├── cli.py                    # CLI 主流程（Pipeline 编排）
│   ├── config.py                 # 所有配置项（从 .env 读取）
│   ├── llm_client.py             # Claude API 封装（LangChain 兼容）
│   ├── gemini_native.py          # Gemini 原生 API 封装（视觉分析用）
│   ├── manim_base.py             # TeachingScene 基类（937行，网格/颜色/LaTeX回退）
│   ├── utils.py                  # 工具函数（slug生成/项目目录重命名）
│   ├── agents/                   # Agent 模块
│   │   ├── __init__.py           # 导出所有 Agent 公共接口
│   │   ├── router.py             # Router Agent — 任务类型分类
│   │   ├── planner.py            # Planner Agent — 分镜脚本生成
│   │   ├── coder.py              # Coder Agent — Manim 代码生成/修复/优化
│   │   ├── asset_manager.py      # AssetManager — 图标资产分析和下载
│   │   ├── critic.py             # VisualCritic — 视频帧视觉分析
│   │   ├── prompts.py            # 所有 LLM Prompt 模板（集中管理）
│   │   └── skill_manager.py      # Skill 加载器 — 按类型注入技能到 Prompt
│   └── skills/                   # 技能经验库（按类型分目录）
│       ├── common/               # 通用技能（所有类型共用）
│       │   ├── grid_positioning.md
│       │   ├── label_placement.md
│       │   └── visual_consistency.md
│       ├── geometry/             # 几何构造专用技能
│       │   ├── sequential_sections.md
│       │   ├── triangle_construction.md
│       │   ├── angle_bisector_parallel.md
│       │   ├── symmetry_construction.md
│       │   └── midpoint_extension.md
│       ├── knowledge/            # 知识点讲解专用（待扩充）
│       │   └── .gitkeep
│       ├── problem/              # 应用/计算题专用（待扩充）
│       │   └── .gitkeep
│       └── proof/                # 证明推导专用
│           ├── .gitkeep
│           └── proof_animation.md
├── backend/                      # FastAPI Web 后端
│   ├── main.py                   # FastAPI 应用入口
│   ├── requirements.txt          # 后端专用依赖
│   └── api/                      # API 路由模块
│       ├── __init__.py
│       ├── generate.py           # 生成任务 API + WebSocket 实时日志
│       ├── projects.py           # 项目 CRUD API
│       └── refiner.py            # 视觉优化 API
├── frontend/                     # Next.js 前端（详见 FRONTEND.md）
├── output/                       # 项目输出目录（运行时生成）
├── test_input/                   # 测试输入（示例题目和图片）
├── tools/                        # 开发工具和测试脚本
├── docs/                         # 文档目录
├── main.py                       # 兼容入口（调用 mathvideo.cli.main）
├── pyproject.toml                # Python 包配置
├── requirements.txt              # 完整依赖列表
└── .env                          # 环境变量配置（API Key 等）
```

## 3. Agent 详解

### 3.1 Router Agent

**文件**: `mathvideo/agents/router.py`
**模型**: Claude (temperature=0.1, max_tokens=1024)
**职责**: 根据用户输入（文本 + 图片描述）判断任务类型

| 任务类型 | 说明 | Section 模式 | 特征关键词 |
|----------|------|-------------|-----------|
| `knowledge` | 知识点讲解 | 独立模式 | "勾股定理"、"二次方程" |
| `geometry` | 几何构造/作图题 | **递进模式** | △、∠、"对称点"、"如图" |
| `problem` | 应用/计算题 | 独立模式 | "求"、"计算"、具体数值 |
| `proof` | 证明推导 | **递进模式** | "证明"、"推导"、"说明...成立" |

**容错设计**: `_parse_task_type()` 支持 4 级回退——直接匹配 → JSON 解析 → 文本搜索 → 中文关键词映射。最终回退到 `knowledge`。

**Section 模式**:
- **独立模式 (independent)**: 各 Section 互不依赖，Coder 使用 `CODER_PROMPT`
- **递进模式 (sequential)**: Coder 接收上一 Section 的完整代码作为上下文，使用 `CODER_SEQUENTIAL_PROMPT`。Planner 为每个 Section 标注 `inherited_objects` 和 `new_objects`

### 3.2 Planner Agent

**文件**: `mathvideo/agents/planner.py`
**模型**: Claude (temperature=0.7, max_tokens=16384)
**职责**: 将用户输入转换为结构化的分镜脚本 `storyboard.json`

**按任务类型选择 Prompt**:
| 任务类型 | Prompt 模板 | 特殊字段 |
|----------|------------|---------|
| `knowledge` / `problem` | `PLANNER_PROMPT` | — |
| `geometry` | `PLANNER_GEOMETRY_PROMPT` | `inherited_objects`, `new_objects` |
| `proof` | `PLANNER_PROOF_PROMPT` | `inherited_objects`, `new_objects` |

**图片理解**: 通过 `_describe_images()` 调用 Gemini 或 Claude 视觉模型，将图片内容翻译为文字描述，注入到 Planner Prompt 中。

**JSON 容错**: 三级回退解析——`json.loads` → `json5.loads`（容忍尾逗号等）→ 引号修复 → LLM 二次修复。

**Skill 注入**: 通过 `load_skills(task_type)` 将对应类型的经验技巧追加到 Prompt 末尾。

### 3.3 Coder Agent

**文件**: `mathvideo/agents/coder.py`
**模型**: Claude (temperature=0.5, max_tokens=16384)
**职责**: 为每个 Section 生成 Manim Python 代码

提供三个核心函数:

| 函数 | 温度 | 用途 |
|------|------|------|
| `generate_code()` | 0.5 | 生成初始代码（独立/递进模式） |
| `fix_code()` | 0.2 | 根据渲染错误修复代码 |
| `refine_code()` | 0.3 | 根据视觉反馈优化代码 |

**类名约定**: Section ID `"section_1"` → 类名 `Section1Scene`（自动重命名）。

**递进模式核心**: 当 `task_type ∈ {geometry, proof}` 且存在前序代码时，使用 `CODER_SEQUENTIAL_PROMPT`，传入 `previous_code`、`inherited_objects`、`new_objects`。Coder 在新 Section 中先 `self.add()` 静默重建继承对象，再动画展示新对象。

### 3.4 AssetManager

**文件**: `mathvideo/agents/asset_manager.py`
**模型**: Claude (temperature=0.3)
**职责**: 分析分镜中需要的图标关键词，下载/生成 SVG 资产

- 使用 LLM 分析 storyboard 识别所需图标
- 优先从 IconFinder API 下载真实图标
- 无 API Key 时生成 SVG 占位符
- 资产路径注入到 storyboard 的 `available_assets` 字段

### 3.5 VisualCritic

**文件**: `mathvideo/agents/critic.py`
**模型**: Gemini 3 Pro（优先） → Claude（回退）
**职责**: 对渲染成功的视频进行视觉分析

**工作流程**:
1. FFmpeg 提取关键帧（每秒1帧，缩放到 320px 宽度节省 token）
2. 选取最多 4 帧代表帧（首、1/3、2/3、尾）
3. Base64 编码后发送至视觉模型
4. 解析 JSON 反馈（`has_issues` / `issues` / `suggestion`）

**双模型策略**: Gemini 调用失败时自动回退到 Claude；Gemini 返回结果解析失败时也会尝试 Claude。

> **注意**: 帧提取依赖系统级 ffmpeg CLI。当前 Windows 环境未安装 ffmpeg，Visual Critic 会 soft fail（不影响主流程）。

### 3.6 Skill Manager

**文件**: `mathvideo/agents/skill_manager.py`
**职责**: 按任务类型加载经验技巧，注入到 LLM Prompt 中

**加载逻辑**: `load_skills("geometry")` → 加载 `common/` + `geometry/` 目录下所有 `.md` / `.yaml` 文件 → 拼接为带层级标题的文本 → 追加到 Prompt 末尾。

**当前 Skill 文件清单**:

| 目录 | 文件 | 内容概要 |
|------|------|---------|
| `common/` | `grid_positioning.md` | 10×10 网格定位系统用法 |
| `common/` | `label_placement.md` | 标签定位最佳实践 |
| `common/` | `visual_consistency.md` | 跨 Section 颜色/坐标/字号一致性规则 |
| `geometry/` | `sequential_sections.md` | 递进 Section 间的对象继承模式 |
| `geometry/` | `triangle_construction.md` | 三角形构造和标注技巧 |
| `geometry/` | `angle_bisector_parallel.md` | 角平分线/角弧/平行线/交点计算 |
| `geometry/` | `symmetry_construction.md` | 轴对称点计算/动画过程/勾号标记 |
| `geometry/` | `midpoint_extension.md` | 中点/倍长/辅助线/射线构造 |
| `proof/` | `proof_animation.md` | 等式链/高亮/推理箭头/几何公式联动 |

**扩展方式**: 在对应目录下新建 `.md` 文件即可自动生效，无需修改代码。

## 4. 支撑模块

### 4.1 LLM Client

**文件**: `mathvideo/llm_client.py`

`ClaudeDirectChat` 继承 LangChain `BaseChatModel`，直接使用 `requests` 调用 Anthropic Messages API：

- **为何不用官方 SDK**: 绕过 anthropic SDK 版本与 langchain-anthropic 的兼容性问题
- **API 版本**: 固定使用 `2023-06-01`，稳定可靠
- 支持 system / human / assistant 消息格式转换
- 所有 Agent 通过 `get_llm(temperature, max_tokens)` 统一创建实例

### 4.2 Gemini Native

**文件**: `mathvideo/gemini_native.py`

封装 Google Gemini 原生 `generateContent` API（非 OpenAI 兼容接口）：

- `messages_content_to_parts()`: 将 OpenAI 格式的消息转为 Gemini parts
- `file_to_inline_part()`: 将本地文件转为 Base64 inline 数据
- `generate_content_from_parts()`: 发送请求并提取文本响应

用于 Planner 的图片理解和 Critic 的视觉分析。

### 4.3 TeachingScene (manim_base.py)

**文件**: `mathvideo/manim_base.py` (937行)

Manim Scene 子类，是所有生成脚本的基类。核心功能：

| 功能 | 方法 | 说明 |
|------|------|------|
| 布局初始化 | `setup_layout(title, lines)` | 左侧讲义 + 右侧网格 |
| 网格定位 | `place_at_grid(obj, 'E5')` | 单点定位 |
| 区域定位 | `place_in_area(obj, 'A1', 'C3')` | 自动缩放适配区域 |
| 安全兜底 | `fit_to_screen(obj)` | 确保不超出画面 |
| 边标签 | `add_side_label(polygon, idx, text)` | 几何体边标注 |
| 顶点标签 | `add_vertex_label(polygon, idx, text)` | 几何体顶点标注 |
| 直角标记 | `add_right_angle_mark(...)` | 直角标记渲染 |
| 讲义高亮 | `highlight_line(n)` | 同步讲义进度 |

**防错机制**:
- **LaTeX 回退**: 自动检测 `pdflatex`，不可用时 monkey patch `MathTex` 为 `Text` 子类
- **颜色别名**: `CYAN`, `NAVY`, `BROWN`, `VIOLET` 等常见颜色映射
- **LLM 兼容**: `grid_to_coords`, `grid_anchor`, `get_grid_position` 等别名方法
- **文本缩放**: 只缩小过长文本，不拉伸短文本

### 4.4 Utils

**文件**: `mathvideo/utils.py`

| 函数 | 说明 |
|------|------|
| `slugify(value)` | 文件系统友好格式化，保留中文字符 |
| `make_slug(value, max_length=40, extra=None)` | 生成可读 slug（截断+6位 sha1 哈希后缀） |
| `rename_project_dir(old_dir, new_slug)` | AI 指导的项目目录重命名 |

**slug 示例**: 输入 `"等边三角形中的对称与交点构造"` → 输出 `"等边三角形中的对称与交点构造-75bd10"`

### 4.5 Config

**文件**: `mathvideo/config.py`

从 `.env` 文件加载所有配置：

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `CLAUDE_API_KEY` | 必填 | Anthropic API 密钥 |
| `CLAUDE_MODEL_NAME` | 可选 | 默认 `claude-opus-4-5-20251101` |
| `GEMINI_API_KEY` | 可选 | 启用视觉分析功能 |
| `GEMINI_VISION_MODEL_NAME` | 可选 | 默认 `gemini-3-pro-preview` |
| `ICONFINDER_API_KEY` | 可选 | 启用真实图标下载 |
| `USE_VISUAL_FEEDBACK` | bool | 是否启用视觉反馈循环 |
| `USE_ASSETS` | bool | 是否启用资产增强 |

## 5. Prompt 体系

**文件**: `mathvideo/agents/prompts.py` (521行)

所有 LLM Prompt 模板集中管理，修改 LLM 行为时优先编辑此文件。

| Prompt 变量 | 起始行 | Agent | 说明 |
|-------------|--------|-------|------|
| `ROUTER_PROMPT` | L13 | Router | 任务分类（4 种类型） |
| `PLANNER_PROMPT` | L55 | Planner | 通用知识点/应用题 storyboard |
| `PLANNER_GEOMETRY_PROMPT` | L105 | Planner | 几何题递进 storyboard |
| `PLANNER_PROOF_PROMPT` | L168 | Planner | 证明题逻辑链 storyboard |
| `CODER_PROMPT` | L209 | Coder | 独立模式代码生成 |
| `CODER_SEQUENTIAL_PROMPT` | L322 | Coder | 递进模式代码生成 |
| `FIX_CODE_PROMPT` | L405 | Coder (fix) | 错误修复 |
| `ASSET_PROMPT` | L432 | AssetManager | 图标需求分析 |
| `CRITIC_PROMPT` | L456 | Critic | 视觉分析指令 |
| `REFINE_CODE_PROMPT` | L494 | Coder (refine) | 视觉优化 |

## 6. Web 后端 (FastAPI)

### 6.1 入口与中间件

**文件**: `backend/main.py`

```python
app = FastAPI(title="MathVideo API", version="1.0.0")
```

- **CORS**: 允许 `localhost:3000`（Next.js）、Tauri 桌面端
- **静态文件**: 挂载 `output/` 目录到 `/static/` 路径
- **路由前缀**: `/api/projects/` / `/api/generate/` / `/api/refiner/`

### 6.2 API 路由

#### 生成 API (`backend/api/generate.py`)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/generate/` | POST | 启动生成任务，返回 `task_id` |
| `/api/generate/ws/{task_id}` | WebSocket | 实时日志推送 |
| `/api/generate/{slug}/section/{section_id}` | POST | 重新生成单个章节（**TODO**） |

**关键实现细节**:
- POST 请求支持 `application/json` 和 `multipart/form-data`（图片上传）
- 生成任务通过 `asyncio.create_task()` 异步执行
- `run_generation()` 等待最多 5 秒让 WebSocket 连接建立，解决竞态条件
- 子进程通过 `asyncio.create_subprocess_shell` 执行 CLI Pipeline
- 实时读取 stdout，按 emoji 判断日志级别（✅=success, ❌=error, ⚠️=warning）
- CLI 可能重命名项目目录（AI 生成名称），后端通过扫描 `output/` 最新目录检测实际 slug

#### 项目 API (`backend/api/projects.py`)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/projects/` | GET | 获取所有项目列表（按时间倒序） |
| `/api/projects/{slug}` | GET | 获取单个项目详情 |
| `/api/projects/{slug}` | DELETE | 删除项目 |
| `/api/projects/{slug}/storyboard` | GET | 获取分镜 JSON |
| `/api/projects/{slug}/storyboard` | PUT | 更新分镜 JSON |
| `/api/projects/{slug}/videos` | GET | 获取视频文件列表 |
| `/api/projects/{slug}/scripts` | GET | 获取脚本文件列表 |

#### 优化 API (`backend/api/refiner.py`)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/refiner/{slug}/critique/{section_id}` | POST | 对章节视频进行视觉分析 |
| `/api/refiner/{slug}/refine` | POST | 根据建议优化代码 |
| `/api/refiner/{slug}/render/{section_id}` | POST | 重新渲染指定章节 |

### 6.3 WebSocket 协议

**连接**: `ws://localhost:8000/api/generate/ws/{task_id}`

**服务端消息格式**:
```json
// 连接确认
{"type": "connected", "message": "已连接到任务 xxx"}

// 日志推送
{"type": "log", "level": "info|success|error|warning", "message": "..."}

// 状态更新
{"type": "status", "status": "running|completed|failed", "data": {"slug": "..."}}

// 心跳
{"type": "heartbeat"}

// Pong 响应
{"type": "pong"}
```

**客户端消息**: 发送 `"ping"` 维持连接，30 秒超时自动发心跳。

## 7. CLI 主流程

**文件**: `mathvideo/cli.py`

```
main()
├── 1. 解析命令行参数（prompt, --image, --render）
├── 2. 生成初始 slug，创建输出目录
├── 3. 处理输入图片（复制到 inputs/）
├── 4. Router 分类任务类型
├── 5. Planner 生成 storyboard.json
├── 6. 用 AI topic 重命名项目目录
├── 7. AssetManager 分析/下载资产
├── 8. 遍历 sections：
│   ├── Coder 生成代码
│   ├── 保存 scripts/section_N.py
│   ├── (递进模式) 传递代码给下一 Section
│   └── (--render) Manim 渲染
│       ├── 成功 → Critic → Refiner → 记录视频路径
│       └── 失败 → fix_code → 重试（最多3次）
├── 9. 合并所有分镜视频 → final_video.mp4
└── 10. 输出完成信息
```

**视频合并**: `_merge_videos()` 使用 PyAV（Manim 内置依赖）的 concat demuxer + decode/encode 方式拼接，CLI ffmpeg 作为回退方案。

## 8. 输出目录结构

```
output/<slug>/                    # 如: 等边三角形中的对称与交点构造-75bd10
├── storyboard.json               # 完整分镜脚本（含 task_type, available_assets）
├── inputs/                       # 用户上传图片副本
│   └── image1.png
├── assets/                       # SVG 图标（AssetManager 生成）
│   ├── triangle.svg
│   └── angle.svg
├── scripts/                      # Manim Python 脚本
│   ├── section_1.py
│   ├── section_2.py
│   └── section_3.py
├── media/                        # Manim 渲染输出
│   └── videos/
│       ├── section_1/480p15/Section1Scene.mp4
│       ├── section_2/480p15/Section2Scene.mp4
│       └── section_3/480p15/Section3Scene.mp4
├── final_video.mp4               # 合并后的完整视频
└── _concat_list.txt              # 临时文件（合并后自动删除）
```

## 9. 环境与部署

### 9.1 依赖

**核心**: `manim>=0.18`, `langchain>=0.1`, `requests`, `json5`, `python-dotenv`, `pydantic>=2.0`

**Web**: `fastapi>=0.104`, `uvicorn[standard]`, `python-multipart`, `websockets`

**视觉**: `opencv-python`, `numpy`（Critic 帧提取；当前通过 ffmpeg CLI 实现）

**隐式**: `av` (PyAV，由 manim 安装，视频合并使用)

### 9.2 启动命令

```bash
# CLI 生成
python -m mathvideo "勾股定理" --render
python -m mathvideo "题目描述" --image ./img.png --render

# Web 后端
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 前端开发
cd frontend && npm run dev    # http://localhost:3000
```

### 9.3 环境变量 (.env)

```env
# 必填
CLAUDE_API_KEY=sk-ant-...

# 可选
CLAUDE_MODEL_NAME=claude-opus-4-5-20251101
GEMINI_API_KEY=AIza...
GEMINI_VISION_MODEL_NAME=gemini-3-pro-preview
ICONFINDER_API_KEY=...
```

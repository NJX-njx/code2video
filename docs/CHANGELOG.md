# MathVideo 变更日志

> 记录项目重要的架构变更和功能改进

## 2026-02-11: 稳定性与 UI 改进（v1.2）

### Bug 修复

#### 1. 后端 API 307 重定向循环

Next.js `rewrites` 代理层可能剥离尾斜杠，导致 FastAPI 返回 307 重定向形成循环，前端报 "Failed to fetch"。

**修复**: 所有 POST 路由添加双装饰器 `@router.post("")` + `@router.post("/")`，兼容有/无尾斜杠请求。

#### 2. 子进程 Shell 解析破坏数学输入（根因）

用户输入的数学表达式含 `$`、`>`、`^`、`()` 等字符，`create_subprocess_shell()` 通过 cmd.exe 执行时会将这些解释为 shell 操作符，导致命令被截断，`--output-dir` 和 `--render` 参数丢失。

**修复**: 
- 将 `create_subprocess_shell()` 改为 `create_subprocess_exec()`，直接传递参数列表，完全绕过 shell 解析
- `_detect_python_command()` 返回 `list` 而非 `str`
- 移除不再需要的 `_quote_arg()` 和 `shlex` 导入
- 新增 `PYTHONUTF8=1` 环境变量确保子进程 UTF-8 输出

#### 3. CLI Unicode 编码崩溃

Windows 默认 GBK 编码无法输出 emoji（🚀），`print()` 抛出 `UnicodeEncodeError`。

**修复**: 在 `cli.py` 的 `main()` 函数入口添加 `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`。

#### 4. Web 模式下目录重命名导致双项目

CLI 在 Web 模式下仍执行目录重命名，导致后端找不到原始输出目录。

**修复**: 添加 `and not args.output_dir` 条件，当后端通过 `--output-dir` 指定路径时跳过重命名。

#### 5. 合并视频文件名不匹配

前端 `ProjectPageClient.tsx` 使用 `final_merged.mp4`，但 CLI 生成文件为 `final_video.mp4`。

**修复**: 前端统一为 `final_video.mp4`。

#### 6. 动画区可见分割线

`setup_layout()` 在讲义区和动画区之间绘制了一条可见的竖线 (`Line` 对象)，影响美观。

**修复**: 移除 `Line` 对象的创建，仅保留逻辑上的 `divider_x` 坐标值。

#### 7. LaTeX 回退分数渲染错误

旧的 `MathTex` 回退实现用简单的字符串替换（`replace("\\", "")` → `replace("frac", "/")`），导致 `\frac{9}{x-3}` 变成 `/9x-3`。

**修复**: 完整重写 `MathTex` 回退类：
- 结构化正则解析器，支持 3 层嵌套大括号
- 正确处理顺序：`^{}`/`_{}` → `\sqrt{}` → `\frac{}{}`
- 完整的 Unicode 符号映射表（希腊字母、运算符、关系符、箭头等）
- 对 `DecimalNumber`、`NumberLine` 等内部引用原始 `MathTex` 的组件进行深度补丁

#### 8. LaTeX Deep Monkey Patch

Manim 的 `DecimalNumber.__init__` 捕获了原始 `MathTex` 引用（在模块导入时），导致 monkey patch 未完全生效。

**修复**: 补丁阶段检测 `DecimalNumber.__init__` 中的原始引用并替换。

### UI 改进

#### 1. 进度条与阶段追踪

LogViewer 新增 5 阶段进度条（规划 → 资产 → 代码 → 渲染 → 合并），当未启用渲染时，跳过的阶段显示删除线样式。

#### 2. 条件完成消息

首页根据实际渲染状态显示不同完成消息：
- 已渲染: "✅ 视频已生成！" + 视频播放入口
- 未渲染: "✅ 代码已生成（未渲染视频）" + 分镜查看入口

#### 3. 渲染状态检测

后端新增 `_detect_rendered_video()` 函数，扫描 `media/videos/` 目录检测实际渲染的 .mp4 文件，代替仅依赖 `--render` 参数判断。

### 修改的文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/api/generate.py` | 修改 | `create_subprocess_exec`、双路由装饰器、`_detect_rendered_video`、`PYTHONUTF8=1` |
| `mathvideo/cli.py` | 修改 | UTF-8 编码修复、`--output-dir` 参数、Web 模式跳过重命名 |
| `mathvideo/manim_base.py` | 修改 | 移除可见分割线、重写 MathTex 回退、Deep Monkey Patch |
| `frontend/app/page.tsx` | 修改 | 条件完成消息、`rendered` 状态 |
| `frontend/app/projects/[slug]/ProjectPageClient.tsx` | 修改 | 视频文件名修正 |
| `frontend/components/LogViewer.tsx` | 修改 | 5 阶段进度条、跳过阶段样式 |
| `frontend/lib/types.ts` | 修改 | 新增 `CompletionData` 接口 |

---

## 2026-02-10: 多项改进（v1.1）

### 新增功能

#### 1. Router Agent — 任务类型路由

新增 `mathvideo/agents/router.py`，在 Planner 之前执行任务分类。

- 支持 4 种任务类型：`knowledge`（知识点）、`geometry`（几何）、`problem`（应用题）、`proof`（证明）
- LLM 理解语义，非简单关键词匹配
- 容错解析支持 4 级回退（直接匹配 → JSON → 文本搜索 → 中文映射）
- 根据类型决定 Section 模式：
  - `independent`（独立模式）：knowledge / problem
  - `sequential`（递进模式）：geometry / proof

#### 2. 递进模式 (Sequential Sections)

新增几何和证明题的递进 Section 生成能力。

- Planner 使用专用 Prompt（`PLANNER_GEOMETRY_PROMPT` / `PLANNER_PROOF_PROMPT`），为每个 Section 标注 `inherited_objects` 和 `new_objects`
- Coder 使用 `CODER_SEQUENTIAL_PROMPT`，接收前序 Section 的完整代码作为上下文
- 新 Section 先 `self.add()` 静默重建继承对象，再动画展示新增对象
- 确保几何题每步构造与前步视觉连贯

#### 3. Skill 注入系统

新增 `mathvideo/agents/skill_manager.py` + `mathvideo/skills/` 目录。

- 按任务类型分目录（common / geometry / knowledge / problem / proof）存储经验 `.md` 文件
- `load_skills(task_type)` 加载 `common/` + 指定类型目录的所有 Skill
- 拼接为带层级标题的文本，追加到 Planner 和 Coder 的 Prompt 末尾
- 新增 Skill 只需在对应目录下添加 `.md` 文件，无需修改代码

**当前 Skill 文件（10 个）**：
- `common/grid_positioning.md` — 网格定位用法
- `common/label_placement.md` — 标签定位最佳实践
- `common/visual_consistency.md` — 跨 Section 视觉一致性规则
- `geometry/sequential_sections.md` — 递进 Section 对象继承
- `geometry/triangle_construction.md` — 三角形构造技巧
- `geometry/angle_bisector_parallel.md` — 角平分线/平行线
- `geometry/symmetry_construction.md` — 轴对称构造
- `geometry/midpoint_extension.md` — 中点/倍长/辅助线
- `proof/proof_animation.md` — 等式链/推理箭头/联动

#### 4. AI 生成项目文件夹名

改写 `mathvideo/utils.py`：

- `slugify()` 保留中文字符（正则 `[\u4e00-\u9fff]`）
- `make_slug()` 最大长度从 30→40 字符，哈希从 8→6 字符
- 新增 `rename_project_dir()` 函数，安全重命名（不覆盖已存在目录）
- CLI 在 Planner 生成 storyboard 后，用 AI 的 `topic` 字段重命名输出目录
- 后端 `generate.py` 在子进程结束后检测重命名，扫描 `output/` 最新目录获取实际 slug

**效果**: `已知等边三角形ABC点D是BC边上一点设角BAD等于alpha点C-273bcf` → `等边三角形中的对称与交点构造-75bd10`

#### 5. 分镜视频合并

在 `mathvideo/cli.py` 新增 `_merge_videos()` 函数：

- 主方案：PyAV（Manim 内置依赖 `av` 模块）concat demuxer + decode/encode
- 回退方案：CLI ffmpeg（`-c copy` 快速拼接）
- 渲染循环中收集所有成功视频路径，循环结束后合并为 `final_video.mp4`
- 单个视频时直接复制为 `final_video.mp4`

#### 6. 新增 Prompt 模板

在 `mathvideo/agents/prompts.py` 新增 3 个模板：

- `ROUTER_PROMPT` — 任务类型分类指令
- `PLANNER_GEOMETRY_PROMPT` — 几何题递进分镜（含 `inherited_objects` / `new_objects` 字段要求）
- `PLANNER_PROOF_PROMPT` — 证明题逻辑链分镜
- `CODER_SEQUENTIAL_PROMPT` — 递进模式代码生成（接收 `previous_code`）

### 修改的文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `mathvideo/agents/router.py` | **新增** | Router Agent |
| `mathvideo/agents/skill_manager.py` | **新增** | Skill 加载器 |
| `mathvideo/skills/**/*.md` | **新增** | 10 个技能文件 |
| `mathvideo/agents/prompts.py` | 修改 | 新增 4 个 Prompt 模板 |
| `mathvideo/agents/planner.py` | 修改 | 按任务类型选择 Prompt + Skill 注入 |
| `mathvideo/agents/coder.py` | 修改 | 支持递进模式 + Skill 注入 |
| `mathvideo/agents/__init__.py` | 修改 | 导出 Router 和 SkillManager |
| `mathvideo/cli.py` | 修改 | Router 集成 + 项目重命名 + 视频合并 |
| `mathvideo/utils.py` | 重写 | 中文 slug + rename_project_dir |
| `backend/api/generate.py` | 修改 | 重命名目录检测 |
| `docs/BACKEND.md` | **新增** | 后端架构文档 |
| `docs/CHANGELOG.md` | **新增** | 变更日志 |
| `.github/copilot-instructions.md` | 更新 | 反映新架构 |

### 验证记录

1. **Proof 类型端到端测试**: `"证明：等边三角形的三条高相等"` → Router→proof, 递进模式, 3 sections 全部渲染成功（Section 3 自动修复 1 次）, 文件夹重命名为 `等边三角形三条高相等的证明-f0d3e6` ✓

2. **Geometry 类型端到端测试**: 等边三角形对称与交点构造（含图片输入）→ Router→geometry, 递进模式, 5 sections 全部首次渲染成功, 文件夹重命名为 `等边三角形中的对称与交点构造-75bd10`, 5 个视频合并为 `final_video.mp4` ✓

---

## 2026-02-08: 初始架构

### 核心功能

- Planner Agent: 将数学主题转为 storyboard.json
- Coder Agent: 为每个 Section 生成 Manim 代码
- Fix Agent: 渲染失败时自动修复代码（最多 3 次重试）
- Visual Critic: Gemini/Claude 视觉分析渲染结果
- Refiner: 根据视觉反馈优化代码
- AssetManager: 图标资产下载/占位
- TeachingScene (manim_base.py): 937行基类，网格定位/颜色/LaTeX 回退
- ClaudeDirectChat (llm_client.py): requests 直调 Anthropic API
- FastAPI 后端: REST API + WebSocket 实时日志
- Next.js 前端: 生成表单 + 日志查看 + 视频播放 + 分镜编辑

# MathVideo AI 编码助手指南

本指南旨在帮助 AI 助手高效理解和维护 `mathvideo` 项目。该项目是一个利用 LLM (Claude/Kimi) 和 Manim 自动生成数学讲解视频的端到端自动化工具。

## 1. 核心架构与数据流

- **目标**: 将数学关键词 ("Topic") 转换为完整的 Manim 视频工程。
- **Pipeline**:
  1.  **Planner** (`mathvideo/agents/planner.py`): 生成结构化 Storyboard (JSON)。
  2.  **Asset Manager** (`mathvideo/agents/asset_manager.py`): 下载/生成所需图像资源。
  3.  **Coder** (`mathvideo/agents/coder.py`): 生成 Manim Python 代码。
  4.  **Renderer** (`main.py`): 执行 `manim` 渲染视频。
  5.  **Refiner Loop** (`mathvideo/agents/critic.py`): 若启用 `USE_VISUAL_FEEDBACK`，使用视觉模型 (Claude Vision) 分析视频帧并自动迭代代码。

- **目录结构**: 所有生成内容必须严格遵循 `output/<topic_slug>/` 结构：
    - `storyboard.json`: 核心剧本。
    - `scripts/`: `.py` 动画脚本 (e.g., `section_1.py`).
    - `media/`: Manim 渲染输出。
    - `assets/`: 图片资源。

## 2. 关键开发规范

### 2.1 语言与注释
- **强制中文**: 所有新增代码注释、文档字符串、以及生成的视频解说词/文本，**必须使用中文**。
- **注释风格**: 解释“为什么”这样做，保持详细。

### 2.2 Manim 代码生成 (CRITICAL)
- **基类继承**: 所有场景类必须继承自 `mathvideo.manim_base.TeachingScene`。
- **布局系统**: 使用 `TeachingScene` 提供的标准化布局：
    ```python
    # 必须在 construct 首行调用
    self.setup_layout(title="标题", lecture_notes=["笔记1", "笔记2"]) 
    # 使用网格系统定位 (A-J行, 1-10列)
    self.place_at_grid(mobject, "C5") 
    ```
- **颜色兼容性**: 使用 `mathvideo.manim_base` 中定义的别名 (如 `LIGHT_BLUE`, `LIGHT_YELLOW`)，**严禁**使用生僻 Manim 颜色。
- **LaTeX 回退**: 不要假设 `MathTex` 原生可用。`mathvideo.manim_base` 会在无 LaTeX 环境下通过 Monkey Patch 将 `MathTex` 回退为 `Text`。编写代码时只需正常使用 `MathTex`，无需手动检测。

### 2.3 异常处理与调试
- **文件路径**: 始终使用 `os.path.join`，且基于 `output/<topic>/` 相对路径。
- **API 调用**: `mathvideo/agents/` 中的 LLM 调用必须包裹在 `try-except` 中。

## 3. 常用命令与工作流

- **完整运行**:
  ```bash
  python -m mathvideo "勾股定理" --render
  ```
- **手动调试生成脚本** (渲染失败时):
  ```bash
  # 必须在项目根目录运行，因为需要 import mathvideo
  manim -qm output/<topic>/scripts/section_X.py SectionXScene
  ```
- **环境**:
  - Python 3.10+, Conda 环境 `mathvideo`。
  - 依赖: `manim`, `ffmpeg`, `langchain`。

## 4. 关键文件索引
- `main.py`: 编排流水线，包含渲染重试和 Refiner 循环逻辑。
- `mathvideo/manim_base.py`: **核心文件**。定义 `TeachingScene` 布局、Grid 系统、颜色别名及 LaTeX 回退机制。
- `mathvideo/config.py`: 配置 (API Keys, Models)。优先遵循 `.env`。

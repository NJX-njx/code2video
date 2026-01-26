# MathVideo AI 编码助手指南

本指南旨在帮助 AI 助手高效理解和维护 `mathvideo` 项目。该项目是一个利用 LLM (Kimi) 和 Manim 自动生成数学讲解视频的自动化工具。

## 1. 核心架构与设计理念

- **项目目标**: 将数学主题关键词转换为完整的 Manim 视频工程。
- **数据流**: Keyword -> `Planner` (Layout/Storyboard) -> `Coder` (Python Script) -> `Manim` (Video).
- **关键文件**:
  - `main.py`: 编排整个流水线。
  - `src/agents/planner.py`: 使用 LangChain 生成 JSON 格式的教学大纲。
  - `src/agents/coder.py`: 使用 LangChain 将大纲转换为 Manim Python 代码。
  - `src/manim_base.py`: 定义 Manim 基础类和兼容性层（重要！）。
  - `src/config.py`: 项目配置（API Key, 模型名称）。

## 2. 关键开发规范

### 2.1 语言与注释
- **强制中文**: 所有新增代码注释、文档字符串、以及生成的视频解说词，**必须使用中文**。
- **风格**: 保持与现有代码一致的详细注释风格，解释“为什么”这样做。

### 2.2 Manim 代码生成规范
- **继承关系**: 生成的场景类应尽量继承自 `TeachingScene` (如果在上下文中可用) 或 `Scene`。
- **LaTeX 兼容性**:
  - 使用 `src.manim_base` 中的定义。
  - 考虑到系统可能未安装 LaTeX，**不要直接假设 `MathTex` 总是原生可用**。`src/manim_base.py` 实现了当 LaTeX 不可用时回退到 `Text` 的机制。
  - 颜色使用预定义的别名 (如 `LIGHT_BLUE`, `LIGHT_YELLOW`)，避免使用生僻的 Manim 颜色常量。
- **动画节奏**: 适当使用 `run_time` 和 `wait()` 确保视频节奏适中，适合教学。

### 2.3 异常处理与调试
- **生成阶段**: 在 `src/agents/` 中，网络请求和解析逻辑需包裹在 `try-except` 中。
- **路径管理**: 所有的文件读写应基于 `output/<topic>/` 目录结构。

## 3. 工作流与集成

### 3.1 LangChain 集成
- 使用 `|` 管道操作符构建 Chain: `prompt | llm | parser`。
- LLM 实例获取统一通过 `src.llm_client.get_llm()`。

### 3.2 运行与测试
- **完整运行**:
  ```bash
  python main.py "你的数学主题" --render
  ```
- **调试生成的脚本**:
  生成的脚本位于 `output/<topic>/scripts/`。若渲染失败，可直接手动运行该脚本进行调试：
  ```bash
  manim -qm output/<topic>/scripts/section_1.py Section1Scene
  ```

## 4. 注意事项
- 这是一个轻量级生产工具，注重代码的稳定性和生成的成功率，而非复杂的实验性功能。
- 这里不涉及 `Code2Video` 项目的复杂 Prompt 链或 Benchmark 逻辑。

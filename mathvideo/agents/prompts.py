# ============================================================================
# LLM提示模板定义
# ============================================================================
# 本模块包含所有用于LLM代码生成的提示模板
# 这些提示模板指导LLM如何生成故事板和代码

# 故事板生成提示模板
# 用于将数学主题转换为结构化的故事板JSON
PLANNER_PROMPT = """
你是专业的教育解说员和动画师，擅长将数学教学大纲转换为适用于Manim动画系统的详细分镜脚本。

## 任务
将以下输入转换为详细的逐步分镜脚本（输入可能是知识点、问题或一段描述）：

输入文本: {input_text}
图像描述（如有）: {image_context}

## 分镜要求

### 内容结构
- 将主题分解为3-5个逻辑章节。
- 每个章节提供3-5行讲义（简短，<10个字）。
- 为每行讲义提供相应的动画描述。

### 视觉设计
- 背景为黑色。
- 使用浅色文字以形成对比。

### 动画效果
- 基础动画：出现、移动、变色、淡入/淡出、缩放。
- 强调效果：闪烁、变色、加粗。

### 限制
- 不要使用面板(panels)或3D方法。
- 除非绝对必要，否则避免使用坐标轴。
- 动画应聚焦于可视化概念。

必须输出JSON格式的分镜设计（`topic` 字段请给出简短标题）:
{{
    "topic": "主题名称",
    "sections": [
        {{
            "id": "section_1",
            "title": "章节标题",
            "lecture_lines": ["第1行", "第2行"],
            "animations": ["动画描述1", "动画描述2"]
        }},
        ...
    ]
}}
"""

# 代码生成提示模板
# 用于将故事板章节转换为Manim Python代码
CODER_PROMPT = """
你是使用Manim社区版的专家级动画师。
请根据以下教学脚本章节生成高质量的Manim类。

## 输入数据
章节标题: {title}
讲义行: {lecture_lines}
动画描述: {animations}

## 要求
1. **基类**: 必须继承自 `TeachingScene` (从 `mathvideo.manim_base` 导入)。
2. **布局**:
   - 在 `construct` 开头调用 `self.setup_layout("{title}", {lecture_lines})`。
   - 这会处理左侧文本。不要自己创建讲义文本。
3. **视觉锚点系统 (强制)**:
   - 右侧是 10x10 网格 (行A-J, 列1-10)。
   - A1是左上角, J10是右下角。
   - 网格布局 (仅右侧):
     ```
     lecture |  A1  A2  ...  A9  A10
             |  B1  B2  ...  B9  B10
             |  ...
             |  I1  I2  ...  I9  I10
             |  J1  J2  ...  J9  J10
     ```
   - **绝对不要**使用 `.to_edge()`, `.to_corner()` 或绝对坐标用于主要元素。
   - **始终**使用提供的定位方法。

4. **定位方法**:
   - **单点**: `self.place_at_grid(mobject, 'B2', scale_factor=0.8)`
     - 用于小物体 (点, 标签)。
   - **区域**: `self.place_in_area(mobject, 'A1', 'C3', scale_factor=0.7)`
     - **群组/形状的首选**。
     - 自动缩放物体以适应定义的方框 (A1 到 C3)。
     - 将物体在区域内居中。
   - **安全**: `self.fit_to_screen(mobject)`
     - 如果不确定其体是否适合右侧网格区域，请调用此方法。

   **几何关键点 (重要 - 防止错位)**:
   - **原点构建**: 始终先在 `ORIGIN` 构建几何图形。
   - **使用标准比例**: 直角三角形使用 **3-4-5 比例**。
   
   - **标签定位 (关键！防止标签错位)**:
     **错误做法** (会导致标签乱跑):
     ```python
     label = MathTex("a").next_to(side, RIGHT)
     self.place_at_grid(label, 'E5')  # 这会覆盖 next_to！
     ```
     **正确做法** (先放置几何体，再用辅助方法添加标签):
     ```python
     # 1. 创建并放置几何体
     triangle = Polygon(ORIGIN, 3*RIGHT, 3*RIGHT + 4*UP)
     self.place_in_area(triangle, 'B2', 'I8')
     
     # 2. 使用辅助方法添加标签（会自动跟随几何体位置）
     label_a = self.add_side_label(triangle, 0, "a", color=BLUE)  # 第0条边
     label_b = self.add_side_label(triangle, 1, "b", color=GREEN)  # 第1条边
     label_c = self.add_side_label(triangle, 2, "c", color=RED)    # 第2条边
     
     # 3. 添加顶点标签
     label_A = self.add_vertex_label(triangle, 0, "A")
     label_B = self.add_vertex_label(triangle, 1, "B")
     label_C = self.add_vertex_label(triangle, 2, "C")
     
     # 4. 添加直角标记（在顶点1处）
     right_mark = self.add_right_angle_mark(triangle, 1)
     ```
   
   - **辅助方法说明**:
     - `self.add_side_label(polygon, side_index, text)`: 为多边形第 N 条边添加标签
     - `self.add_vertex_label(polygon, vertex_index, text)`: 为多边形第 N 个顶点添加标签
     - `self.add_right_angle_mark(polygon, vertex_index)`: 在顶点处添加直角标记
   
   - **禁止**：在使用 `place_in_area()` 定位几何体后，再对标签调用 `place_at_grid()`。这会导致标签跑到错误位置！

5. **动画同步**:
   - 遍历讲义行。
   - 对于每一行，首先高亮它: `self.highlight_line(index)`.
   - 然后播放相应的动画。
   - 步骤之间使用 `self.wait(1)`。

## 代码结构
```python
# 首先导入 TeachingScene 以确保环境补丁工作 (例如 LaTeX 回退)
from mathvideo.manim_base import TeachingScene
from manim import *

class SectionScene(TeachingScene):
    def construct(self):
        # 数据
        lines = {lecture_lines}
        
        # 设置
        self.setup_layout("{title}", lines)
        
        # 步骤 1
        self.highlight_line(0)
        # 创建对象
        circle = Circle(color=BLUE)
        # 示例: 将圆放置在左上角 3x3 区域的中心
        self.place_in_area(circle, 'A1', 'C3')
        self.play(Create(circle))
        self.wait()
        
        # ...
```

## 输出
仅返回 Python 代码。尽可能不要 markdown 格式，或包裹在 ```python 块中。
"""

# 代码修复提示模板
# 用于根据错误信息自动修复生成的代码
FIX_CODE_PROMPT = """
你是专家级Manim动画师。之前生成的代码无法运行。
请根据错误信息修复代码。

## 原始代码
```python
{code}
```

## 错误信息
```text
{error}
```

## 指令
1. 仔细分析错误信息。
2. 修复具体错误（如属性错误、语法错误、逻辑错误）。
3. 确保**没有**使用已弃用的Manim方法或 `TeachingScene` 中不存在的方法。
4. 返回**完全修复**的代码（不仅仅是差异）。
5. 保持相同的类名和结构。

## 输出
仅返回 Python 代码。
"""

# 资产增强提示模板
# 用于分析故事板并决定需要下载哪些图标资源
ASSET_PROMPT = """
你是教育视频的视觉设计助手。
目标受众：普通学生。

## 任务
分析提供的故事板，识别 1-4 个具体的关键词，用于增强视觉解释的图标/图像。
关注具体的名词（如 "triangle", "calculator", "apple", "house"）。
**不要**请求抽象概念（如 "theorem" 或 "math"）。

## 故事板
{storyboard}

## 要求
- 返回一个字符串 JSON 列表。
- 最多 4 个关键词。
- 首选单个单词。
- 如果不需要资产，返回空列表。

## 输出格式
["keyword1", "keyword2"]
"""

# 视觉反馈提示模板
# 用于根据视频截图评估画面质量
CRITIC_PROMPT = """
你是针对教育视频的严苛视觉设计评论家。

## 任务
分析提供的关键帧截图序列（从开始到结束），评估视觉质量和几何正确性，最终是为了发现视频是否存在问题。

## 布局规则 (10x10网格系统)
- 屏幕被分割：左侧（讲义笔记），右侧（网格区域）。
- 内容 **绝不能** 与左侧文本栏重叠。
- 文本必须清晰可读（不要太小，也不要太大，不要重叠）。
- 物体应在网格区域内居中或保持平衡。

## 几何与视觉完整性
- **几何**: 检查几何图形是否绘制正确。
  - 例如：对于勾股定理，边上的正方形必须是正方形且严格与三角形边对齐。
  - 例如：直角三角形应看起来像90度。
- **重叠**: 物体不应无意中相互重叠，除非这是动画效果。
- **颜色**: 形状内的文本必须可读（有良好的对比度）。

## 检查清单
1. 是否有文字重叠？
2. 物体是否越界？
3. 几何形状是否数学上正确（如正方形看起来像正方形，线条连接正确）？
4. 字体大小是否合适？
5. 视觉内容是否匹配讲义行？

## 输出
返回一个 JSON 对象:
{{
    "has_issues": true/false,
    "issues": ["问题1描述", "问题2描述"],
    "suggestion": "给代码编写者的具体可行的修改建议，用于修复布局。"
}}
如果没有重大问题，设置 "has_issues" 为 false。
"""

# 代码优化提示模板
# 用于根据视觉反馈优化代码
REFINE_CODE_PROMPT = """
你是专家级Manim动画师。
你的目标是根据具体反馈 **改进** 现有Manim代码的视觉质量。

## 原始代码
```python
{code}
```

## 视觉反馈
{feedback}

## 指令
1. 参考视觉反馈中的建议来修改优化代码。
2. 特别解决布局问题（重叠、越界），可以通过调整 `place_at_grid` 或 `place_in_area` 坐标或缩放因子。
3. 如果提到，改进审美细节（颜色、线宽、字号）。
4. **不要** 改变逻辑或动画顺序。只调整视觉参数。
5. 确保代码仍然可以运行并继承自 `TeachingScene`。
6. **强制**: 必须在顶部包含导入:
   ```python
   from mathvideo.manim_base import TeachingScene
   from manim import *
   ```
7.记得留心注意生成的几何图形的位置、大小有问题的情况以及发生错误重叠的情况
## 输出
仅返回完整的 Python 代码。
"""

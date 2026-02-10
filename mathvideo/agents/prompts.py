# ============================================================================
# LLM提示模板定义
# ============================================================================
# 本模块包含所有用于LLM代码生成的提示模板
# 这些提示模板指导LLM如何生成故事板和代码
# 修改 LLM 行为时优先编辑此文件

# ============================================================================
# 路由器提示模板
# ============================================================================
# 用于判断用户输入属于哪种任务类型，决定后续使用哪种 Pipeline 模式
ROUTER_PROMPT = """
你是一位经验丰富的数学教育专家。你的任务是根据用户的输入判断其需求类型。

## 用户输入
文本: {input_text}
图像描述（如有）: {image_context}

## 任务类型说明

### knowledge（知识点讲解）
- 用户输入一个数学概念、定理名称或知识点
- 期望系统从零开始讲解该概念
- 特征: 输入简短，如"勾股定理"、"二次方程解法"、"圆的面积公式"
- 各章节之间相互独立

### geometry（几何构造/作图题）
- 用户输入包含具体的几何图形描述和构造步骤
- 通常有配图，描述"如图所示"、点的位置关系、对称/旋转/平行等操作
- 特征: 包含△、∠、"对称点"、"平行线"、"交于"、"连接"、"如图"等关键词
- 需要按顺序递进构造，后续步骤依赖前序图形

### problem（应用/计算题）
- 用户输入一道需要求解具体数值或表达式的题目
- 特征: 包含"求"、"计算"、"多少"、具体数值、实际应用场景
- 各步骤（审题→建模→求解→验证）相对独立

### proof（证明推导）
- 用户需要证明某个数学命题或推导某个公式
- 特征: 包含"证明"、"推导"、"为什么"、"说明...成立"
- 需要严格的逻辑链，后续步骤依赖前序结论

## 重要提示
- 如果用户在文本中**明确说明了要做什么**（如"请讲解..."、"请证明..."），以用户指令为准
- 不要仅靠关键词判断，要理解用户的**真实意图**
- 如果不确定，倾向于选择更具体的类型（geometry > knowledge）

## 输出
仅输出一个单词: knowledge / geometry / problem / proof
"""

# ============================================================================
# 故事板提示模板
# ============================================================================

# 故事板生成提示模板（通用版，用于 knowledge 和 problem 类型）
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
    "task_type": "knowledge",
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

# 几何构造题专用的故事板提示模板
# 核心区别: 要求生成递进式分镜，每个 Section 声明继承和新增的几何对象
PLANNER_GEOMETRY_PROMPT = """
你是专业的几何动画策划师，擅长将几何构造题转换为 Manim 动画的分镜脚本。

## 任务
将以下几何题目转换为**递进式**分镜脚本。每个 Section 必须在前一个 Section 的基础上**增量添加**新的几何对象。

输入文本: {input_text}
图像描述（如有）: {image_context}

## 关键约束（CRITICAL）

### 递进式构造
- 第一个 Section 建立基础图形（如画出△ABC）
- 后续 Section 在已有图形基础上添加新元素（如取点D、作对称点P、连接CP等）
- **每个 Section 的动画必须能看到之前所有已构造的对象**
- 使用 `inherited_objects` 声明从前序 Section 继承的对象
- 使用 `new_objects` 声明本 Section 新增的对象

### 精确还原题意
- **严格按照题目描述的顺序构造**，不要自行重新组织
- 如果题目说"点P是点B关于直线AD的对称点"，动画就要展示做对称的过程
- 如果有配图，动画要尽量还原图中的几何关系和布局

### 分镜结构
- 分为 2-5 个逻辑步骤，每步对应一个构造阶段
- 讲义行要简短（<10字），描述当前步骤在做什么
- 动画描述要具体，明确说明：画什么、在哪里、用什么颜色、标注什么文字

## 必须输出JSON格式:
{{
    "topic": "题目简短标题",
    "task_type": "geometry",
    "sections": [
        {{
            "id": "section_1",
            "title": "构建基础图形",
            "inherited_objects": [],
            "new_objects": ["triangle_ABC", "labels_ABC"],
            "lecture_lines": ["等边△ABC", "边长设为a"],
            "animations": [
                "在网格中心区域画出等边三角形ABC，用BLUE色线条",
                "在三个顶点处分别标注A、B、C"
            ]
        }},
        {{
            "id": "section_2",
            "title": "取点D并作对称点",
            "inherited_objects": ["triangle_ABC", "labels_ABC"],
            "new_objects": ["point_D", "point_P", "line_AD", "line_CP"],
            "lecture_lines": ["D在BC上", "P是B关于AD的对称", "连接CP"],
            "animations": [
                "在BC边上取一点D，用RED标注",
                "画出辅助线AD（虚线）",
                "构造B关于直线AD的对称点P，用GREEN标注",
                "连接CP，用YELLOW实线"
            ]
        }}
    ]
}}
"""

# 证明推导专用的故事板提示模板
# 核心区别: 要求生成逻辑链式分镜，每步依赖前步结论
PLANNER_PROOF_PROMPT = """
你是专业的数学证明动画策划师，擅长将证明过程转换为 Manim 动画的分镜脚本。

## 任务
将以下证明/推导题转换为**逻辑链式**分镜脚本。

输入文本: {input_text}
图像描述（如有）: {image_context}

## 关键约束

### 逻辑递进
- 每个 Section 对应证明的一个关键步骤
- 后续 Section 的结论依赖前序 Section 的结果
- 使用 `inherited_objects` 标注依赖的几何对象/公式
- 使用 `new_objects` 标注本步骤引入的新对象/新结论

### 视觉呈现
- 每步需要在动画中清楚展示推理过程
- 重要等式/不等式用 MathTex 展示
- 推理箭头、等号链等可视化逻辑关系

## 必须输出JSON格式:
{{
    "topic": "证明简短标题",
    "task_type": "proof",
    "sections": [
        {{
            "id": "section_1",
            "title": "步骤标题",
            "inherited_objects": [],
            "new_objects": ["新对象描述"],
            "lecture_lines": ["简短步骤1", "简短步骤2"],
            "animations": ["动画1: 具体描述", "动画2: 具体描述"]
        }}
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

# 带上下文的代码生成提示模板（用于 geometry / proof 的递进式 Section）
# 核心区别: 传入前序 Section 的完整代码，要求后续 Section 继承已有对象
CODER_SEQUENTIAL_PROMPT = """
你是使用Manim社区版的专家级动画师。
请根据以下教学脚本章节生成高质量的Manim类。

**重要**: 本 Section 是递进式构造的一部分。你必须在动画开始时**重建前序 Section 的所有几何对象**，
然后在此基础上添加本 Section 的新内容。

## 输入数据
章节标题: {title}
讲义行: {lecture_lines}
动画描述: {animations}
从前序 Section 继承的对象: {inherited_objects}
本 Section 新增的对象: {new_objects}

## 前序 Section 的完整代码（重要参考）
```python
{previous_code}
```

## 要求
1. **基类**: 必须继承自 `TeachingScene` (从 `mathvideo.manim_base` 导入)。
2. **布局**:
   - 在 `construct` 开头调用 `self.setup_layout("{title}", {{lecture_lines}})`。
   - 这会处理左侧文本。不要自己创建讲义文本。
3. **继承前序几何对象 (CRITICAL)**:
   - 参考前序代码中几何对象的**创建方式和坐标参数**
   - 在 `construct()` 开头（`setup_layout` 之后）**重新创建并放置这些对象**
   - 使用 `self.add(obj)` 添加到场景中（不要用动画，直接显示）
   - **必须使用与前序代码相同的坐标/网格位置**，确保对象位置一致
   - 然后再用动画添加本 Section 的新对象
4. **视觉锚点系统 (强制)**:
   - 右侧是 10x10 网格 (行A-J, 列1-10)。
   - A1是左上角, J10是右下角。
   - **绝对不要**使用 `.to_edge()`, `.to_corner()` 或绝对坐标用于主要元素。
   - **始终**使用提供的定位方法。
5. **定位方法**:
   - **单点**: `self.place_at_grid(mobject, 'B2', scale_factor=0.8)`
   - **区域**: `self.place_in_area(mobject, 'A1', 'C3', scale_factor=0.7)` （首选）
   - **安全**: `self.fit_to_screen(mobject)`

   **标签定位 (关键！防止标签错位)**:
   先 `place_in_area()` 放几何体，再用辅助方法添加标签：
   ```python
   label_a = self.add_side_label(triangle, 0, "a", color=BLUE)
   label_A = self.add_vertex_label(triangle, 0, "A")
   right_mark = self.add_right_angle_mark(triangle, 1)
   ```
   **禁止**先 `next_to` 再 `place_at_grid`（会覆盖位置）!

6. **动画同步**:
   - 先 `self.highlight_line(index)` 高亮讲义行
   - 然后播放对应动画
   - 步骤之间用 `self.wait(1)`

## 代码结构
```python
from mathvideo.manim_base import TeachingScene
from manim import *

class SectionScene(TeachingScene):
    def construct(self):
        lines = {lecture_lines}
        self.setup_layout("{title}", lines)
        
        # === 继承前序对象（直接显示，不要动画） ===
        # 参考前序代码，重建所有几何对象
        # triangle = Polygon(...)
        # self.place_in_area(triangle, 'B2', 'I8')
        # self.add(triangle)  # 直接 add，不要 play
        
        # === 本 Section 新内容（用动画展示） ===
        self.highlight_line(0)
        # ... 添加新的几何对象 ...
        self.play(Create(new_object))
        self.wait(1)
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

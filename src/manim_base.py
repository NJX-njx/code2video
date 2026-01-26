# 导入Manim的所有基础类和函数（用于创建动画）
from manim import *
# 导入shutil模块，用于查找系统命令（如pdflatex）的路径
import shutil
# 导入subprocess模块，用于执行系统命令（检查LaTeX是否可用）
import subprocess

# ============================================================================
# LLM兼容性常量定义
# ============================================================================
# 这些常量是为了让LLM更容易理解和使用颜色
# LLM可能不知道Manim的具体颜色名称，使用这些别名可以提高代码生成的成功率

# 浅蓝色：映射到Manim的BLUE_A（较亮的蓝色）
LIGHT_BLUE = BLUE_A
# 浅黄色：映射到Manim的YELLOW_A（较亮的黄色）
LIGHT_YELLOW = YELLOW_A
# 浅绿色：映射到Manim的GREEN_A（较亮的绿色）
LIGHT_GREEN = GREEN_A
# 浅粉色：映射到Manim的PINK（粉色）
LIGHT_PINK = PINK
# 浅灰色：映射到Manim的GREY_A（较亮的灰色）
LIGHT_GREY = GREY_A

# 常用颜色别名（防止LLM使用非Manim颜色）
# mapping common names missing in Manim to existing colors
CYAN = TEAL
NAVY = DARK_BLUE
BROWN = MAROON_E
VIOLET = PURPLE_A
# NOTE: Standard colors (RED, BLUE, GREEN, etc.) are already imported from manim

# ============================================================================
# LaTeX回退机制
# ============================================================================
# 由于Manim的MathTex需要LaTeX来渲染数学公式，但系统可能没有安装LaTeX
# 本模块提供了一个回退机制：如果LaTeX不可用，则使用Text类来近似显示数学公式

def check_latex_availability():
    """
    检查系统中pdflatex是否可用且正常工作
    
    功能说明：
    本函数通过两个步骤检查LaTeX是否可用：
    1. 检查pdflatex命令是否在系统PATH中
    2. 尝试运行pdflatex --version来验证它是否真的可以执行
    
    返回:
        bool: 
            - True: pdflatex可用且可以正常工作
            - False: pdflatex不可用或无法正常工作
    
    使用场景:
        - 在模块加载时自动检查，决定是否启用LaTeX回退机制
        - 如果返回False，将使用Text类替代MathTex来显示数学公式
    """
    # 第一步：检查pdflatex命令是否在系统PATH中
    # shutil.which()返回命令的完整路径，如果找不到则返回None
    if not shutil.which("pdflatex"):
        # 如果找不到pdflatex命令，直接返回False
        return False
    
    # 第二步：尝试执行pdflatex命令来验证它是否真的可以运行
    # 这是一个可选的但更安全的检查方法
    try:
        # 运行pdflatex --version命令来检查版本
        # 这是一个轻量级的操作，不会实际编译任何文档
        subprocess.run(
            ["pdflatex", "--version"],  # 命令和参数
            stdout=subprocess.DEVNULL,  # 丢弃标准输出（不显示版本信息）
            stderr=subprocess.DEVNULL,  # 丢弃标准错误（不显示错误信息）
            check=True  # 如果命令返回非零退出码则抛出异常
        )
        # 如果命令成功执行，说明LaTeX可用
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果命令执行失败或找不到文件，说明LaTeX不可用
        return False

# 在模块加载时检查LaTeX是否可用，将结果存储在全局变量中
# 这样其他代码可以直接使用LATEX_AVAILABLE来判断，而不需要重复检查
LATEX_AVAILABLE = check_latex_availability()

# 如果LaTeX不可用，启用回退机制
if not LATEX_AVAILABLE:
    # 打印警告信息，提醒用户LaTeX不可用
    print("\n" + "!"*60)
    print("WARNING: LaTeX (pdflatex) not found or not working.")
    print("Falling back to Text() for MathTex() objects.")
    print("Mathematical typesetting will be approximated.")
    print("!"*60 + "\n")

    class MathTex(Text):
        """
        LaTeX不可用时的回退类，将数学公式渲染为纯文本
        
        功能说明：
        当系统中没有安装LaTeX时，Manim的MathTex类无法正常工作。
        本类继承自Text类，提供一个兼容的接口，将LaTeX代码转换为可读的文本。
        
        工作原理：
        1. 接收LaTeX字符串（可能包含多个字符串）
        2. 移除LaTeX分隔符（如$...$）
        3. 将常见的LaTeX命令替换为Unicode符号
        4. 清理LaTeX语法（移除反斜杠、大括号等）
        5. 使用Text类渲染最终的文本
        
        注意：
        - 这是一个近似方案，无法完美渲染复杂的数学公式
        - 建议安装LaTeX以获得最佳的数学公式渲染效果
        - 支持的LaTeX命令有限，复杂公式可能显示不正确
        """
        def __init__(self, *tex_strings, **kwargs):
            """
            初始化MathTex回退类
            
            参数:
                *tex_strings: 可变数量的LaTeX字符串参数
                **kwargs: 传递给Text类的其他关键字参数（如font_size、color等）
            
            处理流程:
                1. 将所有LaTeX字符串连接成一个完整的文本
                2. 移除LaTeX分隔符和转义字符
                3. 替换常见LaTeX命令为Unicode符号
                4. 清理LaTeX语法结构
                5. 调用父类Text的构造函数进行渲染
            """
            # 步骤1：将所有输入的LaTeX字符串用空格连接成一个完整文本
            full_text = " ".join(tex_strings)
            # 步骤2：移除LaTeX的数学模式分隔符（$...$）
            full_text = full_text.replace("$", "")
            # 步骤3：移除LaTeX的反斜杠转义字符（粗略清理）
            # 注意：这是一个简单的替换，可能会误删一些需要的反斜杠
            full_text = full_text.replace("\\", "") # Crude cleanup
            
            # 步骤4：将常见的LaTeX数学命令映射为Unicode符号
            # 这样可以提高可读性，即使没有LaTeX也能理解数学表达式
            replacements = {
                "cdot": "·",      # 点乘符号
                "times": "×",     # 乘号
                "frac": "/",      # 分数（转换为斜杠）
                "sqrt": "√",      # 平方根符号
                "pi": "π",        # 圆周率
                "theta": "θ",     # 希腊字母theta
                "alpha": "α",     # 希腊字母alpha
                "beta": "β",      # 希腊字母beta
                "approx": "≈",    # 约等于
                "neq": "≠",       # 不等于
                "leq": "≤",       # 小于等于
                "geq": "≥",       # 大于等于
                "^{2}": "²",      # 上标2（平方）
                "_{2}": "₂",      # 下标2
            }
            # 遍历替换字典，将所有LaTeX命令替换为对应的Unicode符号
            for k, v in replacements.items():
                full_text = full_text.replace(k, v)
                
            # 步骤5：移除LaTeX的大括号（用于分组）
            # 这些在纯文本显示中不需要
            full_text = full_text.replace("{", "").replace("}", "")
            
            # 步骤6：调用父类Text的构造函数，使用清理后的文本进行渲染
            # 所有其他参数（如font_size、color等）都原样传递给Text类
            super().__init__(full_text, **kwargs)

    # ========================================================================
    # 猴子补丁（Monkey Patch）：替换manim模块中的MathTex类
    # ========================================================================
    # 我们需要将回退的MathTex类注入到manim模块的全局命名空间中
    # 这样即使生成的脚本使用`from manim import *`，也能使用我们的回退版本
    
    # 技术说明：
    # - 由于我们使用`from manim import *`，无法直接在本地覆盖MathTex
    # - 生成的脚本通常使用`from manim import *`和`from src.manim_base import TeachingScene`
    # - 如果只在这里定义MathTex，不会覆盖`from manim import *`导入的版本
    # - 解决方案：直接修改manim模块的MathTex属性（猴子补丁）
    
    # 导入manim模块（注意：这里导入的是模块对象，不是模块内容）
    import manim
    # 将manim模块中的MathTex类替换为我们的回退版本
    # 这样所有使用manim.MathTex的地方都会使用我们的回退类
    manim.MathTex = MathTex
    # 同时也替换Tex类（以防万一，因为有些代码可能使用Tex而不是MathTex）
    manim.Tex = MathTex

class TeachingScene(Scene):
    """
    教学视频的基础场景类，提供标准化的布局系统
    
    功能说明：
    本类为所有教学视频提供一个统一的布局框架，将屏幕分为两个区域：
    - 左侧区域：显示标题和讲义笔记（静态文本）
    - 右侧区域：显示动画内容（使用10x10网格定位系统）
    
    布局结构：
    ```
    ┌─────────────────────────────────────────┐
    │ 标题                                    │
    │ ─────────────────────────────────────  │
    │ 讲义笔记1                               │
    │ 讲义笔记2                               │
    │ 讲义笔记3                               │
    │ ...                                    │
    │                                        │
    │         │  A1  A2  ...  A10           │
    │         │  B1  B2  ...  B10           │
    │         │  ...                         │
    │         │  J1  J2  ...  J10           │
    └─────────────────────────────────────────┘
    ```
    
    网格系统：
    - 行：A（顶部）到J（底部），共10行
    - 列：1（左侧）到10（右侧），共10列
    - 位置表示：'A1'（左上角）、'J10'（右下角）
    
    使用示例:
        class MyScene(TeachingScene):
            def construct(self):
                # 设置布局（标题和讲义笔记）
                self.setup_layout("勾股定理", ["定义", "证明", "应用"])
                
                # 在网格位置创建对象
                circle = Circle()
                self.place_at_grid(circle, 'C5')
                self.play(Create(circle))
    """
    def setup_layout(self, title_text, lecture_notes):
        """
        设置场景的静态布局：标题和讲义笔记
        
        功能说明：
        本方法在场景左侧创建标题和讲义笔记，并在中间绘制一条分隔线。
        右侧区域保留用于动画内容，使用网格定位系统。
        
        参数:
            title_text (str): 场景的标题文本，显示在左上角
            lecture_notes (list[str]): 讲义笔记列表，每个元素是一行笔记文本
                笔记会垂直排列在标题下方，自动换行以适应左侧区域宽度
        
        布局细节:
            - 标题：36号字体，粗体，位于左上角（UL），距离边缘0.5单位
            - 分隔线：垂直分割线，位于x=-2.5处，将屏幕分为左右两部分
            - 笔记：24号字体，斜体，白色，限制宽度为4.0单位，垂直排列
            - 网格区域：右侧从x=-2.0到x=7.1，y从-3.5到3.5
        
        注意事项:
            - 必须在construct()方法开始时调用此方法
            - 笔记文本如果过长会自动缩放以适应宽度
            - 网格系统在调用此方法后自动初始化
        """
        # 步骤1：创建标题
        # 使用Text类创建标题，36号字体，粗体样式
        self.title = Text(title_text, font_size=36, weight=BOLD)
        # 将标题移动到左上角（UL = Up Left），距离边缘0.5单位
        self.title.to_corner(UL, buff=0.5)
        # 将标题添加到场景中（立即显示）
        self.add(self.title)

        # 步骤2：创建垂直分隔线
        # 屏幕宽度通常是14.22单位，高度是8.0单位
        # 将分隔线放置在x = -2.5处，将屏幕分为左右两部分
        self.divider_x = -2.5
        # 创建一条从顶部到底部的垂直线
        line = Line(
            # 起点：屏幕顶部（UP * frame_height/2）加上分隔线的x坐标
            start=UP * config.frame_height / 2 + RIGHT * self.divider_x,
            # 终点：屏幕底部（DOWN * frame_height/2）加上分隔线的x坐标
            end=DOWN * config.frame_height / 2 + RIGHT * self.divider_x,
            # 线条宽度：2像素
            stroke_width=2,
            # 线条颜色：灰色
            color=GRAY
        )
        # 将分隔线添加到场景中
        self.add(line)

        # 步骤3：创建讲义笔记（左侧区域）
        # 创建一个VGroup来包含所有笔记文本对象
        self.notes_group = VGroup()
        # 遍历所有笔记文本
        for i, note in enumerate(lecture_notes):
            # 如果文本过长则自动换行
            # 创建文本对象：24号字体，白色，斜体样式
            text = Text(note, font_size=24, color=WHITE, slant=ITALIC)
            
            # 智能缩放逻辑：只有当文本宽度超过左侧区域限制(4.0)时才缩小
            # 否则保持原样（避免短文本被拉伸得巨大）
            max_width = 4.0
            if text.width > max_width:
                text.scale(max_width / text.width)
                
            # 将文本对象添加到笔记组中
            self.notes_group.add(text)
        
        # 将笔记组垂直排列，左对齐，元素间距0.5单位
        self.notes_group.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        # 将笔记组放置在标题下方，距离标题1.0单位，左对齐
        self.notes_group.next_to(self.title, DOWN, buff=1.0, aligned_edge=LEFT)
        # 确保笔记组位于分隔线左侧
        # 计算左侧区域的中心x坐标：分隔线x坐标和屏幕左边缘的中点
        self.notes_group.set_x((self.divider_x - config.frame_width/2) / 2)
        
        # 将笔记组添加到场景中
        self.add(self.notes_group)

        # 步骤4：定义网格区域（右侧区域）
        # 网格区域范围：从x = -2.0到x = 7.1（屏幕右边缘），y从-3.5到3.5
        # 网格左边界：分隔线右侧0.5单位
        self.grid_x_min = self.divider_x + 0.5
        # 网格右边界：屏幕右边缘左侧0.5单位（留出边距）
        self.grid_x_max = config.frame_width / 2 - 0.5
        # 网格下边界：y = -3.5
        self.grid_y_min = -3.5
        # 网格上边界：y = 3.5
        self.grid_y_max = 3.5
        
        # 计算网格的总宽度和总高度
        self.grid_width = self.grid_x_max - self.grid_x_min
        self.grid_height = self.grid_y_max - self.grid_y_min
        
        # 定义10x10网格系统
        # 列数：10列（从左到右编号1-10）
        self.cols = 10
        # 行数：10行（从上到下编号A-J）
        self.rows = 10
        # 计算每个网格单元的宽度（网格总宽度除以列数）
        self.cell_width = self.grid_width / self.cols
        # 计算每个网格单元的高度（网格总高度除以行数）
        self.cell_height = self.grid_height / self.rows

    def get_grid_point(self, grid_pos):
        """
        将网格位置字符串转换为实际坐标点
        
        功能说明：
        将类似'A1'、'C3'、'J10'这样的网格位置字符串转换为场景中的实际坐标点。
        返回的坐标点是该网格单元的中心点。
        
        参数:
            grid_pos (str): 网格位置字符串
                - 格式：行字母 + 列数字
                - 行：A（顶部）到J（底部），共10行
                - 列：1（左侧）到10（右侧），共10列
                - 示例：'A1'（左上角）、'J10'（右下角）、'C5'（中间偏上）
        
        返回:
            np.array: 三维坐标点数组 [x, y, 0]，表示网格单元的中心坐标
        
        错误处理:
            - 如果位置字符串格式无效，返回原点(0, 0, 0)并打印警告
            - 如果位置超出网格范围，返回原点(0, 0, 0)并打印警告
        
        坐标计算原理:
            - X坐标：网格左边界 + (列索引 + 0.5) * 单元宽度
            - Y坐标：网格上边界 - (行索引 + 0.5) * 单元高度
            - 注意：Y轴向上增长，所以行A（索引0）在顶部
        """
        # 检查位置字符串长度，至少需要2个字符（1个字母+1个数字）
        if len(grid_pos) < 2:
            # 如果格式无效，返回原点
            return ORIGIN
            
        # 提取行字母并转换为大写（确保大小写不敏感）
        row_char = grid_pos[0].upper()
        # 处理多位数列号（例如'10'）
        try:
            # 将位置字符串的第二个字符开始的部分转换为整数（列号）
            col_num = int(grid_pos[1:])
        except ValueError:
            # 如果转换失败（不是有效数字），打印警告并返回原点
            print(f"Warning: Invalid grid column in {grid_pos}")
            return ORIGIN
        
        # 将行字母映射到索引0-9
        # ord('A') = 65, ord('B') = 66, ..., ord('J') = 74
        # 所以 'A' -> 0, 'B' -> 1, ..., 'J' -> 9
        row_idx = ord(row_char) - ord('A')
        # 将列号转换为索引（列号从1开始，索引从0开始）
        col_idx = col_num - 1
        
        # 验证索引是否在有效范围内
        if not (0 <= row_idx < self.rows and 0 <= col_idx < self.cols):
            # 如果超出范围，打印警告并返回原点
            print(f"Warning: Invalid grid position {grid_pos}")
            return ORIGIN

        # 计算网格单元的中心坐标
        # Y轴向上增长，所以行A（索引0）在顶部（y_max）
        # y坐标 = 网格上边界 - (行索引 + 0.5) * 单元高度
        # X坐标 = 网格左边界 + (列索引 + 0.5) * 单元宽度
        x = self.grid_x_min + (col_idx + 0.5) * self.cell_width
        y = self.grid_y_max - (row_idx + 0.5) * self.cell_height
        
        # 返回三维坐标点（z坐标始终为0，因为这是2D场景）
        return np.array([x, y, 0])

    # ========================================================================
    # LLM兼容性别名方法
    # ========================================================================
    # 这些方法是get_grid_point()的别名，用于提高LLM代码生成的成功率
    # LLM可能会使用不同的方法名，这些别名确保无论使用哪个名称都能正常工作
    
    def grid_to_coords(self, grid_pos):
        """
        网格位置转坐标的别名方法（LLM兼容性）
        
        参数:
            grid_pos (str): 网格位置字符串（如'A1'）
        
        返回:
            np.array: 坐标点
        """
        return self.get_grid_point(grid_pos)
        
    def grid_anchor(self, grid_pos):
        """
        网格锚点的别名方法（LLM兼容性）
        
        参数:
            grid_pos (str): 网格位置字符串（如'A1'）
        
        返回:
            np.array: 坐标点
        """
        return self.get_grid_point(grid_pos)

    def get_grid_position(self, grid_pos):
        """
        获取网格位置的别名方法（LLM兼容性）
        
        参数:
            grid_pos (str): 网格位置字符串（如'A1'）
        
        返回:
            np.array: 坐标点
        """
        return self.get_grid_point(grid_pos)

    @property
    def grid(self):
        """
        返回表示网格区域的矩形对象（属性方法）
        
        功能说明：
        本方法返回一个Rectangle对象，其大小和位置与网格区域完全匹配。
        这对于LLM生成的代码很有用，因为LLM可能会尝试访问self.grid.get_corner()等方法。
        
        返回:
            Rectangle: 一个矩形对象，表示整个网格区域
                - 宽度：网格总宽度
                - 高度：网格总高度
                - 位置：网格区域的中心点
        
        使用场景:
            - LLM可能使用self.grid.get_corner(UL)来获取网格的角落位置
            - 可以用于调试，可视化网格边界
            - 可以用于计算相对于网格的位置
        
        注意:
            这是一个@property装饰器方法，可以像属性一样访问：self.grid
            每次访问都会创建一个新的Rectangle对象
        """
        # 创建一个矩形，宽度和高度与网格区域相同
        rect = Rectangle(width=self.grid_width, height=self.grid_height)
        # 计算网格区域的中心点坐标
        center_x = (self.grid_x_min + self.grid_x_max) / 2
        center_y = (self.grid_y_min + self.grid_y_max) / 2
        # 将矩形移动到网格区域的中心
        rect.move_to(np.array([center_x, center_y, 0]))
        # 返回矩形对象
        return rect

    def place_at_grid(self, mobject, grid_pos, scale_factor=1.0, **kwargs):
        """
        将对象放置在指定网格单元的中心
        
        功能说明：
        本方法将给定的Mobject（Manim对象）移动到指定网格位置的中心点，
        并可选择性地缩放对象。适用于放置单个小对象（如点、小标签等）。
        
        参数:
            mobject (Mobject): 要放置的Manim对象（如Circle、Text、VGroup等）
            grid_pos (str): 网格位置字符串（如'A1'、'C5'、'J10'）
            scale_factor (float, 可选): 缩放因子
                - 1.0: 不缩放（默认）
                - >1.0: 放大
                - <1.0: 缩小
            **kwargs: 其他关键字参数
                - width: 尝试设置对象宽度（如果对象支持）
                - height: 尝试设置对象高度（如果对象支持）
        
        返回:
            Mobject: 处理后的对象（已移动和缩放）
        
        使用示例:
            circle = Circle()
            self.place_at_grid(circle, 'C5', scale_factor=0.8)
            self.play(Create(circle))
        
        注意:
            - 本方法只负责定位和缩放，不将对象添加到场景中
            - 通常需要在后续使用self.play()或self.add()来显示对象
            - 对于较大的对象或对象组，建议使用place_in_area()方法
        """
        # 获取网格位置对应的坐标点
        point = self.get_grid_point(grid_pos)
        # 将对象移动到该坐标点
        mobject.move_to(point)
        # 如果缩放因子不是1.0，则应用缩放
        if scale_factor != 1.0:
            mobject.scale(scale_factor)
        
        # 处理LLM常见的尺寸设置尝试
        # 有些对象可能不支持直接设置width/height属性，使用try-except避免错误
        if 'width' in kwargs:
            try:
                # 尝试设置对象宽度
                mobject.width = kwargs['width']
            except: 
                # 如果设置失败，静默忽略（对象可能不支持此属性）
                pass
        if 'height' in kwargs:
            try:
                # 尝试设置对象高度
                mobject.height = kwargs['height']
            except: 
                # 如果设置失败，静默忽略（对象可能不支持此属性）
                pass
            
        # 注意：通常动画会添加对象，所以这个辅助方法只负责定位
        # self.add(mobject) # Usually the animation adds it, but this helper just positions it.
        # 返回处理后的对象（允许链式调用）
        return mobject

    def place_in_area(self, mobject, top_left_pos, bottom_right_pos, scale_factor=1.0):
        """
        将对象放置在由两个网格点定义的矩形区域的中心
        
        功能说明：
        本方法将对象放置在指定矩形区域的中心，并自动缩放对象以适应区域大小。
        这是放置较大对象或对象组的推荐方法，因为它能确保对象不会超出指定区域。
        
        参数:
            mobject (Mobject): 要放置的Manim对象（可以是单个对象或VGroup）
            top_left_pos (str): 矩形区域左上角的网格位置（如'A1'）
            bottom_right_pos (str): 矩形区域右下角的网格位置（如'C3'）
            scale_factor (float, 可选): 用户指定的缩放因子
                - 1.0: 不额外缩放（默认）
                - >1.0: 放大（但不会超过区域大小）
                - <1.0: 缩小
        
        返回:
            Mobject: 处理后的对象（已移动和缩放）
        
        缩放逻辑:
            1. 计算区域可用尺寸（留10%边距）
            2. 如果对象太大，自动缩小以适应区域
            3. 应用用户指定的scale_factor（但不会超过适应尺寸）
            4. 使用较小的缩放比例确保同时适应宽度和高度
        
        使用示例:
            # 将一个大三角形放置在A1到C3的区域中
            triangle = Polygon(...)
            self.place_in_area(triangle, 'A1', 'C3', scale_factor=0.8)
            self.play(Create(triangle))
        
        注意:
            - 这是放置复杂几何图形和对象组的推荐方法
            - 自动缩放确保对象不会超出指定区域
            - 对于单个小对象，可以使用place_at_grid()方法
        """
        # 获取两个网格位置对应的坐标点
        p1 = self.get_grid_point(top_left_pos)
        p2 = self.get_grid_point(bottom_right_pos)
        
        # 计算矩形区域的中心点（两个点的中点）
        center = (p1 + p2) / 2
        # 将对象移动到中心点
        mobject.move_to(center)
        
        # 计算可用尺寸
        # 两个中心点之间的距离是(列数-1)*单元宽度，所以需要加上1个单元宽度来获得完整的边到边尺寸
        available_width = abs(p1[0] - p2[0]) + self.cell_width
        available_height = abs(p1[1] - p2[1]) + self.cell_height
        
        # 应用边距（10%），避免对象紧贴区域边缘
        max_width = available_width * 0.9
        max_height = available_height * 0.9
        
        # 检查是否需要缩放
        # 获取对象的当前宽度和高度
        current_width = mobject.width
        current_height = mobject.height
        
        # 计算适应区域所需的缩放比例
        # 如果宽度或高度为0，则缩放比例为1（不缩放）
        width_scale = max_width / current_width if current_width > 0 else 1
        height_scale = max_height / current_height if current_height > 0 else 1
        
        # 使用较小的缩放比例，确保对象同时适应宽度和高度
        # 这样可以保证对象不会超出区域的任何一边
        fit_scale = min(width_scale, height_scale)
        
        # 如果对象太大，需要缩小它
        # 如果对象较小，我们尊重用户指定的scale_factor，除非用户想要它比区域还大
        # 策略：先应用用户的scale_factor，然后限制在适应尺寸内
        
        # 初始化最终缩放比例为用户指定的值
        final_scale = scale_factor
        
        # 如果应用scale_factor会使对象超出区域，则减小缩放比例
        if fit_scale < 1.0:
             # 如果对象需要缩小以适应区域
             # 如果用户的scale_factor会使对象更小，则使用用户的scale_factor
             # 否则，限制在适应尺寸内
             if scale_factor * fit_scale < fit_scale:
                 # 用户想要对象很小
                 final_scale = scale_factor # User wants it tiny
             else:
                 # 限制在适应尺寸内
                 final_scale = fit_scale # Cap at fit size
        
        # 应用最终计算的缩放比例
        mobject.scale(final_scale)
            
        # 返回处理后的对象
        return mobject

    def add_side_label(self, line_or_polygon, side_index_or_direction, label_text, color=WHITE, font_size=36, buff=0.2):
        """
        为几何图形的边添加标签（自动定位，不受 place_at_grid 影响）
        
        参数:
            line_or_polygon: Line 对象或 Polygon 对象
            side_index_or_direction: 
                - 如果是 Line，则为方向 (UP/DOWN/LEFT/RIGHT)
                - 如果是 Polygon，则为边的索引 (0, 1, 2, ...)
            label_text: 标签文本（如 "a", "b", "c"）
            color: 标签颜色
            font_size: 字号
            buff: 标签与边的距离
        
        返回:
            MathTex: 标签对象（已定位，可直接 play(Write(...))）
        """
        label = MathTex(label_text, color=color, font_size=font_size)
        
        if hasattr(line_or_polygon, 'get_vertices'):
            # 这是一个 Polygon
            vertices = line_or_polygon.get_vertices()
            n = len(vertices)
            idx = side_index_or_direction % n
            start = vertices[idx]
            end = vertices[(idx + 1) % n]
            mid = (start + end) / 2
            # 计算法向量（垂直于边，指向外侧）
            edge_vec = end - start
            normal = np.array([-edge_vec[1], edge_vec[0], 0])
            normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else UP
            label.move_to(mid + normal * buff)
        else:
            # 这是一个 Line
            label.next_to(line_or_polygon, side_index_or_direction, buff=buff)
        
        return label

    def add_vertex_label(self, polygon, vertex_index, label_text, color=WHITE, font_size=36, buff=0.3):
        """
        为多边形的顶点添加标签
        
        参数:
            polygon: Polygon 对象
            vertex_index: 顶点索引 (0, 1, 2, ...)
            label_text: 标签文本（如 "A", "B", "C"）
            color: 标签颜色
            font_size: 字号
            buff: 标签与顶点的距离
        
        返回:
            MathTex: 标签对象
        """
        label = MathTex(label_text, color=color, font_size=font_size)
        vertices = polygon.get_vertices()
        n = len(vertices)
        idx = vertex_index % n
        vertex = vertices[idx]
        
        # 计算从多边形中心指向顶点的方向
        center = polygon.get_center()
        direction = vertex - center
        direction = direction / np.linalg.norm(direction) if np.linalg.norm(direction) > 0 else UP
        
        label.move_to(vertex + direction * buff)
        return label

    def add_right_angle_mark(self, polygon, vertex_index, size=0.3, color=WHITE):
        """
        在多边形的指定顶点处添加直角标记
        
        参数:
            polygon: Polygon 对象
            vertex_index: 直角所在的顶点索引
            size: 直角标记的大小
            color: 颜色
        
        返回:
            VGroup: 直角标记对象
        """
        vertices = polygon.get_vertices()
        n = len(vertices)
        idx = vertex_index % n
        
        # 获取直角顶点和相邻两点
        vertex = vertices[idx]
        prev_vertex = vertices[(idx - 1) % n]
        next_vertex = vertices[(idx + 1) % n]
        
        # 计算两条边的单位向量
        v1 = prev_vertex - vertex
        v1 = v1 / np.linalg.norm(v1) if np.linalg.norm(v1) > 0 else RIGHT
        v2 = next_vertex - vertex
        v2 = v2 / np.linalg.norm(v2) if np.linalg.norm(v2) > 0 else UP
        
        # 构建直角标记的三个点
        p1 = vertex + v1 * size
        p2 = vertex + v1 * size + v2 * size
        p3 = vertex + v2 * size
        
        mark = VGroup(
            Line(p1, p2, color=color, stroke_width=2),
            Line(p2, p3, color=color, stroke_width=2)
        )
        return mark

    def fit_to_screen(self, mobject, margin=0.5):
        """
        确保对象适合网格区域（屏幕右侧）
        
        功能说明：
        本方法检查对象是否超出网格区域，如果超出则自动缩放以适合区域。
        这是一个安全方法，适用于不确定对象大小的场景。
        
        参数:
            mobject (Mobject): 要调整的Manim对象
            margin (float, 可选): 边距大小（单位）
                - 默认0.5单位，在对象和区域边界之间留出空间
                - 可以调整以控制对象与边界的距离
        
        返回:
            Mobject: 调整后的对象（如果超出则已缩放）
        
        缩放逻辑:
            - 如果对象宽度超出，按宽度比例缩放
            - 如果对象高度超出，按高度比例缩放
            - 如果同时超出，会应用两次缩放（可能不是最优，但确保适合）
        
        使用场景:
            - 不确定对象大小时的安全措施
            - 动态生成的对象，大小未知
            - 作为place_in_area()的补充或替代
        
        注意:
            - 本方法只缩放，不移动对象位置
            - 如果对象已经适合区域，不会进行任何操作
            - 建议在定位对象之前或之后调用此方法
        """
        # 计算网格区域的最大可用尺寸（减去边距）
        max_w = self.grid_width - margin
        max_h = self.grid_height - margin
        
        # 如果对象宽度超出最大宽度，按比例缩放
        if mobject.width > max_w:
            mobject.scale(max_w / mobject.width)
        
        # 如果对象高度超出最大高度，按比例缩放
        if mobject.height > max_h:
            mobject.scale(max_h / mobject.height)
            
        # 可选：如果对象位置偏离太远，可以将其居中到网格
        # 但这可能会干扰预期的位置，所以注释掉了
        # Ensure it's centered in the grid if it's way off
        # (Optional, might disturb intended position)
        
        # 返回调整后的对象
        return mobject

    def highlight_line(self, line_index, color=YELLOW):
        """
        高亮显示讲义笔记中的特定行
        
        功能说明：
        本方法将指定索引的讲义笔记行改变颜色，用于在动画过程中突出显示当前讲解的内容。
        这是一个简单的视觉提示，帮助观众跟随讲解进度。
        
        参数:
            line_index (int): 要高亮的行索引（从0开始）
                - 0: 第一行笔记
                - 1: 第二行笔记
                - 以此类推
            color (str/Color, 可选): 高亮颜色
                - 默认：YELLOW（黄色）
                - 可以使用任何Manim支持的颜色（如RED、BLUE、GREEN等）
        
        使用示例:
            # 在讲解第一步时高亮第一行笔记
            self.highlight_line(0, color=YELLOW)
            # 执行相应的动画
            self.play(Create(circle))
            # 在讲解第二步时高亮第二行笔记
            self.highlight_line(1, color=YELLOW)
        
        注意:
            - 如果索引超出范围，方法不会执行任何操作（静默失败）
            - 高亮动画持续0.5秒
            - 高亮是永久性的，直到场景结束或手动改变颜色
        """
        # 检查索引是否在有效范围内
        if 0 <= line_index < len(self.notes_group):
            # 播放动画：将指定行的颜色改变为高亮颜色
            # animate.set_color()是Manim的动画语法，用于平滑改变颜色
            # run_time=0.5表示动画持续0.5秒
            self.play(self.notes_group[line_index].animate.set_color(color), run_time=0.5)

    def debug_grid(self):
        """
        绘制网格用于调试目的
        
        功能说明：
        本方法在场景中绘制完整的10x10网格，包括每个单元的边框和位置标签。
        这对于调试和可视化网格系统非常有用，可以帮助理解对象应该放置在哪个位置。
        
        绘制内容:
            - 每个网格单元：蓝色半透明矩形边框
            - 每个网格位置：位置标签（如'A1'、'B2'等），蓝色文字
        
        使用场景:
            - 开发时可视化网格布局
            - 调试对象位置问题
            - 理解网格系统的工作原理
        
        注意:
            - 这会添加大量对象到场景中，可能影响性能
            - 建议只在调试时使用，正式渲染时移除
            - 网格线是半透明的，不会完全遮挡内容
        
        使用示例:
            class MyScene(TeachingScene):
                def construct(self):
                    self.setup_layout("标题", ["笔记1", "笔记2"])
                    # 显示网格用于调试
                    self.debug_grid()
                    # 然后正常创建动画...
        """
        # 创建一个VGroup来包含所有网格调试元素
        grid_group = VGroup()
        # 遍历所有行（0到9，对应A到J）
        for r in range(self.rows):
            # 遍历所有列（0到9，对应1到10）
            for c in range(self.cols):
                # 将行索引转换为字母（0->'A', 1->'B', ..., 9->'J'）
                row_char = chr(ord('A') + r)
                # 将列索引转换为数字字符串（0->'1', 1->'2', ..., 9->'10'）
                col_char = str(c + 1)
                # 组合成位置字符串（如'A1'、'B2'等）
                pos_str = f"{row_char}{col_char}"
                # 获取该位置的坐标点
                point = self.get_grid_point(pos_str)
                
                # 创建网格单元的矩形边框
                rect = Rectangle(width=self.cell_width, height=self.cell_height)
                # 将矩形移动到网格单元的中心
                rect.move_to(point)
                # 设置矩形边框样式：蓝色，宽度1，透明度0.3（半透明）
                rect.set_stroke(color=BLUE, width=1, opacity=0.3)
                
                # 创建位置标签文本
                label = Text(pos_str, font_size=12, color=BLUE_A)
                # 将标签移动到网格单元的中心
                label.move_to(point)
                
                # 将矩形和标签添加到网格组中
                grid_group.add(rect, label)
        
        # 将整个网格组添加到场景中（立即显示）
        self.add(grid_group)

# ============================================================================
# 猴子补丁：修复LLM常见的幻觉方法
# ============================================================================
# LLM可能会生成一些Manim中不存在但逻辑上合理的方法调用
# 这些补丁为VGroup添加了常用的排列方法，提高代码生成的成功率

# 检查VGroup是否已经有arrange_in_circle方法
if not hasattr(VGroup, "arrange_in_circle"):
    def arrange_in_circle(self, radius=1, **kwargs):
        """
        将VGroup中的对象排列成圆形
        
        功能说明：
        本方法将VGroup中的所有子对象均匀地排列在一个圆周上。
        这是LLM经常尝试使用的方法，但Manim默认不提供，所以通过猴子补丁添加。
        
        参数:
            self (VGroup): VGroup实例（包含要排列的对象）
            radius (float, 可选): 圆的半径，默认1.0
            **kwargs: 其他关键字参数（当前未使用，保留用于未来扩展）
        
        返回:
            VGroup: 排列后的VGroup（允许链式调用）
        
        排列逻辑:
            - 计算每个对象之间的角度间隔：2π / 对象数量
            - 将每个对象放置在圆周上的对应位置
            - 第一个对象在角度0（右侧），按逆时针方向排列
        
        使用示例:
            dots = VGroup(*[Dot() for _ in range(8)])
            dots.arrange_in_circle(radius=2)
            self.play(Create(dots))
        """
        # 如果VGroup为空（没有子对象），直接返回
        if not self.submobjects:
            return self
        # 遍历所有子对象
        for i, mob in enumerate(self.submobjects):
            # 计算当前对象应该放置的角度
            # TAU = 2π，将圆周等分为对象数量份
            angle = i * TAU / len(self.submobjects)
            # 计算对象在圆周上的坐标
            # 使用极坐标转直角坐标：x = r*cos(θ), y = r*sin(θ)
            mob.move_to(radius * np.array([np.cos(angle), np.sin(angle), 0]))
        # 返回VGroup自身（允许链式调用）
        return self
    # 将方法添加到VGroup类中（猴子补丁）
    VGroup.arrange_in_circle = arrange_in_circle

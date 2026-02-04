# 首先导入 TeachingScene 以确保环境补丁工作 (例如 LaTeX 回退)
from src.manim_base import TeachingScene
from manim import *

class Section1Scene(TeachingScene):
    def construct(self):
        # 数据
        lines = ['这是直角三角形', '有一个90度角', '三条边各有名称']
        
        # 设置
        self.setup_layout("引入直角三角形", lines)
        
        # 步骤 1: 这是直角三角形
        self.highlight_line(0)
        
        # 创建直角三角形 (3-4-5 比例，直角在左下方)
        # 顶点顺序: 左下(直角), 右下, 左上
        triangle = Polygon(
            ORIGIN,           # 左下角 (直角)
            3*RIGHT,          # 右下角
            4*UP,             # 左上角
            color=WHITE,
            stroke_width=3
        )
        
        # 放置三角形在右侧区域
        self.place_in_area(triangle, 'B2', 'I8')
        
        # 淡入三角形
        self.play(FadeIn(triangle))
        self.wait(1)
        
        # 步骤 2: 有一个90度角
        self.highlight_line(1)
        
        # 添加直角标记 (在顶点0处，即左下角)
        right_angle_mark = self.add_right_angle_mark(triangle, 0)
        self.play(Create(right_angle_mark))
        
        # 闪烁两次强调
        self.play(
            right_angle_mark.animate.set_color(YELLOW),
            rate_func=there_and_back,
            run_time=0.5
        )
        self.play(
            right_angle_mark.animate.set_color(YELLOW),
            rate_func=there_and_back,
            run_time=0.5
        )
        self.wait(1)
        
        # 步骤 3: 三条边各有名称
        self.highlight_line(2)
        
        # 获取三角形的三条边
        vertices = triangle.get_vertices()
        # 边0: 左下到右下 (底边，直角边 a)
        # 边1: 右下到左上 (斜边 c)
        # 边2: 左上到左下 (左边，直角边 b)
        
        # 创建边的线段用于变色
        side_a = Line(vertices[0], vertices[1], color=BLUE, stroke_width=4)  # 底边
        side_b = Line(vertices[2], vertices[0], color=BLUE, stroke_width=4)  # 左边
        side_c = Line(vertices[1], vertices[2], color=YELLOW, stroke_width=4)  # 斜边
        
        # 直角边 a 变蓝色并标注
        self.play(Create(side_a))
        label_a = self.add_side_label(triangle, 0, "a", color=BLUE)
        self.play(FadeIn(label_a))
        self.wait(0.5)
        
        # 直角边 b 变蓝色并标注
        self.play(Create(side_b))
        label_b = self.add_side_label(triangle, 2, "b", color=BLUE)
        self.play(FadeIn(label_b))
        self.wait(0.5)
        
        # 斜边 c 变黄色并标注
        self.play(Create(side_c))
        label_c = self.add_side_label(triangle, 1, "c", color=YELLOW)
        self.play(FadeIn(label_c))
        self.wait(1)
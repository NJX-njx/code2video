from src.manim_base import TeachingScene
from manim import *

class Section1Scene(TeachingScene):
    def construct(self):
        lines = ['直角三角形', '三边关系', '神秘规律']
        self.setup_layout("直角三角形登场", lines)

        # Step 1: 直角三角形淡入并闪烁两次
        self.highlight_line(0)
        # 使用 3-4-5 直角三角形，保持几何正确性
        triangle = Polygon(
            ORIGIN,
            3 * RIGHT,
            3 * RIGHT + 4 * UP,
            color=WHITE,
            fill_opacity=0,
            stroke_width=4
        )
        # 调整放置区域，避免越界和重叠
        self.place_in_area(triangle, 'B2', 'H7')
        self.play(FadeIn(triangle))
        self.wait(1)
        for _ in range(2):
            self.play(
                triangle.animate.set_fill(WHITE, opacity=0.3),
                rate_func=there_and_back,
                run_time=0.5
            )
        self.wait(1)

        # Step 2: 三边依次亮起并同步缩放
        self.highlight_line(1)
        side_AB = Line(
            triangle.get_vertices()[0],
            triangle.get_vertices()[1],
            color=RED,
            stroke_width=5
        )
        side_BC = Line(
            triangle.get_vertices()[1],
            triangle.get_vertices()[2],
            color=GREEN,
            stroke_width=5
        )
        side_CA = Line(
            triangle.get_vertices()[2],
            triangle.get_vertices()[0],
            color=BLUE,
            stroke_width=5
        )
        self.play(Create(side_AB), run_time=0.5)
        self.play(Create(side_BC), run_time=0.5)
        self.play(Create(side_CA), run_time=0.5)
        self.wait(0.5)
        group = VGroup(triangle, side_AB, side_BC, side_CA)
        # 微调缩放幅度，避免越界
        self.play(
            group.animate.scale(1.15),
            rate_func=there_and_back,
            run_time=1
        )
        self.wait(1)

        # Step 3: 三角形滑出，留下旋转问号
        self.highlight_line(2)
        # 滑出距离微调，确保完全离开可视区域
        self.play(group.animate.shift(7 * RIGHT), run_time=1)
        question = Text("?", font_size=110, color=WHITE)
        # 将问号放置在中心偏左，避免与右侧潜在内容重叠
        self.place_at_grid(question, 'D5')
        self.play(FadeIn(question))
        self.play(
            Rotate(question, angle=2 * PI),
            run_time=3,
            rate_func=linear
        )
        self.wait(1)
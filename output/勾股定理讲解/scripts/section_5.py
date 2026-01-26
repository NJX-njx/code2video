from src.manim_base import TeachingScene
from manim import *

class Section5Scene(TeachingScene):
    def construct(self):
        lines = ['勾股定理', '任意直角', '边长关系']
        self.setup_layout("定理总结", lines)

        # Step 1: 勾股定理 —— 中心淡入定理文字并放大
        self.highlight_line(0)
        theorem = Text("勾股定理", font_size=72, color=WHITE).set_stroke(BLACK, 4, background=True)
        self.place_in_area(theorem, 'D5', 'G6')
        self.play(FadeIn(theorem, scale=0.5), theorem.animate.scale(1.3))
        self.wait(1)

        # Step 2: 任意直角 —— 背景淡入多个不同比例浅色直角三角形环绕
        self.highlight_line(1)
        triangles = VGroup()
        # 3-4-5 直角三角形
        t1 = Polygon(
            ORIGIN, 2.4 * RIGHT, 2.4 * RIGHT + 3.2 * UP,
            color=BLUE, stroke_width=2, fill_opacity=0.15
        )
        # 6-8-10 直角三角形
        t2 = Polygon(
            ORIGIN, 3.6 * RIGHT, 3.6 * RIGHT + 4.8 * UP,
            color=GREEN, stroke_width=2, fill_opacity=0.15
        )
        # 5-12-13 直角三角形
        t3 = Polygon(
            ORIGIN, 3.0 * RIGHT, 3.0 * RIGHT + 7.2 * UP,
            color=YELLOW, stroke_width=2, fill_opacity=0.15
        )
        triangles.add(t1, t2, t3)
        # 分别旋转并放置到环绕位置
        t1.rotate(PI / 6).shift(2.5 * LEFT + 1.2 * DOWN)
        t2.rotate(-PI / 4).shift(4.5 * RIGHT + 0.5 * UP)
        t3.rotate(PI / 3).shift(1.5 * LEFT + 2.5 * UP)
        self.place_in_area(triangles, 'A1', 'J10')
        self.play(FadeIn(triangles, scale=0.7))
        self.wait(1)

        # Step 3: 边长关系 —— 所有图形同步闪烁后淡出，定理高亮停留
        self.highlight_line(2)
        self.play(
            *[
                Flash(tri, color=tri.get_color(), flash_radius=0.6, line_length=0.4)
                for tri in triangles
            ],
            Flash(theorem, color=WHITE, flash_radius=1.2, line_length=0.6),
            run_time=1.5
        )
        self.play(FadeOut(triangles))
        self.play(theorem.animate.set_color(YELLOW).scale(1.1))
        self.wait(1)
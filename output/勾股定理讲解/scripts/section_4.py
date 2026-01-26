from src.manim_base import TeachingScene
from manim import *

class Section4Scene(TeachingScene):
    def construct(self):
        lines = ['3-4-5', '9＋16', '25']
        self.setup_layout("数值验证", lines)

        # Step 1: 右侧淡入浅色3-4-5三角形
        self.highlight_line(0)
        triangle = Polygon(
            ORIGIN, 4 * RIGHT, 4 * RIGHT + 3 * UP,
            color=BLUE, fill_opacity=0.3, stroke_width=3
        )
        self.place_in_area(triangle, 'D2', 'H8')
        self.play(FadeIn(triangle))
        self.wait(1)

        # 直角符号
        right_angle = Square(side_length=0.3, stroke_width=2, color=WHITE)
        right_angle.move_to(triangle.get_vertices()[1] + 0.15 * UP + 0.15 * LEFT)
        right_angle.rotate(PI / 2, about_point=right_angle.get_corner(DL))
        self.play(FadeIn(right_angle), run_time=0.5)

        # Step 2: a²=9、b²=16两数滑入并相加
        self.highlight_line(1)
        a_sq = MathTex("9", color=WHITE)          # 高对比度
        b_sq = MathTex("16", color=WHITE)         # 高对比度
        plus = MathTex("+", color=WHITE)
        eq = MathTex("=", color=WHITE)
        sum_val = MathTex("25", color=YELLOW)

        a_sq.move_to(ORIGIN)
        b_sq.next_to(a_sq, RIGHT, buff=0.5)
        plus.next_to(a_sq, LEFT, buff=0.3)
        eq.next_to(b_sq, RIGHT, buff=0.3)
        sum_val.next_to(eq, RIGHT, buff=0.3)

        calc_group = VGroup(plus, a_sq, b_sq, eq, sum_val).scale(0.9)
        self.place_in_area(calc_group, 'B2', 'I4')

        self.play(
            a_sq.animate.shift(LEFT * 0.5),
            b_sq.animate.shift(RIGHT * 0.5),
            FadeIn(plus, shift=UP * 0.3),
            FadeIn(eq, shift=UP * 0.3),
            run_time=1
        )
        self.wait(1)

        # Step 3: 结果25滑向c²=25，等式闪烁确认
        self.highlight_line(2)
        c_sq_label = MathTex("c^2 = 25", color=YELLOW).scale(0.9)
        self.place_in_area(c_sq_label, 'F7', 'H8')   # 下移一格避免重叠

        self.play(sum_val.animate.move_to(c_sq_label.get_center()))
        self.wait(0.5)
        self.play(
            Flash(c_sq_label, color=YELLOW, flash_radius=0.6),
            c_sq_label.animate.set_color(YELLOW).scale(1.2),
            run_time=0.6
        )
        self.play(c_sq_label.animate.scale(1 / 1.2))
        self.wait(1)
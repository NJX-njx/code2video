from src.manim_base import TeachingScene
from manim import *

class Section3Scene(TeachingScene):
    def construct(self):
        lines = ['a²＋b²', '等于', 'c²']
        self.setup_layout("定理亮相", lines)

        # Step 1: a²、b²两方块靠拢并变色闪烁
        self.highlight_line(0)
        # Build squares at origin
        square_a = Square(side_length=1.8, color=BLUE, fill_opacity=0.6)
        square_b = Square(side_length=1.8, color=GREEN, fill_opacity=0.6)
        square_a.shift(LEFT * 2.3)
        square_b.shift(RIGHT * 2.3)
        group_ab = VGroup(square_a, square_b)
        self.place_in_area(group_ab, 'D1', 'G10')
        self.play(Create(group_ab))
        self.play(
            square_a.animate.shift(RIGHT * 2.3),
            square_b.animate.shift(LEFT * 2.3),
            run_time=1
        )
        self.play(
            square_a.animate.set_color(YELLOW),
            square_b.animate.set_color(YELLOW),
            Flash(square_a, color=YELLOW),
            Flash(square_b, color=YELLOW)
        )
        self.wait(1)

        # Step 2: 中间出现浅色加号并放大
        self.highlight_line(1)
        plus = MathTex("+", color=LIGHT_GREY)
        plus.scale(0.9)
        plus.move_to((square_a.get_right() + square_b.get_left()) / 2 + UP * 0.2)
        self.play(FadeIn(plus), plus.animate.scale(1.5), run_time=0.8)
        self.wait(1)

        # Step 3: c²方块淡入，整体等式居中高亮
        self.highlight_line(2)
        square_c = Square(side_length=1.8, color=RED, fill_opacity=0.6)
        square_c.next_to(group_ab, RIGHT, buff=1.2)
        self.play(FadeIn(square_c))
        full_eq = VGroup(square_a, plus, square_b, square_c)
        self.play(
            full_eq.animate.set_fill(opacity=1),
            full_eq.animate.set_stroke(width=4),
            run_time=1
        )
        self.play(Indicate(full_eq, color=WHITE, scale_factor=1.05))
        self.wait(1)
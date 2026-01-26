from src.manim_base import TeachingScene
from manim import *

class Section1Scene(TeachingScene):
    def construct(self):
        lines = ['直角三角形', '直角标记', '三边命名']
        self.setup_layout("直角三角形登场", lines)

        # Step 1: 直角三角形淡入
        self.highlight_line(0)
        # Build 3-4-5 right triangle at ORIGIN, right angle at C
        A = np.array([0, 0, 0])
        B = np.array([4, 0, 0])
        C = np.array([0, 3, 0])
        triangle = Polygon(A, B, C, color=LIGHT_GREY, stroke_width=4)
        # Labels
        label_A = MathTex("A").scale(0.8)
        label_B = MathTex("B").scale(0.8)
        label_C = MathTex("C").scale(0.8)
        label_A.next_to(A, DL, buff=0.1)
        label_B.next_to(B, DR, buff=0.1)
        label_C.next_to(C, UL, buff=0.1)
        tri_group = VGroup(triangle, label_A, label_B, label_C)
        self.place_in_area(tri_group, 'A1', 'J10')
        self.play(FadeIn(tri_group))
        self.wait(1)

        # Step 2: 直角标记闪烁
        self.highlight_line(1)
        # Small square at C, snugly fit inside the right angle
        size = 0.25
        corner = C
        square = Square(side_length=size, color=YELLOW, fill_opacity=0)
        square.move_to(corner + size/2 * (RIGHT + DOWN))
        self.play(Create(square))
        self.wait(0.2)
        self.play(square.animate.set_fill(YELLOW, opacity=1), run_time=0.3)
        self.play(square.animate.set_fill(YELLOW, opacity=0), run_time=0.3)
        self.play(square.animate.set_fill(YELLOW, opacity=1), run_time=0.3)
        self.play(square.animate.set_fill(YELLOW, opacity=0), run_time=0.3)
        self.wait(1)

        # Step 3: 斜边AB加粗变色，另两边标a、b
        self.highlight_line(2)
        # Highlight hypotenuse AB
        side_AB = Line(A, B, color=RED, stroke_width=8)
        self.play(Transform(triangle[0], triangle[0].copy().set_stroke(width=8).set_color(RED)), run_time=0.6)
        # Labels for legs
        label_a = MathTex("a").scale(0.8).set_color(BLUE)
        label_b = MathTex("b").scale(0.8).set_color(GREEN)
        label_a.move_to(Line(B, C).get_center() + 0.3 * UP)
        label_b.move_to(Line(A, C).get_center() + 0.3 * RIGHT)
        self.play(Write(label_a), Write(label_b))
        self.wait(1)
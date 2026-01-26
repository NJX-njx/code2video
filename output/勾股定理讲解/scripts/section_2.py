from src.manim_base import TeachingScene
from manim import *

class Section2Scene(TeachingScene):
    def construct(self):
        lines = ['正方形a²', '正方形b²', '正方形c²']
        self.setup_layout("面积拼图", lines)

        # Step 1: 正方形a²
        self.highlight_line(0)
        square_a = Square(side_length=1.5, color=BLUE, fill_opacity=0.3)
        square_a.scale(0.8)
        self.place_in_area(square_a, 'A1', 'D4')
        square_a.shift(LEFT * 4)
        self.play(square_a.animate.shift(RIGHT * 4).scale(1.25))
        self.wait(1)

        # Step 2: 正方形b²
        self.highlight_line(1)
        square_b = Square(side_length=1.5, color=GREEN, fill_opacity=0.3)
        square_b.scale(0.8)
        self.place_in_area(square_b, 'G1', 'J4')
        square_b.shift(RIGHT * 4)
        self.play(square_b.animate.shift(LEFT * 4).scale(1.25))
        self.wait(1)

        # Step 3: 正方形c²
        self.highlight_line(2)
        square_c = Square(side_length=1.5, color=RED, fill_opacity=0.3)
        square_c.scale(0.8)
        self.place_in_area(square_c, 'D7', 'G10')
        square_c.shift(DOWN * 3)
        self.play(square_c.animate.shift(UP * 3).scale(1.25))
        self.wait(1)
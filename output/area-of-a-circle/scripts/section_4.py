from src.manim_base import TeachingScene
from manim import *

class AreaFormulaScene(TeachingScene):
    def construct(self):
        lines = ['Area of rectangle?', 'Length times width.', 'πr times r.', 'Equals πr squared.']
        self.setup_layout("Area Formula", lines)

        # Step 1: Area of rectangle?
        self.highlight_line(0)
        rect = Rectangle(width=4, height=2, color=WHITE)
        self.place_in_area(rect, 'D1', 'G5')
        self.play(Create(rect))
        self.wait(1)

        # Rectangle interior flashes white once
        flash = rect.copy().set_fill(WHITE, opacity=1)
        self.play(FadeIn(flash, run_time=0.2), FadeOut(flash, run_time=0.2))
        self.wait(1)

        # Step 2: Length times width.
        self.highlight_line(1)
        label = MathTex(r"\text{Length} \times \text{Width}", color=WHITE)
        self.place_at_grid(label, 'E6')
        self.play(Write(label))
        self.wait(1)

        # Step 3: πr times r.
        self.highlight_line(2)
        formula = MathTex(r"\pi r \times r", color=TEAL)
        self.place_at_grid(formula, 'E7')
        self.play(Transform(label, formula))
        self.wait(1)

        # Step 4: Equals πr squared.
        self.highlight_line(3)
        final = MathTex(r"\pi r^2", color=WHITE).scale(1.5)
        self.place_at_grid(final, 'E8')
        self.play(Transform(label, final))
        self.wait(1)

        # Fade out rectangle, scale up formula
        self.play(FadeOut(rect), label.animate.scale(1.2))
        self.wait(1)
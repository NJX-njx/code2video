from src.manim_base import TeachingScene
from manim import *

class Section1Scene(TeachingScene):
    def construct(self):
        # Data
        lines = ['Triangle area equals half base times height.', 'Area = ½ × base × height.', 'Why half? Watch the rectangle split.']
        
        # Setup
        self.setup_layout("The Formula", lines)
        
        # Step 1
        self.highlight_line(0)
        formula = MathTex(r"\frac{1}{2} \times b \times h", font_size=96, color=WHITE)
        self.place_in_area(formula, 'D1', 'G4')
        self.play(FadeIn(formula))
        self.wait(1)
        
        # Step 2
        self.highlight_line(1)
        # Already showing the formula, just highlight 1/2
        half = formula[0][0:3]  # "\frac" "{1}" "{2}"
        self.play(
            half.animate.set_color(YELLOW),
            rate_func=there_and_back,
            run_time=1.5
        )
        self.wait(1)
        
        # Step 3
        self.highlight_line(2)
        # Build rectangle split into two right triangles at origin
        rect_width = 4
        rect_height = 3
        rectangle = Rectangle(width=rect_width, height=rect_height, color=WHITE)
        
        # Diagonal line from bottom-left to top-right
        diag = Line(
            rectangle.get_corner(DL),
            rectangle.get_corner(UR),
            color=WHITE
        )
        
        # Two right triangles
        triangle1 = Polygon(
            rectangle.get_corner(DL),
            rectangle.get_corner(UL),
            rectangle.get_corner(UR),
            color=BLUE,
            fill_opacity=0.3,
            stroke_width=2
        )
        triangle2 = Polygon(
            rectangle.get_corner(DL),
            rectangle.get_corner(DR),
            rectangle.get_corner(UR),
            color=GREEN,
            fill_opacity=0.3,
            stroke_width=2
        )
        
        # Group the shapes
        rect_group = VGroup(rectangle, diag, triangle1, triangle2)
        
        # Place the group in the right-side grid
        self.place_in_area(rect_group, 'D5', 'J9')
        
        # Animate creation
        self.play(Create(rectangle), Create(diag))
        self.play(Create(triangle1), Create(triangle2))
        self.wait(0.5)
        
        # Flash one triangle
        self.play(
            triangle1.animate.set_fill(YELLOW, opacity=0.7),
            rate_func=there_and_back,
            run_time=0.8
        )
        self.wait(1)
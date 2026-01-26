from src.manim_base import TeachingScene
from manim import *

class Section1Scene(TeachingScene):
    def construct(self):
        # Data
        lines = ['Start with a circle.', 'Mark the center.', 'Draw a radius.', 'Double it: diameter.']
        
        # Setup
        self.setup_layout("Radius & Diameter", lines)
        
        # Step 1: Start with a circle
        self.highlight_line(0)
        circle = Circle(stroke_width=2, color=WHITE)
        self.place_in_area(circle, 'C3', 'H8')
        self.play(FadeIn(circle))
        self.wait(1)
        
        # Step 2: Mark the center
        self.highlight_line(1)
        center_dot = Dot(color=TEAL)
        self.place_at_grid(center_dot, 'E6')
        self.play(Flash(center_dot, color=TEAL, num_flashes=2, flash_radius=0.3))
        self.wait(1)
        
        # Step 3: Draw a radius
        self.highlight_line(2)
        radius = Line(circle.get_center(), circle.get_right(), stroke_width=2, color=ManimColor("#FF00FF"))
        self.play(GrowFromCenter(radius))
        self.wait(1)
        
        # Step 4: Double it: diameter
        self.highlight_line(3)
        radius_copy = radius.copy()
        diameter = Line(circle.get_left(), circle.get_right(), stroke_width=2, color=ManimColor("#FF00FF"))
        self.play(
            Transform(radius_copy, diameter),
            radius.animate.set_color(YELLOW),
            run_time=1
        )
        self.play(
            Flash(radius, color=YELLOW, num_flashes=1, flash_radius=0.3),
            Flash(radius_copy, color=YELLOW, num_flashes=1, flash_radius=0.3)
        )
        self.wait(1)
from src.manim_base import TeachingScene
from manim import *

class ApproximateRectangle(TeachingScene):
    def construct(self):
        # Data
        lines = ['Edges become straighter.', 'Width equals radius.', 'Length: half circumference.', 'Shape morphs to rectangle.']
        
        # Setup
        self.setup_layout("Approximate Rectangle", lines)
        
        # Step 1: Edges become straighter
        self.highlight_line(0)
        # Create a jagged circle-like shape with straight edges
        radius = 2
        n_points = 8
        jagged_points = []
        for i in range(n_points):
            angle = i * TAU / n_points
            jagged_points.append(radius * np.array([np.cos(angle), np.sin(angle), 0]))
        jagged_shape = Polygon(*jagged_points, color=BLUE, stroke_width=2)
        self.place_in_area(jagged_shape, 'D1', 'G10')
        self.play(Create(jagged_shape))
        
        # Flash cyan twice
        for _ in range(2):
            self.play(jagged_shape.animate.set_color(PURE_CYAN), run_time=0.3)
            self.play(jagged_shape.animate.set_color(BLUE), run_time=0.3)
        
        # Smooth into straight lines (approximate rectangle)
        circle = Circle(radius=radius, color=BLUE, stroke_width=2)
        circle_points = []
        n_smooth = 64
        for i in range(n_smooth):
            angle = i * TAU / n_smooth
            circle_points.append(radius * np.array([np.cos(angle), np.sin(angle), 0]))
        smooth_poly = Polygon(*circle_points, color=BLUE, stroke_width=2)
        self.place_in_area(smooth_poly, 'D1', 'G10')
        self.play(Transform(jagged_shape, smooth_poly))
        self.wait(1)
        
        # Step 2: Width equals radius
        self.highlight_line(1)
        # Create a rectangle with width = radius, height = pi*radius (half circumference)
        rect = Rectangle(width=radius, height=PI*radius, color=BLUE, stroke_width=2)
        self.place_in_area(rect, 'D1', 'G10')
        self.play(Transform(jagged_shape, rect))
        
        # Label left edge as 'r'
        r_label = MathTex("r", color=WHITE)
        # Position label at left edge center
        label_pos = rect.get_left() + LEFT * 0.5
        r_label.move_to(label_pos)
        self.play(Write(r_label))
        self.wait(1)
        
        # Step 3: Length: half circumference
        self.highlight_line(2)
        # Label top edge as 'πr'
        pi_r_label = MathTex("\\pi r", color=WHITE)
        # Position label at top edge center
        label_pos_top = rect.get_top() + UP * 0.5
        pi_r_label.move_to(label_pos_top)
        self.play(Write(pi_r_label))
        self.wait(1)
        
        # Step 4: Shape morphs to rectangle
        self.highlight_line(3)
        # Scale slightly and make outline bold yellow
        final_rect = Rectangle(width=radius, height=PI*radius, color=YELLOW, stroke_width=6)
        self.place_in_area(final_rect, 'D1', 'G10')
        self.play(
            Transform(jagged_shape, final_rect),
            r_label.animate.set_color(YELLOW),
            pi_r_label.animate.set_color(YELLOW),
            run_time=1.5
        )
        self.wait(1)
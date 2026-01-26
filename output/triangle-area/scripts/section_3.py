from src.manim_base import TeachingScene
from manim import *

class Section3Scene(TeachingScene):
    def construct(self):
        # Data
        lines = ['Slide vertex parallel to base.', 'Area stays constant during slide.', 'Visual proof via rectangle halves.']
        
        # Setup
        self.setup_layout("Same Base, Same Height, Same Area", lines)
        
        # Step 1: Slide vertex parallel to base.
        self.highlight_line(0)
        
        # Build triangle at origin
        base_length = 4
        base = Line(ORIGIN, base_length * RIGHT, color=WHITE)
        vertex = Dot(base_length/2 * RIGHT + 2.5 * UP, color=YELLOW)
        triangle = Polygon(
            base.get_start(), base.get_end(), vertex.get_center(),
            color=BLUE, fill_opacity=0.3
        )
        
        # Group and place
        triangle_group = VGroup(base, triangle, vertex)
        self.place_in_area(triangle_group, 'D1', 'G10')
        
        # Draw fixed base
        self.play(Create(base))
        self.play(Create(triangle), Create(vertex))
        
        # Slide vertex horizontally
        trail = TracedPath(vertex.get_center, stroke_opacity=0.3, color=YELLOW)
        self.add(trail)
        
        vertex_target = Dot(vertex.get_center() + 3 * RIGHT, color=YELLOW)
        triangle_target = Polygon(
            base.get_start(), base.get_end(), vertex_target.get_center(),
            color=BLUE, fill_opacity=0.3
        )
        
        self.play(
            vertex.animate.move_to(vertex_target.get_center()),
            triangle.animate.become(triangle_target),
            run_time=2
        )
        self.wait(1)
        
        # Step 2: Area stays constant during slide.
        self.highlight_line(1)
        
        # Add area label
        area_label = MathTex(r"\frac{1}{2} b h", color=GREEN)
        self.place_at_grid(area_label, 'C5')
        self.play(Write(area_label))
        
        # Flash green once
        self.play(area_label.animate.set_color(GREEN_B), run_time=0.3)
        self.play(area_label.animate.set_color(GREEN), run_time=0.3)
        
        # Continue sliding to show area unchanged
        vertex_target2 = Dot(vertex.get_center() - 6 * RIGHT, color=YELLOW)
        triangle_target2 = Polygon(
            base.get_start(), base.get_end(), vertex_target2.get_center(),
            color=BLUE, fill_opacity=0.3
        )
        
        self.play(
            vertex.animate.move_to(vertex_target2.get_center()),
            triangle.animate.become(triangle_target2),
            run_time=2
        )
        self.wait(1)
        
        # Step 3: Visual proof via rectangle halves.
        self.highlight_line(2)
        
        # Show ghosted rectangles at positions
        positions = [vertex.get_center() + i * 1.5 * RIGHT for i in range(-2, 3)]
        
        for pos in positions:
            # Create rectangle with triangle as half
            rect = Rectangle(
                width=base_length, height=2.5,
                color=WHITE, stroke_opacity=0.3
            )
            rect.move_to(base.get_center() + 1.25 * UP)
            
            # Ghost rectangle
            rect.set_opacity(0.2)
            self.play(Create(rect), run_time=0.5)
            
            # Show triangle as half
            half_line = Line(
                base.get_start(), base.get_end() + 2.5 * UP,
                color=WHITE, stroke_opacity=0.3
            )
            half_line.move_to(base.get_center() + 1.25 * UP)
            self.play(Create(half_line), run_time=0.3)
            
            # Fade out
            self.play(FadeOut(rect), FadeOut(half_line), run_time=0.3)
        
        self.wait(1)
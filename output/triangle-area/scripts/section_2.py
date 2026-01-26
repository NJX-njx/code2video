from src.manim_base import TeachingScene
from manim import *

class Section2Scene(TeachingScene):
    def construct(self):
        # Data
        lines = ['Any side can be the base.', 'Rotate triangle; base label hops to new side.', 'Height always meets base at right angle.']
        
        # Setup
        self.setup_layout("Pick Any Side as Base", lines)
        
        # Step 1: Any side can be the base.
        self.highlight_line(0)
        
        # Build scalene triangle at origin
        A = np.array([0, 0, 0])
        B = np.array([4, 0, 0])
        C = np.array([2, 3, 0])
        
        triangle = Polygon(A, B, C, color=WHITE)
        
        # Create side labels
        label_ab = MathTex("AB").next_to(Line(A, B), DOWN, buff=0.2)
        label_bc = MathTex("BC").next_to(Line(B, C), RIGHT, buff=0.2)
        label_ca = MathTex("CA").next_to(Line(C, A), LEFT, buff=0.2)
        
        # Create base label
        base_label = Text("Base", color=YELLOW).next_to(Line(A, B), DOWN, buff=0.5)
        
        # Group triangle and labels
        triangle_group = VGroup(triangle, label_ab, label_bc, label_ca, base_label)
        
        # Place in right area
        self.place_in_area(triangle_group, 'C2', 'H8')
        
        # Show triangle and initial base label
        self.play(Create(triangle), Write(label_ab), Write(label_bc), Write(label_ca), Write(base_label))
        
        # Glow each side in turn
        for side in [Line(A, B), Line(B, C), Line(C, A)]:
            glow = side.copy().set_color(color=TEAL).set_stroke(width=8)
            self.play(Create(glow), run_time=0.8)
            self.play(FadeOut(glow), run_time=0.4)
        
        self.wait(1)
        
        # Step 2: Rotate triangle; base label hops to new side.
        self.highlight_line(1)
        
        # Rotate triangle and move base label to BC
        self.play(
            Rotate(triangle_group, angle=-120 * DEGREES, about_point=triangle.get_center()),
            base_label.animate.next_to(Line(B, C), RIGHT, buff=0.5)
        )
        self.wait(0.5)
        
        # Rotate triangle and move base label to CA
        self.play(
            Rotate(triangle_group, angle=-120 * DEGREES, about_point=triangle.get_center()),
            base_label.animate.next_to(Line(C, A), LEFT, buff=0.5)
        )
        self.wait(0.5)
        
        # Rotate triangle and move base label back to AB
        self.play(
            Rotate(triangle_group, angle=-120 * DEGREES, about_point=triangle.get_center()),
            base_label.animate.next_to(Line(A, B), DOWN, buff=0.5)
        )
        self.wait(1)
        
        # Step 3: Height always meets base at right angle.
        self.highlight_line(2)
        
        # Draw perpendicular from C to AB
        foot = np.array([2, 0, 0])
        height_line = DashedLine(C, foot, color=ManimColor('#FF00FF'))
        
        # Place height line
        self.place_at_grid(height_line, 'E5')
        
        self.play(Create(height_line))
        
        # Flash the height line
        for _ in range(3):
            self.play(height_line.animate.set_stroke(width=6), run_time=0.2)
            self.play(height_line.animate.set_stroke(width=2), run_time=0.2)
        
        self.wait(1)
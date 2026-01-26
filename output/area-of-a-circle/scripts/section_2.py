from src.manim_base import TeachingScene
from manim import *

class Section2Scene(TeachingScene):
    def construct(self):
        # Data
        lines = ['Slice circle like pizza.', 'Split into 8 wedges.', 'Fan wedges out.', 'Flip every other piece.']
        
        # Setup
        self.setup_layout("Cut & Rearrange", lines)
        
        # Step 1: Slice circle like pizza
        self.highlight_line(0)
        circle = Circle(fill_color=BLUE, fill_opacity=1, color=WHITE)
        self.place_in_area(circle, 'D2', 'H8')
        self.play(Create(circle))
        
        # Create 8 radial lines (pizza cuts)
        cuts = VGroup()
        for i in range(8):
            angle = i * PI / 4
            line = Line(ORIGIN, 3 * UR).rotate(angle, about_point=ORIGIN)
            cuts.add(line)
        
        self.play(*[Create(c) for c in cuts])
        self.wait(1)
        
        # Step 2: Split into 8 wedges
        self.highlight_line(1)
        wedges = VGroup()
        for i in range(8):
            start_angle = i * PI / 4
            end_angle = (i + 1) * PI / 4
            wedge = Sector(
                radius=3,
                start_angle=start_angle,
                angle=PI/4,
                fill_color=BLUE,
                fill_opacity=1,
                stroke_color=WHITE,
                stroke_width=2
            )
            wedges.add(wedge)
        
        self.play(FadeOut(circle), FadeOut(cuts))
        for wedge in wedges:
            self.place_in_area(wedge, 'D2', 'H8')
        self.play(*[FadeIn(w) for w in wedges])
        self.wait(1)
        
        # Step 3: Fan wedges out
        self.highlight_line(2)
        # Rotate each wedge outward
        fan_animations = []
        for i, wedge in enumerate(wedges):
            # Rotate around origin while shifting outward
            angle = (i - 3.5) * 0.2  # Spread factor
            fan_animations.append(
                wedge.animate.rotate(angle, about_point=ORIGIN).shift(angle * 0.3 * UP)
            )
        self.play(*fan_animations)
        self.wait(1)
        
        # Step 4: Flip every other piece
        self.highlight_line(3)
        flip_animations = []
        for i, wedge in enumerate(wedges):
            if i % 2 == 1:  # Flip odd-indexed wedges
                # Flip 180 degrees around radial axis
                axis = np.array([np.cos(i * PI / 4), np.sin(i * PI / 4), 0])
                flip_animations.append(
                    wedge.animate.rotate(PI, axis=axis)
                )
        self.play(*flip_animations)
        
        # Interlock into jagged rectangle
        # Shift wedges to form rectangular outline
        target_positions = []
        for i in range(8):
            x = (i - 3.5) * 0.6
            y = 0 if i % 2 == 0 else 0.5
            target_positions.append(np.array([x, y, 0]))
        
        shift_animations = []
        for wedge, pos in zip(wedges, target_positions):
            shift_animations.append(wedge.animate.move_to(pos))
        
        self.play(*shift_animations)
        self.wait(1)
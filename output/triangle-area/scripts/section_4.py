from src.manim_base import TeachingScene
from manim import *

class Section4Scene(TeachingScene):
    def construct(self):
        # Data
        lines = ['Base 6, height 4: area 12.', 'Base 10, height 5: area 25.', 'Right triangle legs 3-4: area 6.']
        
        # Setup
        self.setup_layout("Quick Examples", lines)
        
        # Step 1
        self.highlight_line(0)
        # Create triangle with base 6 and height 4
        triangle1 = Polygon(
            ORIGIN, 
            6 * RIGHT, 
            6 * RIGHT + 4 * UP,
            color=BLUE
        )
        # Labels
        base_label1 = MathTex("6").set_color(YELLOW)
        height_label1 = MathTex("4").set_color(YELLOW)
        area_label1 = MathTex("12").set_color(GREEN).scale(1.5)
        
        # Position labels
        base_label1.next_to(triangle1.get_bottom(), DOWN, buff=0.2)
        height_label1.next_to(triangle1.get_right(), RIGHT, buff=0.2)
        
        # Group and place
        group1 = VGroup(triangle1, base_label1, height_label1)
        self.place_in_area(group1, 'C2', 'H8')
        self.play(Create(triangle1))
        self.play(
            base_label1.animate.shift(LEFT * 3),
            height_label1.animate.shift(UP * 2)
        )
        # Place area label at center
        self.place_at_grid(area_label1, 'E5', scale_factor=0.8)
        self.play(area_label1.animate.scale(2), run_time=0.5)
        self.wait(1)
        
        # Step 2
        self.highlight_line(1)
        # Fade out previous
        self.play(FadeOut(group1), FadeOut(area_label1))
        
        # New triangle base 10 height 5
        triangle2 = Polygon(
            ORIGIN,
            10 * RIGHT,
            10 * RIGHT + 5 * UP,
            color=BLUE
        )
        base_label2 = MathTex("10").set_color(YELLOW)
        height_label2 = MathTex("5").set_color(YELLOW)
        area_label2 = MathTex("25").set_color(GREEN).scale(1.5)
        
        base_label2.next_to(triangle2.get_bottom(), DOWN, buff=0.2)
        height_label2.next_to(triangle2.get_right(), RIGHT, buff=0.2)
        
        group2 = VGroup(triangle2, base_label2, height_label2)
        self.place_in_area(group2, 'C2', 'H8')
        
        # Scale up animation
        triangle2.scale(0.1).move_to(ORIGIN)
        self.play(triangle2.animate.scale(10))
        self.play(FadeIn(base_label2), FadeIn(height_label2))
        
        # Pop area label
        self.place_at_grid(area_label2, 'E5', scale_factor=0.8)
        self.play(area_label2.animate.scale(2).set_stroke(width=4), run_time=0.5)
        self.wait(1)
        
        # Step 3
        self.highlight_line(2)
        self.play(FadeOut(group2), FadeOut(area_label2))
        
        # Right triangle legs 3-4
        right_triangle = Polygon(
            ORIGIN,
            4 * RIGHT,
            4 * RIGHT + 3 * UP,
            color=BLUE
        )
        
        # Labels for legs
        leg3_label = MathTex("3").set_color(YELLOW)
        leg4_label = MathTex("4").set_color(YELLOW)
        leg3_label.next_to(right_triangle.get_right(), RIGHT, buff=0.2)
        leg4_label.next_to(right_triangle.get_bottom(), DOWN, buff=0.2)
        
        # Copy and rotate to form rectangle
        copy_triangle = right_triangle.copy().set_color(RED)
        copy_triangle.rotate_about_origin(-PI)
        
        # Rectangle formed
        rectangle = VGroup(right_triangle, copy_triangle)
        
        # Area label
        area_label3 = MathTex("6").set_color(GREEN).scale(1.5)
        
        # Place initial triangle
        self.place_in_area(VGroup(right_triangle, leg3_label, leg4_label), 'C2', 'H8')
        self.play(Create(right_triangle))
        self.play(FadeIn(leg3_label), FadeIn(leg4_label))
        
        # Show copy forming rectangle
        self.place_in_area(rectangle, 'C2', 'H8')
        self.play(FadeIn(copy_triangle))
        
        # Flash half area
        half_rect = Rectangle(width=4, height=3, color=GREEN, fill_opacity=0.5)
        half_rect.move_to(right_triangle.get_center_of_mass())
        self.play(FadeIn(half_rect))
        self.play(Flash(half_rect.get_center()))
        
        # Show area 6
        self.place_at_grid(area_label3, 'E5', scale_factor=0.8)
        self.play(Write(area_label3))
        self.wait(1)
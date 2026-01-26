from src.manim_base import TeachingScene
from manim import *

class Section5Scene(TeachingScene):
    def construct(self):
        lines = ['勾股定理', 'a² + b² = c²', '永远成立']
        self.setup_layout("定理总结", lines)

        # Step 1: 勾股定理
        self.highlight_line(0)
        self.wait(1)

        # Step 2: 公式从中心缩放出现，白字加粗
        self.highlight_line(1)
        formula = MathTex("a^2 + b^2 = c^2", color=WHITE, font_size=64)
        formula.set_stroke(width=2)  # 加粗效果
        self.place_in_area(formula, 'E4', 'F7')
        self.play(ScaleInPlace(formula, scale_factor=1.3, rate_func=smooth))
        self.wait(1)

        # Step 3: 公式变色为金色并旋转一圈回正
        self.play(
            formula.animate.set_color(GOLD),
            Rotate(formula, angle=TAU, about_point=formula.get_center()),
            run_time=2
        )
        self.wait(1)

        # Step 4: “永远成立”淡入下方，整体渐隐结束
        self.highlight_line(2)
        always_true = Text("永远成立", font_size=42, color=WHITE)
        self.place_in_area(always_true, 'G5', 'G6')
        always_true.next_to(formula, DOWN, buff=0.4)
        self.play(FadeIn(always_true))
        self.wait(1)

        self.play(FadeOut(formula), FadeOut(always_true))
        self.wait(1)
from src.manim_base import TeachingScene
from manim import *

class Section4Scene(TeachingScene):
    def construct(self):
        lines = ['3-4-5 组合', '数值代入', '成立！']
        self.setup_layout("经典验证", lines, line_spacing=1.4)  # 增加左侧讲义行间距

        # 顶部公式
        top_formula = MathTex("a^2 + b^2 = c^2", color=GOLD)
        self.place_in_area(top_formula, 'A1', 'A10')
        self.play(FadeIn(top_formula))
        self.wait(1)

        # 步骤 1: 3-4-5 组合
        self.highlight_line(0)
        # 创建小字算式，字号与顶部公式一致
        calc = MathTex("3^2 + 4^2 = 9 + 16 = 25", color=WHITE, font_size=48)
        self.place_in_area(calc, 'B2', 'I3')
        self.play(FadeIn(calc))
        self.wait(1)

        # 步骤 2: 数值代入
        self.highlight_line(1)
        # 放大25并变色
        twenty_five = calc[0][-2:]  # "25"
        self.play(
            twenty_five.animate.scale(1.5).set_color(GREEN),
            run_time=0.6
        )
        # 滑入5^2，增加与25的横向间距
        five_sq = MathTex("5^2", color=WHITE, font_size=48)
        five_sq.next_to(calc, RIGHT, buff=0.8)
        self.play(five_sq.animate.shift(LEFT * five_sq.width), run_time=0.6)
        # 同步闪烁
        self.play(
            Flash(twenty_five, color=GREEN, flash_radius=0.3),
            Flash(five_sq, color=WHITE, flash_radius=0.3),
            run_time=0.5
        )
        self.wait(1)

        # 步骤 3: 成立！
        self.highlight_line(2)
        # 组合算式区域
        whole_group = VGroup(calc, five_sq)
        self.play(
            whole_group.animate.scale(1.3).rotate(360 * DEGREES),
            run_time=1.2
        )
        self.play(FadeOut(whole_group), run_time=0.6)
        self.wait(1)
from src.manim_base import TeachingScene
from manim import *

class Section3Scene(TeachingScene):
    def construct(self):
        lines = ['a² + b² = c²', '勾股定理', '永恒真理']
        self.setup_layout("公式亮相", lines)

        # Step 1: 逐字打出公式
        self.highlight_line(0)
        formula = MathTex("a^2 + b^2 = c^2", color=WHITE)
        self.place_in_area(formula, 'D2', 'G9')  # 居中右侧网格
        formula.scale(1.3)  # 稍微缩小避免越界
        letters = formula[0]
        animations = []
        for letter in letters:
            letter.scale(0.01)
            animations.append(letter.animate.scale(100))
        self.play(LaggedStart(*animations, lag_ratio=0.2))
        self.wait(1)

        # Step 2: 公式变金色加粗，扩散光晕
        self.highlight_line(1)
        glow = Circle(radius=1.8, color=GOLD, fill_opacity=0.25, stroke_width=0)
        self.place_in_area(glow, 'D2', 'G9')  # 居中光晕
        self.play(
            formula.animate.set_color(GOLD).set_stroke(width=3),
            FadeIn(glow, scale=0.1),
            run_time=1
        )
        self.wait(2)
        self.play(
            formula.animate.set_color(WHITE).set_stroke(width=0),
            FadeOut(glow, scale=3),
            run_time=1
        )
        self.wait(1)

        # Step 3: 公式缩小上浮，底部淡入文字
        self.highlight_line(2)
        title = Text("勾股定理", color=LIGHT_GRAY, font_size=36)
        self.place_in_area(title, 'H3', 'H8')  # 居中底部文字
        title.set_opacity(0)
        self.play(
            formula.animate.scale(0.5).shift(UP * 2.2),  # 微调上浮距离
            title.animate.set_opacity(1),
            run_time=1.5
        )
        self.wait(1)
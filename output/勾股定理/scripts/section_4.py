from manim import *

class Section4Scene(Scene):
    def construct(self):
        # 标题
        title = Text("数值实例", font_size=36)
        title.to_edge(UP)
        self.play(FadeIn(title))
        
        # 数据
        lines = ['经典的3-4-5三角形', '3² + 4² = 9 + 16', '9 + 16 = 25 = 5²', '定理验证成功！']
        
        # 创建步骤文本
        step_texts = VGroup()
        for i, line in enumerate(lines):
            text = Text(f"{i+1}. {line}", font_size=24)
            step_texts.add(text)
        step_texts.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        step_texts.to_edge(LEFT, buff=0.5)
        step_texts.shift(DOWN * 0.5)
        
        self.play(FadeIn(step_texts))
        
        # 步骤 1: 经典的3-4-5三角形
        self.play(step_texts[0].animate.set_color(YELLOW))
        
        # 创建3-4-5直角三角形
        triangle = Polygon(
            ORIGIN,
            3 * RIGHT * 0.5,
            3 * RIGHT * 0.5 + 4 * UP * 0.5,
            color=WHITE,
            stroke_width=3
        )
        triangle.move_to(ORIGIN + RIGHT * 1.5)
        
        # 添加边标签
        # 底边 (3)
        p0, p1, p2 = triangle.get_vertices()
        label_3 = MathTex("3", color=BLUE, font_size=36)
        label_3.next_to((p0 + p1) / 2, DOWN, buff=0.2)
        
        # 右边 (4)
        label_4 = MathTex("4", color=GREEN, font_size=36)
        label_4.next_to((p1 + p2) / 2, RIGHT, buff=0.2)
        
        # 斜边 (5)
        label_5 = MathTex("5", color=RED, font_size=36)
        label_5.next_to((p0 + p2) / 2, LEFT + UP, buff=0.2)
        
        # 添加直角标记
        right_angle = RightAngle(
            Line(p1, p0),
            Line(p1, p2),
            length=0.2,
            color=WHITE
        )
        
        # 动画：三角形出现，数字淡入
        self.play(Create(triangle))
        self.play(Create(right_angle))
        self.play(
            FadeIn(label_3, shift=UP * 0.2),
            FadeIn(label_4, shift=LEFT * 0.2),
            FadeIn(label_5, shift=DOWN * 0.2),
        )
        self.wait(1)
        
        # 步骤 2: 3² + 4² = 9 + 16
        self.play(
            step_texts[0].animate.set_color(WHITE),
            step_texts[1].animate.set_color(YELLOW)
        )
        
        # 先显示 3² + 4²
        eq1_left = MathTex("3^2", "+", "4^2", font_size=36)
        eq1_left[0].set_color(BLUE)
        eq1_left[2].set_color(GREEN)
        eq1_left.move_to(RIGHT * 4 + UP * 1)
        
        self.play(FadeIn(eq1_left))
        self.wait(0.5)
        
        # 创建完整等式
        eq1 = MathTex("3^2", "+", "4^2", "=", "9", "+", "16", font_size=36)
        eq1[0].set_color(BLUE)
        eq1[2].set_color(GREEN)
        eq1[4].set_color(BLUE)
        eq1[6].set_color(GREEN)
        eq1.move_to(RIGHT * 4 + UP * 1)
        
        # 变换为完整等式
        self.play(
            ReplacementTransform(eq1_left, eq1[:3]),
            run_time=0.5
        )
        self.play(
            FadeIn(eq1[3], scale=1.5),  # =
            FadeIn(eq1[4], scale=1.5),  # 9
            FadeIn(eq1[5], scale=1.5),  # +
            FadeIn(eq1[6], scale=1.5),  # 16
        )
        self.wait(1)
        
        # 步骤 3: 9 + 16 = 25 = 5²
        self.play(
            step_texts[1].animate.set_color(WHITE),
            step_texts[2].animate.set_color(YELLOW)
        )
        
        # 创建新等式
        eq2 = MathTex("3^2", "+", "4^2", "=", "25", "=", "5^2", font_size=36)
        eq2[0].set_color(BLUE)
        eq2[2].set_color(GREEN)
        eq2[4].set_color(YELLOW)
        eq2[6].set_color(RED)
        eq2.move_to(RIGHT * 4 + UP * 1)
        
        # 9 + 16 合并为 25
        self.play(
            ReplacementTransform(eq1[:4], eq2[:4]),
            ReplacementTransform(VGroup(eq1[4], eq1[5], eq1[6]), eq2[4]),
            run_time=1
        )
        self.wait(0.3)
        
        # 显示 = 5²
        self.play(
            FadeIn(eq2[5], scale=1.5),
            FadeIn(eq2[6], scale=1.5),
        )
        
        # 等号两边同时闪烁
        self.play(
            Indicate(eq2[4], color=YELLOW, scale_factor=1.3),
            Indicate(eq2[6], color=RED, scale_factor=1.3),
        )
        self.wait(1)
        
        # 步骤 4: 定理验证成功！
        self.play(
            step_texts[2].animate.set_color(WHITE),
            step_texts[3].animate.set_color(YELLOW)
        )
        
        # 整个等式变为绿色
        self.play(
            eq2.animate.set_color(GREEN),
            triangle.animate.set_color(GREEN),
            label_3.animate.set_color(GREEN),
            label_4.animate.set_color(GREEN),
            label_5.animate.set_color(GREEN),
            run_time=1
        )
        
        # 创建对勾符号
        checkmark = MathTex(r"\checkmark", color=GREEN, font_size=72)
        checkmark.move_to(RIGHT * 4 + DOWN * 1)
        
        # 对勾出现
        self.play(
            FadeIn(checkmark, scale=2),
            Flash(checkmark, color=GREEN, line_length=0.3)
        )
        
        # 三角形边框闪烁表示验证通过
        self.play(
            Indicate(triangle, color=GREEN, scale_factor=1.05),
            run_time=1
        )
        
        self.wait(2)
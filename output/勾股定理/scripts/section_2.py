from manim import *

class Section2Scene(Scene):
    def construct(self):
        # 创建标题
        title = Text("勾股定理公式", font_size=36)
        title.to_edge(UP)
        self.play(FadeIn(title))
        
        # 创建说明文字
        lines = [
            Text("两直角边的平方", font_size=24),
            Text("等于斜边的平方", font_size=24),
            MathTex("a^2 + b^2 = c^2").scale(0.8)
        ]
        
        # 放置说明文字在右侧
        text_group = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        text_group.to_edge(RIGHT, buff=1)
        
        # 创建直角三角形 (3-4-5 比例)
        triangle = Polygon(
            ORIGIN,
            3 * RIGHT,
            3 * RIGHT + 4 * UP,
            color=WHITE,
            stroke_width=3
        )
        
        # 缩放并放置三角形到左侧
        triangle.scale(0.5)
        triangle.move_to(LEFT * 2.5)
        
        # 获取三角形的顶点
        vertices = triangle.get_vertices()
        v0, v1, v2 = vertices[0], vertices[1], vertices[2]
        
        # 计算边的中点用于标签定位
        side_a_mid = (v1 + v2) / 2  # 边a (垂直边)
        side_b_mid = (v0 + v1) / 2  # 边b (水平边)
        side_c_mid = (v0 + v2) / 2  # 边c (斜边)
        
        # 创建边的线条对象用于闪烁
        side_a = Line(v1, v2, color=BLUE, stroke_width=4)
        side_b = Line(v0, v1, color=GREEN, stroke_width=4)
        side_c = Line(v0, v2, color=RED, stroke_width=4)
        
        # 创建边标签
        label_a = MathTex("a", color=BLUE).scale(0.7).next_to(side_a_mid, RIGHT, buff=0.2)
        label_b = MathTex("b", color=GREEN).scale(0.7).next_to(side_b_mid, DOWN, buff=0.2)
        label_c = MathTex("c", color=RED).scale(0.7).next_to(side_c_mid, LEFT + UP, buff=0.2)
        
        # 添加直角标记
        right_angle = RightAngle(
            Line(v1, v0), Line(v1, v2),
            length=0.2, color=YELLOW
        )
        
        # 显示三角形
        self.play(Create(triangle))
        self.play(
            FadeIn(label_a), FadeIn(label_b), FadeIn(label_c),
            Create(right_angle)
        )
        self.wait(0.5)
        
        # 步骤 1: 两直角边的平方
        self.play(FadeIn(lines[0]))
        lines[0].set_color(YELLOW)
        
        # 边a闪烁 - 添加side_a到场景
        self.add(side_a)
        self.play(
            side_a.animate.set_color(YELLOW),
            label_a.animate.set_color(YELLOW),
            run_time=0.3
        )
        self.play(
            side_a.animate.set_color(BLUE),
            label_a.animate.set_color(BLUE),
            run_time=0.3
        )
        
        # 显示 a² 文字
        a_squared = MathTex("a^2", color=BLUE).scale(0.8)
        a_squared.next_to(v2, RIGHT + UP, buff=0.3)
        self.play(FadeIn(a_squared, shift=UP * 0.2))
        
        # 边b闪烁 - 添加side_b到场景
        self.add(side_b)
        self.play(
            side_b.animate.set_color(YELLOW),
            label_b.animate.set_color(YELLOW),
            run_time=0.3
        )
        self.play(
            side_b.animate.set_color(GREEN),
            label_b.animate.set_color(GREEN),
            run_time=0.3
        )
        
        # 显示 b² 文字
        b_squared = MathTex("b^2", color=GREEN).scale(0.8)
        b_squared.next_to(v0, LEFT + DOWN, buff=0.3)
        self.play(FadeIn(b_squared, shift=UP * 0.2))
        
        lines[0].set_color(WHITE)
        self.wait(1)
        
        # 步骤 2: 等于斜边的平方
        self.play(FadeIn(lines[1]))
        lines[1].set_color(YELLOW)
        
        # 斜边c闪烁变亮 - 添加side_c到场景
        self.add(side_c)
        self.play(
            side_c.animate.set_color(YELLOW).set_stroke(width=6),
            label_c.animate.set_color(YELLOW),
            run_time=0.5
        )
        self.play(
            side_c.animate.set_color(RED).set_stroke(width=4),
            label_c.animate.set_color(RED),
            run_time=0.5
        )
        
        # 显示 c² 文字
        c_squared = MathTex("c^2", color=RED).scale(0.8)
        c_squared.next_to(side_c_mid, LEFT + UP, buff=0.5)
        self.play(FadeIn(c_squared, shift=UP * 0.2))
        
        lines[1].set_color(WHITE)
        self.wait(1)
        
        # 步骤 3: 公式 a² + b² = c²
        self.play(FadeIn(lines[2]))
        lines[2].set_color(YELLOW)
        
        # 创建公式
        formula = MathTex("a^2", "+", "b^2", "=", "c^2")
        formula[0].set_color(BLUE)
        formula[2].set_color(GREEN)
        formula[4].set_color(RED)
        formula.scale(0.8)
        
        # 放置在三角形上方
        formula.next_to(triangle, UP, buff=0.8)
        
        # 淡入公式
        self.play(FadeIn(formula, scale=0.5))
        
        # 逐渐放大并变为金色强调
        self.play(
            formula.animate.scale(1.5).set_color(GOLD),
            run_time=1.5
        )
        
        # 添加发光效果
        glow = formula.copy().set_color(YELLOW).set_stroke(width=2, color=YELLOW, opacity=0.5)
        self.play(
            FadeIn(glow),
            run_time=0.5
        )
        self.play(
            FadeOut(glow),
            run_time=0.5
        )
        
        self.wait(2)
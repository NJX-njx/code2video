from manim import *

class Section5Scene(Scene):
    def construct(self):
        # 标题
        title = Text("总结与应用", font_size=42, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=1)
        
        # 要点列表
        lines = ['勾股定理核心公式', '可求未知边长', '广泛用于测量计算']
        bullet_points = VGroup()
        for i, line in enumerate(lines):
            bullet = Text(f"• {line}", font_size=24, color=WHITE)
            bullet_points.add(bullet)
        bullet_points.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        bullet_points.to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        
        self.play(FadeIn(bullet_points), run_time=1)
        
        # 步骤 1: 公式居中放大显示，加粗并发光强调
        # 高亮第一行
        self.play(bullet_points[0].animate.set_color(YELLOW), run_time=0.5)
        
        # 创建核心公式
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=72)
        formula.set_color(YELLOW)
        formula.move_to(ORIGIN + RIGHT * 1.5)
        
        # 创建发光效果
        glow = formula.copy()
        glow.set_stroke(YELLOW, width=8, opacity=0.5)
        
        self.play(Write(formula), run_time=1.5)
        self.play(
            formula.animate.scale(1.2),
            FadeIn(glow),
            run_time=0.8
        )
        self.play(
            formula.animate.scale(1/1.2),
            FadeOut(glow),
            run_time=0.8
        )
        self.wait(1)
        
        # 步骤 2: 三角形重新出现，问号变为具体数值
        # 高亮第二行
        self.play(
            bullet_points[0].animate.set_color(WHITE),
            bullet_points[1].animate.set_color(YELLOW),
            run_time=0.5
        )
        
        # 将公式移到上方
        self.play(
            formula.animate.scale(0.6).to_edge(UP, buff=1.2),
            run_time=0.8
        )
        
        # 创建直角三角形 (3-4-5比例)
        triangle = Polygon(
            ORIGIN,
            3*RIGHT,
            3*RIGHT + 4*UP,
            color=WHITE,
            stroke_width=3
        )
        triangle.scale(0.4)
        triangle.move_to(LEFT * 2 + DOWN * 0.5)
        
        self.play(Create(triangle), run_time=1)
        
        # 获取三角形顶点
        vertices = triangle.get_vertices()
        v0 = vertices[0]  # 原点
        v1 = vertices[1]  # 右下
        v2 = vertices[2]  # 右上
        
        # 添加边标签
        label_a = MathTex("3", color=BLUE, font_size=36)
        label_a.next_to((v0 + v1) / 2, DOWN, buff=0.2)
        
        label_b = MathTex("4", color=GREEN, font_size=36)
        label_b.next_to((v1 + v2) / 2, RIGHT, buff=0.2)
        
        # 添加问号标签（斜边）
        question_mark = MathTex("?", color=RED, font_size=36)
        hyp_mid = (v0 + v2) / 2
        direction = v2 - v0
        direction = direction / np.linalg.norm(direction)
        perp = np.array([-direction[1], direction[0], 0])
        question_mark.move_to(hyp_mid + perp * 0.4)
        
        # 添加直角标记
        right_angle_size = 0.2
        right_mark = VGroup(
            Line(v1 + UP * right_angle_size, v1 + UP * right_angle_size + LEFT * right_angle_size, color=WHITE),
            Line(v1 + LEFT * right_angle_size, v1 + UP * right_angle_size + LEFT * right_angle_size, color=WHITE)
        )
        
        self.play(
            Write(label_a),
            Write(label_b),
            Write(question_mark),
            Create(right_mark),
            run_time=1
        )
        self.wait(0.5)
        
        # 显示计算过程
        calc = MathTex("3^2 + 4^2 = 9 + 16 = 25 = 5^2", font_size=28)
        calc.move_to(RIGHT * 2 + DOWN * 0.5)
        
        self.play(Write(calc), run_time=1.5)
        self.wait(0.5)
        
        # 问号变为5
        label_c = MathTex("5", color=RED, font_size=36)
        label_c.move_to(question_mark.get_center())
        
        self.play(
            Transform(question_mark, label_c),
            Flash(question_mark, color=YELLOW, flash_radius=0.5),
            run_time=1
        )
        self.wait(1)
        
        # 步骤 3: 应用场景图标依次淡入
        # 高亮第三行
        self.play(
            bullet_points[1].animate.set_color(WHITE),
            bullet_points[2].animate.set_color(YELLOW),
            run_time=0.5
        )
        
        # 清除计算过程和三角形
        self.play(
            FadeOut(triangle),
            FadeOut(label_a),
            FadeOut(label_b),
            FadeOut(question_mark),
            FadeOut(right_mark),
            FadeOut(calc),
            run_time=0.8
        )
        
        # 将公式移回中心并放大
        self.play(
            formula.animate.scale(1.5).move_to(ORIGIN + UP * 0.5),
            run_time=0.8
        )
        
        # 创建应用场景图标
        # 建筑图标 (简化的房子)
        building = VGroup(
            Rectangle(width=0.8, height=0.6, color=BLUE, fill_opacity=0.5),
            Polygon(
                [-0.5, 0.3, 0], [0, 0.7, 0], [0.5, 0.3, 0],
                color=BLUE, fill_opacity=0.5
            )
        )
        building_label = Text("建筑", font_size=18, color=BLUE)
        building_label.next_to(building, DOWN, buff=0.1)
        building_group = VGroup(building, building_label)
        building_group.move_to(LEFT * 4 + UP * 0.5)
        
        # 地图图标 (简化的网格)
        map_icon = VGroup(
            Square(side_length=0.6, color=GREEN, fill_opacity=0.3),
            Line([-0.3, 0, 0], [0.3, 0, 0], color=GREEN),
            Line([0, -0.3, 0], [0, 0.3, 0], color=GREEN),
            Dot(point=[0.15, 0.15, 0], color=RED, radius=0.05)
        )
        map_label = Text("地图", font_size=18, color=GREEN)
        map_label.next_to(map_icon, DOWN, buff=0.1)
        map_group = VGroup(map_icon, map_label)
        map_group.move_to(RIGHT * 4 + UP * 0.5)
        
        # 梯子图标
        ladder = VGroup(
            Line([0, 0, 0], [0, 0.8, 0], color=ORANGE),
            Line([0.3, 0, 0], [0.3, 0.8, 0], color=ORANGE),
            Line([0, 0.2, 0], [0.3, 0.2, 0], color=ORANGE),
            Line([0, 0.4, 0], [0.3, 0.4, 0], color=ORANGE),
            Line([0, 0.6, 0], [0.3, 0.6, 0], color=ORANGE),
        )
        ladder_label = Text("梯子", font_size=18, color=ORANGE)
        ladder_label.next_to(ladder, DOWN, buff=0.1)
        ladder_group = VGroup(ladder, ladder_label)
        ladder_group.move_to(DOWN * 2)
        
        # 依次淡入图标
        self.play(FadeIn(building_group, shift=UP), run_time=0.8)
        self.wait(0.3)
        self.play(FadeIn(map_group, shift=UP), run_time=0.8)
        self.wait(0.3)
        self.play(FadeIn(ladder_group, shift=UP), run_time=0.8)
        self.wait(0.5)
        
        # 所有元素汇聚，公式保持居中
        all_icons = VGroup(building_group, map_group, ladder_group)
        
        self.play(
            all_icons.animate.scale(0.5).arrange(RIGHT, buff=0.5).next_to(formula, DOWN, buff=0.5),
            formula.animate.scale(0.8),
            run_time=1.2
        )
        
        # 最终发光效果
        final_glow = formula.copy()
        final_glow.set_stroke(YELLOW, width=6, opacity=0.6)
        
        self.play(
            FadeIn(final_glow),
            run_time=0.5
        )
        self.play(
            FadeOut(final_glow),
            run_time=0.5
        )
        
        self.wait(2)
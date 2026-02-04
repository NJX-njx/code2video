from manim import *

class Section3Scene(Scene):
    def construct(self):
        # 标题
        title = Text("几何证明——面积法", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        
        # 步骤文字
        lines = ['在各边上画正方形', 'a²和b²是两小正方形', 'c²是大正方形面积', '小正方形面积之和等于大']
        
        steps = VGroup()
        for i, line in enumerate(lines):
            step_text = Text(f"{i+1}. {line}", font_size=24)
            steps.add(step_text)
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        steps.to_edge(LEFT, buff=0.5)
        steps.shift(DOWN * 0.5)
        
        self.play(FadeIn(steps))
        
        # 创建直角三角形 (3-4-5比例)
        A = ORIGIN
        B = 3 * RIGHT
        C = 4 * UP
        
        triangle = Polygon(A, B, C, color=WHITE, stroke_width=3)
        triangle.set_fill(opacity=0)
        triangle.scale(0.5)
        triangle.move_to(RIGHT * 1.5)
        
        # 添加边标签
        verts = triangle.get_vertices()
        v_A, v_B, v_C = verts[0], verts[1], verts[2]
        
        mid_a = (v_A + v_B) / 2
        mid_b = (v_A + v_C) / 2
        mid_c = (v_B + v_C) / 2
        
        label_a = MathTex("a", color=BLUE, font_size=30)
        label_a.next_to(mid_a, DOWN, buff=0.15)
        
        label_b = MathTex("b", color=GREEN, font_size=30)
        label_b.next_to(mid_b, LEFT, buff=0.15)
        
        label_c = MathTex("c", color=RED, font_size=30)
        label_c.next_to(mid_c, UR, buff=0.15)
        
        # 直角标记
        right_angle_size = 0.2
        right_mark = VGroup(
            Line(v_A + RIGHT * right_angle_size, v_A + RIGHT * right_angle_size + UP * right_angle_size, color=WHITE, stroke_width=2),
            Line(v_A + UP * right_angle_size, v_A + RIGHT * right_angle_size + UP * right_angle_size, color=WHITE, stroke_width=2)
        )
        
        triangle_group = VGroup(triangle, label_a, label_b, label_c, right_mark)
        
        self.play(Create(triangle), Create(right_mark))
        self.play(FadeIn(label_a), FadeIn(label_b), FadeIn(label_c))
        self.wait(0.5)
        
        # 步骤 1: 在各边上画正方形
        self.play(steps[0].animate.set_color(YELLOW))
        
        # 将三角形移至左侧
        self.play(triangle_group.animate.shift(LEFT * 1))
        self.wait(0.3)
        
        # 获取三角形当前顶点位置
        verts = triangle.get_vertices()
        v_A, v_B, v_C = verts[0], verts[1], verts[2]
        
        # 计算各边向量
        edge_a = v_B - v_A
        edge_b = v_C - v_A
        edge_c = v_C - v_B
        
        # a边上的正方形 (向下生长)
        a_len = np.linalg.norm(edge_a)
        a_unit = edge_a / a_len
        a_perp = np.array([a_unit[1], -a_unit[0], 0])
        sq_a = Polygon(
            v_A, v_B, 
            v_B + a_perp * a_len, 
            v_A + a_perp * a_len,
            color=BLUE, stroke_width=2
        )
        
        # b边上的正方形 (向左生长)
        b_len = np.linalg.norm(edge_b)
        b_unit = edge_b / b_len
        b_perp = np.array([-b_unit[1], b_unit[0], 0])
        sq_b = Polygon(
            v_A, v_C,
            v_C + b_perp * b_len,
            v_A + b_perp * b_len,
            color=GREEN, stroke_width=2
        )
        
        # c边上的正方形 (向右上生长)
        c_len = np.linalg.norm(edge_c)
        c_unit = edge_c / c_len
        c_perp = np.array([-c_unit[1], c_unit[0], 0])
        sq_c = Polygon(
            v_B, v_C,
            v_C + c_perp * c_len,
            v_B + c_perp * c_len,
            color=RED, stroke_width=2
        )
        
        # 正方形生长动画
        self.play(
            Create(sq_a),
            Create(sq_b),
            Create(sq_c),
            run_time=1.5
        )
        self.wait(1)
        
        # 步骤 2: a²和b²是两小正方形
        self.play(steps[0].animate.set_color(WHITE), steps[1].animate.set_color(YELLOW))
        
        # 创建网格线 for sq_a
        grid_a = VGroup()
        sq_a_verts = sq_a.get_vertices()
        for i in range(1, 3):
            t = i / 3
            start = sq_a_verts[0] + t * (sq_a_verts[1] - sq_a_verts[0])
            end = sq_a_verts[3] + t * (sq_a_verts[2] - sq_a_verts[3])
            grid_a.add(Line(start, end, color=BLUE_B, stroke_width=1))
            start = sq_a_verts[0] + t * (sq_a_verts[3] - sq_a_verts[0])
            end = sq_a_verts[1] + t * (sq_a_verts[2] - sq_a_verts[1])
            grid_a.add(Line(start, end, color=BLUE_B, stroke_width=1))
        
        # 创建网格线 for sq_b
        grid_b = VGroup()
        sq_b_verts = sq_b.get_vertices()
        for i in range(1, 4):
            t = i / 4
            start = sq_b_verts[0] + t * (sq_b_verts[1] - sq_b_verts[0])
            end = sq_b_verts[3] + t * (sq_b_verts[2] - sq_b_verts[3])
            grid_b.add(Line(start, end, color=GREEN_B, stroke_width=1))
            start = sq_b_verts[0] + t * (sq_b_verts[3] - sq_b_verts[0])
            end = sq_b_verts[1] + t * (sq_b_verts[2] - sq_b_verts[1])
            grid_b.add(Line(start, end, color=GREEN_B, stroke_width=1))
        
        # 变蓝色并填充
        self.play(
            sq_a.animate.set_fill(BLUE_A, opacity=0.4).set_stroke(BLUE, width=3),
            Create(grid_a),
            run_time=0.8
        )
        self.play(
            sq_b.animate.set_fill(GREEN_A, opacity=0.4).set_stroke(GREEN, width=3),
            Create(grid_b),
            run_time=0.8
        )
        
        # 添加a²和b²标签
        label_a2 = MathTex("a^2", color=BLUE, font_size=28)
        label_a2.move_to(sq_a.get_center())
        label_b2 = MathTex("b^2", color=GREEN, font_size=28)
        label_b2.move_to(sq_b.get_center())
        
        self.play(FadeIn(label_a2), FadeIn(label_b2))
        self.wait(1)
        
        # 步骤 3: c²是大正方形面积
        self.play(steps[1].animate.set_color(WHITE), steps[2].animate.set_color(YELLOW))
        
        # 创建网格线 for sq_c
        grid_c = VGroup()
        sq_c_verts = sq_c.get_vertices()
        for i in range(1, 5):
            t = i / 5
            start = sq_c_verts[0] + t * (sq_c_verts[1] - sq_c_verts[0])
            end = sq_c_verts[3] + t * (sq_c_verts[2] - sq_c_verts[3])
            grid_c.add(Line(start, end, color=YELLOW_B, stroke_width=1))
            start = sq_c_verts[0] + t * (sq_c_verts[3] - sq_c_verts[0])
            end = sq_c_verts[1] + t * (sq_c_verts[2] - sq_c_verts[1])
            grid_c.add(Line(start, end, color=YELLOW_B, stroke_width=1))
        
        self.play(
            sq_c.animate.set_fill(YELLOW_A, opacity=0.4).set_stroke(YELLOW, width=3),
            Create(grid_c),
            run_time=1
        )
        
        # 添加c²标签
        label_c2 = MathTex("c^2", color=YELLOW, font_size=32)
        label_c2.move_to(sq_c.get_center())
        
        self.play(FadeIn(label_c2))
        self.wait(1)
        
        # 步骤 4: 小正方形面积之和等于大
        self.play(steps[2].animate.set_color(WHITE), steps[3].animate.set_color(YELLOW))
        
        # 创建小正方形的碎片副本用于移动
        sq_a_copy = sq_a.copy()
        sq_a_copy.set_fill(BLUE_A, opacity=0.6)
        grid_a_copy = grid_a.copy()
        piece_a = VGroup(sq_a_copy, grid_a_copy)
        
        sq_b_copy = sq_b.copy()
        sq_b_copy.set_fill(GREEN_A, opacity=0.6)
        grid_b_copy = grid_b.copy()
        piece_b = VGroup(sq_b_copy, grid_b_copy)
        
        self.add(piece_a, piece_b)
        
        # 计算移动到大正方形的位置
        sq_c_center = sq_c.get_center()
        
        # 移动并旋转碎片到大正方形
        self.play(
            piece_a.animate.move_to(sq_c_center + UP * 0.3 + LEFT * 0.2).rotate(PI/6).scale(0.8),
            piece_b.animate.move_to(sq_c_center + DOWN * 0.2 + RIGHT * 0.1).rotate(-PI/8).scale(0.8),
            run_time=1.5
        )
        
        # 最终拼合
        self.play(
            piece_a.animate.move_to(sq_c_center).set_opacity(0.5),
            piece_b.animate.move_to(sq_c_center).set_opacity(0.5),
            run_time=1
        )
        
        # 闪烁效果
        flash_rect = sq_c.copy()
        flash_rect.set_fill(WHITE, opacity=0.8)
        flash_rect.set_stroke(WHITE, width=5)
        
        self.play(
            FadeIn(flash_rect, rate_func=there_and_back),
            run_time=0.5
        )
        self.play(
            FadeIn(flash_rect, rate_func=there_and_back),
            run_time=0.5
        )
        
        # 显示最终等式
        equation = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=40)
        equation[0].set_color(BLUE)
        equation[2].set_color(GREEN)
        equation[4].set_color(YELLOW)
        equation.next_to(triangle_group, DOWN, buff=0.5)
        
        self.play(Write(equation))
        
        # 最终闪烁
        self.play(
            Indicate(equation, color=GOLD, scale_factor=1.2),
            run_time=1
        )
        
        self.wait(2)
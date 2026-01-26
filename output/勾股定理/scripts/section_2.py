from src.manim_base import TeachingScene
from manim import *

class AreaPuzzleScene(TeachingScene):
    def construct(self):
        lines = ['正方形面积', '拼成大图', '面积守恒']
        self.setup_layout("面积拼图", lines)

        # Step 1: 正方形面积
        self.highlight_line(0)
        # 创建红色正方形（边长AB）和绿色正方形（边长BC）
        red_square = Square(side_length=2.0, color=RED, fill_opacity=0.8)
        green_square = Square(side_length=1.5, color=GREEN, fill_opacity=0.8)
        
        # 放置到左侧和右侧区域
        self.place_in_area(red_square, 'B2', 'D4')
        self.place_in_area(green_square, 'F2', 'H4')
        
        # 同时淡入并跳动一次
        self.play(
            FadeIn(red_square),
            FadeIn(green_square),
            run_time=1
        )
        self.play(
            red_square.animate.shift(UP * 0.3).shift(DOWN * 0.3),
            green_square.animate.shift(UP * 0.3).shift(DOWN * 0.3),
            run_time=0.6
        )
        self.wait(1)

        # Step 2: 拼成大图
        self.highlight_line(1)
        # 碎裂成小块并飞向中央拼接成蓝色大正方形
        # 碎裂红色正方形
        red_pieces = VGroup(*[
            Square(side_length=0.5, color=RED, fill_opacity=0.8)
            for _ in range(16)
        ])
        red_pieces.arrange_in_grid(4, 4, buff=0)
        red_pieces.move_to(red_square.get_center())
        
        # 碎裂绿色正方形
        green_pieces = VGroup(*[
            Square(side_length=0.5, color=GREEN, fill_opacity=0.8)
            for _ in range(9)
        ])
        green_pieces.arrange_in_grid(3, 3, buff=0)
        green_pieces.move_to(green_square.get_center())
        
        # 替换原正方形为碎块
        self.play(
            Transform(red_square, red_pieces),
            Transform(green_square, green_pieces),
            run_time=0.5
        )
        
        # 创建目标蓝色大正方形（边长CA，假设CA=2.5）
        blue_square = Square(side_length=2.5, color=BLUE, fill_opacity=0.8)
        self.place_in_area(blue_square, 'D5', 'G8')
        
        # 所有碎块飞向中央拼接
        all_pieces = VGroup(red_pieces, green_pieces)
        self.play(
            all_pieces.animate.move_to(blue_square.get_center()).scale(0.8),
            run_time=1.5
        )
        
        # 碎块融合成蓝色正方形
        self.play(
            Transform(all_pieces, blue_square),
            run_time=1
        )
        self.wait(1)

        # Step 3: 面积守恒
        self.highlight_line(2)
        # 蓝色正方形闪烁三次
        for _ in range(3):
            self.play(
                blue_square.animate.set_fill(opacity=0.3),
                run_time=0.3
            )
            self.play(
                blue_square.animate.set_fill(opacity=0.8),
                run_time=0.3
            )
        
        # 内部小块逐渐透明化，仅留下外框
        self.play(
            blue_square.animate.set_fill(opacity=0),
            run_time=1
        )
        
        # 强调外框（面积相等）
        self.play(
            blue_square.animate.set_stroke(width=6),
            run_time=0.5
        )
        self.wait(1)
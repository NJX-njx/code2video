# 证明推导动画技巧

## 等式链展示
```python
# 逐步展示推导过程中的等式变换
eq1 = MathTex(r"a^2 + b^2", font_size=36)
self.place_in_area(eq1, 'C3', 'E6')
self.play(Write(eq1))
self.wait(0.5)

# 变换到下一步
eq2 = MathTex(r"= c^2", font_size=36)
eq2.next_to(eq1, RIGHT, buff=0.2)
self.play(Write(eq2))
self.wait(0.5)
```

## 高亮关键变换
```python
# 用框或颜色强调关键步骤
highlight_box = SurroundingRectangle(eq1, color=YELLOW, buff=0.1)
self.play(Create(highlight_box))
self.wait(0.5)
self.play(FadeOut(highlight_box))
```

## 推理箭头
```python
# 步骤之间用箭头 + 文字说明
arrow = Arrow(eq1.get_bottom(), eq2.get_top(), color=WHITE, buff=0.2)
reason = Text("(代入)", font_size=20, color=GRAY).next_to(arrow, RIGHT, buff=0.1)
self.play(Create(arrow), FadeIn(reason))
```

## 几何图形 + 公式联动
```python
# 高亮几何体的某条边，同时在公式中高亮对应变量
self.play(
    triangle.get_sides()[0].animate.set_color(RED),
    eq1[0].animate.set_color(RED),  # 假设 a 在 eq1 的第 0 个子对象
    run_time=1
)
```

## 注意事项
- 证明题的 Section 数通常为 2-4 个（不宜过多）
- 每个 Section 对应一个关键推理步骤
- 公式推导可以在同一个 Section 内完成多步，不需要每步一个 Section
- 几何证明需要同时展示图形和公式

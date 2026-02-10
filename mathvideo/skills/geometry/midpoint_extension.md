# 中点、倍长与辅助线技巧

## 线段中点
```python
# M 是 AE 的中点
M_pos = (A_pos + E_pos) / 2
point_M = Dot(M_pos, color=YELLOW)
label_M = MathTex("M", color=YELLOW, font_size=28).next_to(point_M, UP, buff=0.2)
```

## 倍长线段
```python
# 倍长 FM 到 N（即 N 在 FM 延长线上，MN = FM）
FM_vec = M_pos - F_pos
N_pos = M_pos + FM_vec  # N = M + (M - F) = 2M - F
point_N = Dot(N_pos, color=RED)
label_N = MathTex("N", color=RED, font_size=28).next_to(point_N, RIGHT, buff=0.2)

# 动画: 先画 FM 延长线，再标注 N
extend_line = DashedLine(M_pos, N_pos, color=GRAY)
self.play(Create(extend_line), run_time=0.8)
self.play(FadeIn(point_N), FadeIn(label_N), run_time=0.5)
```

## 连接辅助线
```python
# 连接多条辅助线时，推荐使用 VGroup 批量创建
auxiliary_lines = VGroup(
    Line(C_pos, M_pos, color=ORANGE, stroke_width=2),
    Line(F_pos, M_pos, color=ORANGE, stroke_width=2),
    Line(C_pos, N_pos, color=TEAL, stroke_width=2),
    Line(A_pos, N_pos, color=TEAL, stroke_width=2),
)
# 可以逐条动画，也可以一起显示
for line in auxiliary_lines:
    self.play(Create(line), run_time=0.5)
```

## 射线与直线
```python
# 射线 AD（从 A 出发经过 D 并延伸）
AD_unit = (D_pos - A_pos) / np.linalg.norm(D_pos - A_pos)
ray_end = D_pos + 1.5 * AD_unit  # 延伸一定距离
ray_AD = Line(A_pos, ray_end, color=YELLOW, stroke_width=2)

# 如果射线与某条线交于点 H，用参数方程求交
# Line1: A + t * AD_unit
# Line2: B + s * dir2
# 解方程组
```

## 注意事项
- 倍长线段时注意方向：`N = M + (M - F)` 不是 `N = F + 2*(M - F)`，后者也正确但意义不同
- 连接辅助线时使用不同颜色区分不同组的关系
- 中点标记可以加等距短线表示 AM = ME

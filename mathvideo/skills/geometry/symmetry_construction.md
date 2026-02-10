# 对称构造动画技巧

## 轴对称点构造（含动画过程）

### 计算对称点
```python
# 点 B 关于直线 AD 的对称点 P
A_pos = vertices[0]
D_pos = D_point  # 已知的点 D 坐标
AD = D_pos - A_pos
AB = B_pos - A_pos

# 投影公式: B 在 AD 上的投影
proj_scalar = np.dot(AB, AD) / np.dot(AD, AD)
foot_pos = A_pos + proj_scalar * AD  # 垂足

# 对称点 = 2 * 垂足 - 原点
P_pos = 2 * foot_pos - B_pos
```

### 展示对称过程动画
```python
# 1. 画垂线（B 到垂足）
perp_line = DashedLine(B_pos, foot_pos, color=GRAY)
self.play(Create(perp_line), run_time=0.8)

# 2. 画垂足标记
right_angle_mark = Square(side_length=0.15, color=GRAY).move_to(
    foot_pos + 0.1 * normalize(B_pos - foot_pos) + 0.1 * normalize(np.cross(AD, OUT)[:3])
)
self.play(Create(right_angle_mark), run_time=0.3)

# 3. 延长等距到 P
extend_line = DashedLine(foot_pos, P_pos, color=GRAY)
self.play(Create(extend_line), run_time=0.8)

# 4. 添加等距标记
AD_unit = AD / np.linalg.norm(AD)
mid1 = (B_pos + foot_pos) / 2
mid2 = (foot_pos + P_pos) / 2
tick_size = 0.1
tick1 = Line(mid1 - tick_size * AD_unit, mid1 + tick_size * AD_unit, color=GRAY, stroke_width=2)
tick2 = Line(mid2 - tick_size * AD_unit, mid2 + tick_size * AD_unit, color=GRAY, stroke_width=2)
self.play(Create(tick1), Create(tick2), run_time=0.5)

# 5. 标注对称点
point_P = Dot(P_pos, color=GREEN)
label_P = MathTex("P", color=GREEN, font_size=28).next_to(point_P, LEFT, buff=0.2)
self.play(FadeIn(point_P, scale=1.5), FadeIn(label_P), run_time=0.8)
```

## 等距标记的通用做法
```python
# 在线段中点处添加短横线标记表示等长
def add_tick_mark(start, end, perpendicular_dir, color=GRAY):
    mid = (start + end) / 2
    tick_size = 0.1
    return Line(
        mid - tick_size * perpendicular_dir,
        mid + tick_size * perpendicular_dir,
        color=color, stroke_width=2
    )
```

## 注意事项
- 对称构造时，确保 `np.dot(AD, AD)` 不为零（AD 方向向量长度不为零）
- 垂足可能在线段外，这时对称点的位置仍然是数学正确的
- 等距标记的方向应垂直于等距线段本身，不要平行

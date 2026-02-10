# 角平分线与平行线构造技巧

## 外角平分线
```python
# 延长 CB 到 E，构造外角 ∠ABE
CB_vec = B_pos - C_pos
CB_unit = CB_vec / np.linalg.norm(CB_vec)
E_pos = B_pos + 1.5 * CB_unit  # 延长到 E
ray_BE = DashedLine(B_pos, E_pos, color=GRAY, dash_length=0.1)

# 外角平分线方向 = BA 方向 + BE 方向的角平分
BA_unit = (A_pos - B_pos) / np.linalg.norm(A_pos - B_pos)
BE_unit = (E_pos - B_pos) / np.linalg.norm(E_pos - B_pos)

angle_BA = np.arctan2(BA_unit[1], BA_unit[0])
angle_BE = np.arctan2(BE_unit[1], BE_unit[0])
# 注意角度连续性，可能需要 +2π
if angle_BA < angle_BE:
    angle_BA += 2 * np.pi

bisector_angle = angle_BE + (angle_BA - angle_BE) / 2
bisector_dir = np.array([np.cos(bisector_angle), np.sin(bisector_angle), 0])
M_pos = B_pos + 2.0 * bisector_dir
ray_BM = Line(B_pos, M_pos, color=PURPLE, stroke_width=3)
```

## 角度标记弧线
```python
# 在顶点 A 处标记角度 α（从 AB 到 AD）
AB_vec = B_pos - A_pos
AD_vec = D_pos - A_pos
start_angle = np.arctan2(AB_vec[1], AB_vec[0])
end_angle = np.arctan2(AD_vec[1], AD_vec[0])

angle_arc = Arc(
    radius=0.5,
    start_angle=start_angle,
    angle=end_angle - start_angle,
    arc_center=A_pos,
    color=GREEN
)

# 在弧线中间位置添加角度标签
mid_angle = (start_angle + end_angle) / 2
label_offset = 0.75 * np.array([np.cos(mid_angle), np.sin(mid_angle), 0])
angle_label = MathTex(r"\alpha", color=GREEN, font_size=28).move_to(A_pos + label_offset)
```

## 作平行线并求交点
```python
# 过点 A 作 CP 的平行线，与 BM 交于点 N
CP_unit = (P_pos - C_pos) / np.linalg.norm(P_pos - C_pos)

# 参数方程求交点:
# A + t * CP_unit = B + s * bisector_dir
d1 = CP_unit[:2]
d2 = -bisector_dir[:2]
b = (B_pos - A_pos)[:2]
det = d1[0] * d2[1] - d1[1] * d2[0]

if abs(det) > 1e-6:
    t_param = (b[0] * d2[1] - b[1] * d2[0]) / det
    N_pos = A_pos + t_param * CP_unit
else:
    N_pos = A_pos + 1.5 * CP_unit  # 退化时的回退

line_AN = Line(A_pos, N_pos, color=TEAL, stroke_width=3)
```

## 平行线标记
```python
# 在两条平行线中点处添加箭头标记
CP_mid = (C_pos + P_pos) / 2
AN_mid = (A_pos + N_pos) / 2
arrow_size = 0.15

arrow1 = Arrow(
    CP_mid - arrow_size * CP_unit,
    CP_mid + arrow_size * CP_unit,
    buff=0, stroke_width=2,
    max_tip_length_to_length_ratio=0.5, color=YELLOW
).scale(0.5)

arrow2 = Arrow(
    AN_mid - arrow_size * CP_unit,
    AN_mid + arrow_size * CP_unit,
    buff=0, stroke_width=2,
    max_tip_length_to_length_ratio=0.5, color=YELLOW
).scale(0.5)
```

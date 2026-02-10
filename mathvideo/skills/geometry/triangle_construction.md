# 三角形构造技巧

## 等边三角形
```python
# 使用正确的数学比例，边长 s
s = 3
triangle = Polygon(
    ORIGIN,
    s * RIGHT,
    s/2 * RIGHT + s * np.sqrt(3)/2 * UP,
    color=BLUE
)
self.place_in_area(triangle, 'B2', 'I8', scale_factor=0.85)
```

## 直角三角形
```python
# 使用 3-4-5 比例
triangle = Polygon(
    ORIGIN,
    3 * RIGHT,
    3 * RIGHT + 4 * UP,
    color=BLUE
)
self.place_in_area(triangle, 'B2', 'I8')
```

## 在边上取点
```python
# 在 BC 边上取点 D（比例 t，0 < t < 1）
vertices = triangle.get_vertices()
B, C = vertices[1], vertices[2]  # 根据实际顶点顺序
t = 0.4  # D 在 BC 上的比例位置
D = B + t * (C - B)
dot_D = Dot(D, color=RED)
label_D = MathTex("D", color=RED, font_size=28).next_to(dot_D, DOWN, buff=0.2)
```

## 对称点构造
```python
# 构造点 B 关于直线 AD 的对称点 P
# 1. 计算 B 到直线 AD 的投影
A, D = vertices[0], D_point
AD = D - A
proj = A + np.dot(B - A, AD) / np.dot(AD, AD) * AD  # B 在 AD 上的投影
# 2. 对称点 = 2 * 投影 - 原点
P = 2 * proj - B
dot_P = Dot(P, color=GREEN)
```

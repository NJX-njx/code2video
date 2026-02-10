# 标签定位技巧

## 核心原则
- 先用 `place_in_area()` 放置几何体
- 再用辅助方法添加标签：
  - `self.add_side_label(polygon, side_index, text)` — 边标签
  - `self.add_vertex_label(polygon, vertex_index, text)` — 顶点标签  
  - `self.add_right_angle_mark(polygon, vertex_index)` — 直角标记

## 正确示例
```python
triangle = Polygon(ORIGIN, 3*RIGHT, 3*RIGHT + 4*UP)
self.place_in_area(triangle, 'B2', 'I8')
label_a = self.add_side_label(triangle, 0, "a", color=BLUE)
label_A = self.add_vertex_label(triangle, 0, "A")
```

## 错误示例（会导致标签飞走）
```python
label = MathTex("a").next_to(side, RIGHT)
self.place_at_grid(label, 'E5')  # 覆盖了 next_to 的定位！
```

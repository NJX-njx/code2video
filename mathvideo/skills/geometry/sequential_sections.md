# 递进式 Section 构造技巧

## 核心原则
在 geometry 和 proof 模式下，后续 Section 需要重建前序 Section 的所有对象。

## 做法
1. 参考前序 Section 的代码，复制几何对象的创建和定位代码
2. 使用 `self.add(obj)` 直接添加（不要用动画），让已有对象立即可见
3. 然后用动画 `self.play(Create(...))` 添加本 Section 的新对象

## 示例
```python
class Section2Scene(TeachingScene):
    def construct(self):
        lines = ["D在BC上", "P是B的对称点"]
        self.setup_layout("构造对称点", lines)
        
        # === 继承前序对象（直接显示） ===
        # 与 Section1 完全相同的创建和定位代码
        triangle = Polygon(ORIGIN, 3*RIGHT, 3*RIGHT + 4*UP, color=BLUE)
        self.place_in_area(triangle, 'B2', 'I8')
        label_A = self.add_vertex_label(triangle, 0, "A")
        label_B = self.add_vertex_label(triangle, 1, "B")
        label_C = self.add_vertex_label(triangle, 2, "C")
        self.add(triangle, label_A, label_B, label_C)  # 直接 add
        
        # === 本 Section 新内容（用动画） ===
        self.highlight_line(0)
        # ... 动画添加新对象 ...
```

## 关键注意事项
- **坐标一致性**: 继承对象的 `place_in_area` 参数必须与前序代码完全一致
- **不要重新计算**: 如果前序用了 `place_in_area(triangle, 'B2', 'I8')`，继承时也必须用相同参数
- **标签也要继承**: 不只是几何体，标签和标记也要一起重建

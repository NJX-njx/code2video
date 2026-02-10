# 视觉一致性规范（跨 Section 场景）

## 核心原则
递进模式下，多个 Section 的视频是分别渲染并最终合并的。
观众会连续观看这些片段，所以**视觉必须前后一致**。

## 颜色规范
在同一个项目中，每个几何对象的颜色必须始终一致：

| 对象类型 | 推荐颜色 | 说明 |
|---------|---------|------|
| 基础图形边 | BLUE | 三角形、四边形的边 |
| 辅助线/虚线 | YELLOW / GRAY | `DashedLine` |
| 重要点 | RED | 题目中的关键点 |
| 对称点/新构造点 | GREEN | 通过对称、旋转等得到的 |
| 角度弧线/标记 | GREEN / ORANGE | 角度弧和标签 |
| 射线/延长线 | PURPLE / TEAL | 平分线、平行线 |
| 标签文字 | WHITE (默认) | 除非需要强调 |

## 坐标必须完全一致
```python
# ❌ 错误：Section 2 中用了不同的参数
# Section 1:
triangle = Polygon(A, B, C, color=BLUE)
self.place_in_area(triangle, 'B2', 'I8', scale_factor=0.85)

# Section 2 继承时 scale_factor 写成了 0.9 —— 会导致位置偏移！
# triangle = Polygon(A, B, C, color=BLUE)
# self.place_in_area(triangle, 'B2', 'I8', scale_factor=0.9)  # ❌

# ✅ 正确：完全复制前序代码中的参数
triangle = Polygon(A, B, C, color=BLUE)
self.place_in_area(triangle, 'B2', 'I8', scale_factor=0.85)  # ✅ 参数一致
```

## 字号一致性
- 顶点标签: `font_size=28`
- 角度标签: `font_size=28`
- 边长标签: `font_size=28`
- 标题等大字: `font_size=36`
- 不要在不同 Section 中使用不同字号

## 线宽一致性
- 基础图形边: `stroke_width=4` (Manim 默认)
- 辅助线: `stroke_width=2` 或 `stroke_width=3`
- 虚线: `dash_length=0.1`
- 不要在不同 Section 中修改相同线条的线宽

## `self.add()` vs `self.play()` 的视觉效果
- 继承对象用 `self.add()`: 场景开始时就已经存在，观众感觉图形延续了
- 新增对象用 `self.play(Create(...))`: 有动画效果，观众知道"这是新加的"
- **切勿反过来**: 继承对象如果用 `Create` 动画，观众会以为是新加的

## 布局稳定性
- 所有 Section 的 `place_in_area` 第一个调用参数范围建议用相同的网格区域
- 典型几何题推荐区域: `'B2'` 到 `'I8'`，给四周留出标签空间
- 如果后续 Section 需要更多空间（如新增外部点），可以缩小 `scale_factor` 但**所有 Section 一起改**

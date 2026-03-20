---
name: pptx
description: Use this skill any time a .pptx file is involved - creating, reading, editing presentations, pitch decks, slide shows.
metadata:
  deepcobot:
    emoji: "📊"
    requires:
      packages: ["python-pptx"]
---

# PPTX - PowerPoint 演示文稿

> **重要**: 所有脚本路径相对于此 skill 目录。

## 依赖安装

```bash
# Python 库
pip install python-pptx

# 命令行工具 (可选)
# macOS
brew install libreoffice poppler

# Ubuntu/Debian
apt-get install libreoffice poppler-utils
```

## 快速参考

| 任务 | 方法 |
|------|------|
| 读取内容 | `python-pptx` 或 `markitdown` |
| 创建演示文稿 | `python-pptx` |
| 编辑模板 | 解包 → 编辑 XML → 打包 |
| 转换图片 | `libreoffice` + `pdftoppm` |

## python-pptx - 基础操作

### 创建演示文稿
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# 创建演示文稿
prs = Presentation()

# 设置幻灯片尺寸 (16:9)
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

# 添加空白幻灯片
blank_layout = prs.slide_layouts[6]  # 空白布局
slide = prs.slides.add_slide(blank_layout)

# 添加标题幻灯片
title_layout = prs.slide_layouts[0]  # 标题布局
slide = prs.slides.add_slide(title_layout)
slide.shapes.title.text = "演示标题"
slide.placeholders[1].text = "副标题"

prs.save('presentation.pptx')
```

### 添加文本
```python
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

# 添加文本框
left = Inches(1)
top = Inches(2)
width = Inches(11)
height = Inches(1)

textbox = slide.shapes.add_textbox(left, top, width, height)
tf = textbox.text_frame
tf.word_wrap = True

# 添加文本
p = tf.paragraphs[0]
p.text = "标题文本"
p.font.size = Pt(44)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER

# 添加多个段落
p2 = tf.add_paragraph()
p2.text = "正文内容"
p2.font.size = Pt(24)
p2.level = 1  # 缩进级别
```

### 添加形状
```python
from pptx.enum.shapes import MSO_SHAPE

# 矩形
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(1), Inches(1),
    Inches(4), Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0, 112, 192)
shape.line.color.rgb = RGBColor(0, 0, 0)

# 圆形
circle = slide.shapes.add_shape(
    MSO_SHAPE.OVAL,
    Inches(6), Inches(1),
    Inches(2), Inches(2)
)

# 箭头
arrow = slide.shapes.add_shape(
    MSO_SHAPE.RIGHT_ARROW,
    Inches(4), Inches(3),
    Inches(3), Inches(0.5)
)
```

### 添加图片
```python
# 添加图片
pic = slide.shapes.add_picture(
    'image.png',
    Inches(1), Inches(1),
    width=Inches(5)
)

# 图片居中
pic.left = int((prs.slide_width - pic.width) / 2)
pic.top = int((prs.slide_height - pic.height) / 2)
```

### 添加表格
```python
# 添加表格
rows, cols = 4, 3
left = Inches(1)
top = Inches(2)
width = Inches(11)
height = Inches(3)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 设置列宽
table.columns[0].width = Inches(3)
table.columns[1].width = Inches(4)
table.columns[2].width = Inches(4)

# 填充数据
for i in range(rows):
    for j in range(cols):
        cell = table.cell(i, j)
        cell.text = f"单元格 {i+1}-{j+1}"
        cell.text_frame.paragraphs[0].font.size = Pt(14)
```

## 读取演示文稿
```python
from pptx import Presentation

prs = Presentation('presentation.pptx')

# 遍历幻灯片
for slide_num, slide in enumerate(prs.slides, 1):
    print(f"\n=== 幻灯片 {slide_num} ===")

    # 遍历形状
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                print(paragraph.text)

        if shape.has_table:
            print("表格内容:")
            for row in shape.table.rows:
                row_text = [cell.text for cell in row.cells]
                print(" | ".join(row_text))
```

## 设计建议

### 配色方案

| 主题 | 主色 | 辅色 | 强调色 |
|------|------|------|--------|
| **商务蓝** | `1E3A5F` | `4A90A4` | `FFFFFF` |
| **科技绿** | `2C5F2D` | `97BC62` | `F5F5F5` |
| **活力橙** | `F96167` | `F9E795` | `2F3C7E` |
| **简约灰** | `36454F` | `F2F2F2` | `212121` |

### 排版建议

1. **标题**: 36-44pt 加粗
2. **正文**: 14-16pt
3. **注释**: 10-12pt
4. **边距**: 至少 0.5 英寸
5. **间距**: 内容块之间 0.3-0.5 英寸

### 避免事项

- ❌ 单调的白色背景
- ❌ 居中对齐的正文
- ❌ 过小的字号
- ❌ 过多的文字堆砌
- ❌ 标题下方的装饰线（AI 生成特征）

## 常见布局

### 标题+内容
```
┌────────────────────────────┐
│          标题              │
├────────────────────────────┤
│                            │
│       主要内容区            │
│                            │
└────────────────────────────┘
```

### 两栏布局
```
┌─────────────┬──────────────┐
│             │              │
│   文字区    │    图片区    │
│             │              │
└─────────────┴──────────────┘
```

### 三列布局
```
┌───────┬───────┬───────┐
│  📊   │  📈   │  📉   │
│ 标题1 │ 标题2 │ 标题3 │
│ 描述  │ 描述  │ 描述  │
└───────┴───────┴───────┘
```

## 转换为图片

```bash
# 转换为 PDF
soffice --headless --convert-to pdf presentation.pptx

# PDF 转图片
pdftoppm -jpeg -r 150 presentation.pdf slide
# 生成 slide-01.jpg, slide-02.jpg 等

# 指定页面
pdftoppm -jpeg -r 150 -f 1 -l 3 presentation.pdf slide
```

## 示例：创建完整的演示文稿

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

# 幻灯片 1: 标题页
slide1 = prs.slides.add_slide(prs.slide_layouts[6])
title_box = slide1.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11.33), Inches(1))
tf = title_box.text_frame
p = tf.paragraphs[0]
p.text = "项目演示"
p.font.size = Pt(54)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER

subtitle_box = slide1.shapes.add_textbox(Inches(1), Inches(4), Inches(11.33), Inches(0.5))
tf = subtitle_box.text_frame
p = tf.paragraphs[0]
p.text = "2024 年度报告"
p.font.size = Pt(24)
p.alignment = PP_ALIGN.CENTER

# 幻灯片 2: 目录
slide2 = prs.slides.add_slide(prs.slide_layouts[6])
title = slide2.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
tf = title.text_frame
tf.paragraphs[0].text = "目录"
tf.paragraphs[0].font.size = Pt(36)

content = slide2.shapes.add_textbox(Inches(1), Inches(2), Inches(10), Inches(4))
tf = content.text_frame
for i, item in enumerate(["项目背景", "技术方案", "实施计划", "预期成果"]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"{i+1}. {item}"
    p.font.size = Pt(24)
    p.space_after = Pt(12)

prs.save('demo.pptx')
```
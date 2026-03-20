---
name: docx
description: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) - reports, memos, letters, templates, tracked changes, etc.
metadata:
  deepcobot:
    emoji: "📝"
    requires:
      packages: ["python-docx"]
      bins: ["pandoc"]
---

# DOCX - Word 文档处理

> **重要**: 所有脚本路径相对于此 skill 目录。
> 运行方式: `cd {this_skill_dir} && python scripts/...`

## 依赖安装

```bash
# Python 库
pip install python-docx

# 命令行工具 (可选)
# macOS
brew install pandoc libreoffice

# Ubuntu/Debian
apt-get install pandoc libreoffice
```

## 快速参考

| 任务 | 方法 |
|------|------|
| 读取内容 | `pandoc` 或 `python-docx` |
| 创建新文档 | `python-docx` 或 `docx-js` |
| 编辑现有文档 | 解包 → 编辑 XML → 打包 |
| 转换格式 | `libreoffice` 或 `pandoc` |

## python-docx - 基础操作

### 创建新文档
```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 添加标题
doc.add_heading('文档标题', level=0)

# 添加段落
p = doc.add_paragraph('这是正文内容。')

# 添加带格式的文本
run = p.add_run('加粗文本')
run.bold = True

# 添加列表
doc.add_paragraph('项目1', style='List Bullet')
doc.add_paragraph('项目2', style='List Bullet')
doc.add_paragraph('步骤1', style='List Number')
doc.add_paragraph('步骤2', style='List Number')

# 添加图片
doc.add_picture('image.png', width=Inches(4))

# 添加表格
table = doc.add_table(rows=3, cols=3)
for i, row in enumerate(table.rows):
    for j, cell in enumerate(row.cells):
        cell.text = f'单元格 {i+1}-{j+1}'

# 添加分页
doc.add_page_break()

doc.save('document.docx')
```

### 读取文档
```python
from docx import Document

doc = Document('document.docx')

# 读取段落
for para in doc.paragraphs:
    print(para.text)

# 读取表格
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)

# 读取样式
for para in doc.paragraphs:
    if para.style.name.startswith('Heading'):
        print(f'标题: {para.text}')
```

### 编辑文档
```python
from docx import Document

doc = Document('existing.docx')

# 修改段落
doc.paragraphs[0].text = '新的标题'

# 添加内容
doc.add_paragraph('新增段落')

# 修改表格单元格
doc.tables[0].rows[0].cells[0].text = '新的单元格内容'

doc.save('modified.docx')
```

## 格式和样式

### 段落格式
```python
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

para = doc.add_paragraph()

# 对齐
para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 缩进
para.paragraph_format.left_indent = Inches(0.5)
para.paragraph_format.first_line_indent = Inches(0.3)

# 行距
para.paragraph_format.line_spacing = 1.5

# 段前段后间距
para.paragraph_format.space_before = Pt(12)
para.paragraph_format.space_after = Pt(6)
```

### 字符格式
```python
run = para.add_run('格式化文本')

run.bold = True          # 加粗
run.italic = True        # 斜体
run.underline = True     # 下划线
run.font.size = Pt(14)   # 字号
run.font.name = 'Arial'  # 字体

# Windows 中文字体
run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
```

### 表格样式
```python
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT

table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

# 设置列宽
for col in table.columns:
    col.width = Inches(1.5)

# 单元格格式
cell = table.rows[0].cells[0]
cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in cell.paragraphs[0].runs:
    run.bold = True
```

## 页面设置

```python
from docx.shared import Inches
from docx.enum.section import WD_ORIENT

section = doc.sections[0]

# 页面尺寸
section.page_width = Inches(8.5)   # Letter 宽度
section.page_height = Inches(11)   # Letter 高度

# 横向
section.orientation = WD_ORIENT.LANDSCAPE

# 边距
section.left_margin = Inches(1)
section.right_margin = Inches(1)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
```

## 页眉页脚

```python
section = doc.sections[0]

# 页眉
header = section.header
header_para = header.paragraphs[0]
header_para.text = '页眉内容'

# 页脚
footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.text = '第 页'

# 添加页码需要更复杂的 XML 操作
```

## 命令行工具

### pandoc - 文本提取
```bash
# 转换为 Markdown
pandoc document.docx -o output.md

# 保留修订
pandoc --track-changes=all document.docx -o output.md
```

### LibreOffice - 格式转换
```bash
# 转换为 PDF
soffice --headless --convert-to pdf document.docx

# 转换旧格式 .doc
soffice --headless --convert-to docx document.doc
```

## 常见任务

### 创建报告模板
```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 标题
title = doc.add_heading('项目报告', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 元信息
meta = doc.add_paragraph()
meta.add_run('日期: ').bold = True
meta.add_run('2024-01-15\n')
meta.add_run('作者: ').bold = True
meta.add_run('张三')

# 目录（需要手动维护或使用 Word 功能）
doc.add_heading('目录', level=1)
doc.add_paragraph('1. 摘要')
doc.add_paragraph('2. 背景')
doc.add_paragraph('3. 分析')

# 正文
doc.add_heading('1. 摘要', level=1)
doc.add_paragraph('这是摘要内容...')

doc.add_heading('2. 背景', level=1)
doc.add_paragraph('这是背景内容...')

doc.save('report.docx')
```

### 批量替换文本
```python
from docx import Document

doc = Document('template.docx')

# 替换段落中的文本
for para in doc.paragraphs:
    if '{{name}}' in para.text:
        para.text = para.text.replace('{{name}}', '张三')
    if '{{date}}' in para.text:
        para.text = para.text.replace('{{date}}', '2024-01-15')

# 替换表格中的文本
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            if '{{amount}}' in cell.text:
                cell.text = cell.text.replace('{{amount}}', '10,000')

doc.save('output.docx')
```

## 注意事项

1. **不使用 `\n`**: 使用多个 Paragraph 元素
2. **不使用 Unicode 项目符号**: 使用 `List Bullet` 样式
3. **中文字体**: 需要单独设置东亚字体
4. **复杂格式**: 考虑使用模板文件
5. **性能**: 大文档考虑分段处理
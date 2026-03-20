---
name: pdf
description: Use this skill whenever the user wants to do anything with PDF files - reading, extracting, merging, splitting, rotating, watermarking, creating, filling forms, encrypting, OCR, and more.
metadata:
  deepcobot:
    emoji: "📄"
    requires:
      packages: ["pypdf", "pdfplumber", "reportlab"]
      bins: ["qpdf", "pdftotext"]
---

# PDF Processing Guide - PDF 处理指南

> **重要**: 所有脚本路径相对于此 skill 目录。
> 运行方式: `cd {this_skill_dir} && python scripts/...`

## 依赖安装

```bash
# Python 库
pip install pypdf pdfplumber reportlab pytesseract pdf2image

# 命令行工具 (macOS)
brew install poppler qpdf

# 命令行工具 (Ubuntu/Debian)
apt-get install poppler-utils qpdf
```

## 快速参考

| 任务 | 工具 | 命令/代码 |
|------|------|----------|
| 合并 PDF | pypdf | `writer.add_page(page)` |
| 拆分 PDF | pypdf | 逐页保存 |
| 提取文本 | pdfplumber | `page.extract_text()` |
| 提取表格 | pdfplumber | `page.extract_tables()` |
| 创建 PDF | reportlab | Canvas 或 Platypus |
| 命令行合并 | qpdf | `qpdf --empty --pages ...` |
| OCR 扫描件 | pytesseract | 先转图片再 OCR |

## Python 库使用

### pypdf - 基础操作

#### 读取 PDF
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
print(f"页数: {len(reader.pages)}")

# 提取文本
text = ""
for page in reader.pages:
    text += page.extract_text()
```

#### 合并 PDF
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### 拆分 PDF
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### 旋转页面
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # 顺时针旋转90度
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

#### 添加密码
```python
writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - 文本和表格提取

#### 提取文本（保留布局）
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### 提取表格
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"第 {i+1} 页，表格 {j+1}:")
            for row in table:
                print(row)
```

#### 表格转 Excel
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - 创建 PDF

#### 基础创建
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

c.drawString(100, height - 100, "Hello World!")
c.save()
```

#### 多页文档
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("标题", styles['Title']))
story.append(Spacer(1, 12))
story.append(Paragraph("正文内容...", styles['Normal']))
story.append(PageBreak())

doc.build(story)
```

## 命令行工具

### pdftotext (poppler-utils)
```bash
# 提取文本
pdftotext input.pdf output.txt

# 保留布局
pdftotext -layout input.pdf output.txt

# 指定页面范围
pdftotext -f 1 -l 5 input.pdf output.txt
```

### qpdf
```bash
# 合并 PDF
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# 拆分页面
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# 旋转页面
qpdf input.pdf output.pdf --rotate=+90:1

# 移除密码
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

## 高级功能

### OCR 扫描件
```python
import pytesseract
from pdf2image import convert_from_path

# PDF 转图片
images = convert_from_path('scanned.pdf')

# OCR 每页
text = ""
for i, image in enumerate(images):
    text += f"第 {i+1} 页:\n"
    text += pytesseract.image_to_string(image, lang='chi_sim+eng')
    text += "\n\n"
```

### 添加水印
```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### 提取图片
```bash
# 使用 pdfimages
pdfimages -j input.pdf output_prefix
# 生成 output_prefix-000.jpg, output_prefix-001.jpg 等
```

## 注意事项

1. **下标和上标**: 在 reportlab 中使用 `<sub>` 和 `<super>` 标签，不要用 Unicode 下标
2. **中文支持**: 需要注册中文字体
3. **大文件**: 使用 `read_only=True` 或分页处理
4. **公式值**: openpyxl 创建的文件公式值不计算，需要用 LibreOffice 重算
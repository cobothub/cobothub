---
name: xlsx
description: Use this skill any time a spreadsheet file is the primary input or output - create, read, edit, analyze, or convert Excel files (.xlsx, .xlsm, .csv, .tsv).
metadata:
  deepcobot:
    emoji: "📊"
    requires:
      packages: ["openpyxl", "pandas"]
---

# XLSX - Excel 文件处理

> **重要**: 所有脚本路径相对于此 skill 目录。
> 运行方式: `cd {this_skill_dir} && python scripts/...`

## 依赖安装

```bash
pip install openpyxl pandas
# 可选：公式重算需要 LibreOffice
```

## 快速参考

| 任务 | 推荐工具 | 说明 |
|------|---------|------|
| 数据分析 | pandas | 批量操作、统计 |
| 创建/编辑 | openpyxl | 公式、格式、图表 |
| 公式重算 | LibreOffice | 必须操作 |

## 核心原则

### ⚠️ 使用公式，而非硬编码值

❌ **错误 - 硬编码计算值**
```python
total = df['Sales'].sum()
sheet['B10'] = total  # 硬编码结果
```

✅ **正确 - 使用 Excel 公式**
```python
sheet['B10'] = '=SUM(B2:B9)'  # 使用公式
```

## pandas - 数据分析

### 读取 Excel
```python
import pandas as pd

# 读取默认工作表
df = pd.read_excel('file.xlsx')

# 读取所有工作表
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)

# 读取特定列
df = pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])

# 指定数据类型
df = pd.read_excel('file.xlsx', dtype={'id': str, 'amount': float})
```

### 数据分析
```python
df.head()      # 预览数据
df.info()      # 列信息
df.describe()  # 统计摘要

# 筛选
df[df['column'] > 100]
df.query('column > 100 and column2 == "value"')

# 分组统计
df.groupby('category').sum()
df.pivot_table(values='amount', index='category', columns='month')
```

### 写入 Excel
```python
df.to_excel('output.xlsx', index=False)

# 多个工作表
with pd.ExcelWriter('output.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1', index=False)
    df2.to_excel(writer, sheet_name='Sheet2', index=False)
```

## openpyxl - 创建和编辑

### 创建新文件
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = Workbook()
sheet = wb.active

# 添加数据
sheet['A1'] = '姓名'
sheet['B1'] = '金额'

# 添加公式
sheet['B10'] = '=SUM(B2:B9)'
sheet['C2'] = '=B2*1.1'  # 增长10%

# 格式化
sheet['A1'].font = Font(bold=True, color='0000FF')
sheet['A1'].fill = PatternFill('solid', fgColor='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# 设置列宽
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### 编辑现有文件
```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active

# 修改单元格
sheet['A1'] = '新值'

# 插入行/列
sheet.insert_rows(2)
sheet.insert_cols(3)

# 删除行/列
sheet.delete_rows(5)
sheet.delete_cols(2)

# 添加新工作表
new_sheet = wb.create_sheet('NewSheet')

wb.save('modified.xlsx')
```

### 读取公式值（需要 LibreOffice 重算）
```python
# 读取公式（返回公式字符串）
wb = load_workbook('file.xlsx')
sheet['B10'].value  # 返回 '=SUM(B2:B9)'

# 读取计算值
wb = load_workbook('file.xlsx', data_only=True)
sheet['B10'].value  # 返回计算结果
```

## 格式规范

### 颜色编码标准（财务模型）

| 颜色 | RGB | 用途 |
|------|-----|------|
| 蓝色 | 0,0,255 | 硬编码输入值 |
| 黑色 | 0,0,0 | 公式和计算 |
| 绿色 | 0,128,0 | 工作表内引用 |
| 红色 | 255,0,0 | 外部文件引用 |
| 黄色背景 | 255,255,0 | 需要注意的假设 |

### 数字格式

```python
# 货币格式
sheet['A1'].number_format = '$#,##0.00'

# 百分比
sheet['B1'].number_format = '0.0%'

# 千分位
sheet['C1'].number_format = '#,##0'

# 自定义格式（零显示为"-"）
sheet['D1'].number_format = '$#,##0;($#,##0);-'
```

## 公式验证清单

- [ ] 测试 2-3 个示例引用是否正确
- [ ] 列映射：确认 Excel 列号（如第64列是BL，不是BK）
- [ ] 行偏移：DataFrame 第5行 = Excel 第6行
- [ ] NaN 处理：使用 `pd.notna()` 检查空值
- [ ] 除零检查：除法公式前检查分母
- [ ] 跨表引用：使用正确格式 `Sheet1!A1`

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| #REF! | 无效单元格引用 | 检查引用范围 |
| #DIV/0! | 除以零 | 添加 IF 判断 |
| #VALUE! | 错误数据类型 | 检查数据格式 |
| #NAME? | 未知的公式名 | 检查拼写 |
| #N/A | 找不到值 | 使用 IFERROR 包装 |

## 最佳实践

1. **先读后改**: 编辑前先分析现有格式
2. **公式优先**: 让 Excel 计算而非 Python
3. **格式一致**: 保持现有模板的风格
4. **验证结果**: 检查公式错误和计算结果
5. **备份数据**: 修改前保存原始文件
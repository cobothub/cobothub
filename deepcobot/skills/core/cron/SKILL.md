---
name: cron
description: Schedule reminders and recurring tasks with natural language support.
metadata:
  deepcobot:
    emoji: "⏰"
    requires: {}
---

# Cron - 定时任务管理

通过自然语言创建、管理定时任务。

## 三种模式

1. **reminder** - 直接发送消息提醒用户
2. **task** - 定时让 Agent 执行任务并返回结果
3. **one-time** - 一次性定时任务，执行后自动删除

## 使用示例

### 固定提醒
```
每天早上9点提醒我开会
每20分钟提醒我休息一下
工作日下午5点提醒我下班
```

### 动态任务（Agent 执行）
```
每天早上8点检查我的待办事项
每小时检查 GitHub PR 状态
每周一早上汇总上周工作
```

### 一次性任务
```
下午3点提醒我打电话
明天早上10点提醒我开会
```

## 时间表达方式

| 用户描述 | 参数转换 |
|---------|---------|
| 每20分钟 | `every_seconds: 1200` |
| 每小时 | `every_seconds: 3600` |
| 每天8点 | `cron_expr: "0 8 * * *"` |
| 工作日下午5点 | `cron_expr: "0 17 * * 1-5"` |
| 指定时间（一次性） | `at: ISO datetime` |

## CLI 命令

```bash
# 列出所有任务
deepcobot cron list

# 查看任务详情
deepcobot cron get <job_id>

# 删除任务
deepcobot cron delete <job_id>

# 暂停/恢复任务
deepcobot cron pause <job_id>
deepcobot cron resume <job_id>

# 立即执行一次
deepcobot cron run <job_id>
```

## Cron 表达式参考

```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日 (1 - 31)
│ │ │ ┌───────────── 月 (1 - 12)
│ │ │ │ ┌───────────── 星期几 (0 - 6, 0 = 周日)
│ │ │ │ │
* * * * *

示例:
0 9 * * *      # 每天 9:00
0 */2 * * *    # 每 2 小时
30 8 * * 1-5   # 工作日 8:30
0 0 * * 0      # 每周日零点
*/15 * * * *   # 每 15 分钟
```

## 时区支持

使用 IANA 时区名称设置时区：
- Asia/Shanghai
- America/New_York
- Europe/London
- UTC
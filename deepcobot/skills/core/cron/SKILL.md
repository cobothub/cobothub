---
name: cron
description: Manage scheduled tasks with deepcobot cron CLI - create, list, remove, and run tasks.
metadata:
  deepcobot:
    emoji: "⏰"
    requires: {}
---

# Cron - 定时任务管理

使用 `deepcobot cron` 命令管理定时任务。

## CLI 命令

### 列出任务
```bash
deepcobot cron list           # 列出所有启用的任务
deepcobot cron list --all     # 列出所有任务（包括禁用的）
```

### 添加任务
```bash
# 间隔执行（简单格式）
deepcobot cron add "任务名称" "发送给 Agent 的消息" --every 1h

# Cron 表达式
deepcobot cron add "每日报告" "生成今日报告" --cron "0 9 * * *"

# 指定结果发送渠道
deepcobot cron add "定时提醒" "检查待办事项" --every 30m --channel telegram --chat-id 123456789
```

### 删除任务
```bash
deepcobot cron remove <job_id>
```

### 立即执行
```bash
deepcobot cron run <job_id>
```

## 时间格式

### 间隔格式 (--every)

支持简单间隔和复合格式：

| 格式 | 说明 |
|------|------|
| `30s` | 每 30 秒 |
| `5m` | 每 5 分钟 |
| `1h` | 每 1 小时 |
| `1d` | 每 1 天 |
| `2h30m` | 每 2 小时 30 分钟 |

### Cron 表达式 (--cron)

标准 5 字段 cron 表达式：

```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日 (1 - 31)
│ │ │ ┌───────────── 月 (1 - 12)
│ │ │ │ ┌───────────── 星期几 (0 - 6, 0 = 周日)
│ │ │ │ │
* * * * *
```

**常用示例：**

| 表达式 | 说明 |
|--------|------|
| `0 9 * * *` | 每天 9:00 |
| `0 */2 * * *` | 每 2 小时 |
| `30 8 * * 1-5` | 工作日 8:30 |
| `0 0 * * 0` | 每周日零点 |
| `*/15 * * * *` | 每 15 分钟 |

## 完整参数

```bash
deepcobot cron add <name> <message> [options]

参数:
  name                  任务名称
  message               发送给 Agent 的消息

选项:
  --every, -e TEXT      间隔时间 (如: 30m, 1h, 1d)
  --cron TEXT           Cron 表达式 (5 字段)
  --channel TEXT        结果发送渠道 (如: telegram, discord)
  --chat-id TEXT        结果发送目标 ID
  --timeout, -t INT     执行超时秒数 (默认: 120)
  --config, -c PATH     配置文件路径
```

## 使用示例

### 每小时检查
```bash
deepcobot cron add "每小时检查" "检查系统状态并报告" --every 1h
```

### 每日早晨任务
```bash
deepcobot cron add "早安问候" "早安！今天有什么计划？" --cron "0 8 * * *" --channel telegram --chat-id 123456789
```

### 工作日提醒
```bash
deepcobot cron add "下班提醒" "别忘了提交今日工作日志" --cron "0 18 * * 1-5"
```

### 定期清理
```bash
deepcobot cron add "每周清理" "清理临时文件和缓存" --cron "0 10 * * 6" --timeout 300
```

## 任务管理流程

1. **创建任务**：使用 `cron add` 命令创建
2. **查看任务**：使用 `cron list` 列出所有任务
3. **测试任务**：使用 `cron run <job_id>` 立即执行测试
4. **删除任务**：使用 `cron remove <job_id>` 删除不需要的任务

## 注意事项

- 当任务执行时，Agent 会收到 `message` 中的消息
- 如果指定了 `--channel` 和 `--chat-id`，结果会发送到指定渠道
- 任务存储在 `~/.deepcobot/cron_jobs.json` 文件中
- 使用 `--config` 可以指定不同的配置文件
---
name: cron
description: Manage scheduled tasks with deepcobot cron CLI - add, list, remove, enable, disable tasks.
metadata:
  deepcobot:
    emoji: "⏰"
    requires: {}
---

# Cron - 定时任务管理

使用 `deepcobot cron` CLI 管理定时任务。

**重要提示**：这些 CLI 命令只操作任务存储文件，不会启动调度服务。
调度服务需要通过 `deepcobot bot` 或 `deepcobot serve` 启动。
服务会自动检测文件变化并加载新任务。

## CLI 命令

### 列出任务
```bash
deepcobot cron list           # 列出所有启用的任务
deepcobot cron list --all     # 列出所有任务（包括禁用的）
```

### 添加任务
```bash
# 间隔执行
deepcobot cron add "任务名称" "发送给 Agent 的消息" --every 1h

# Cron 表达式
deepcobot cron add "每日报告" "生成今日报告" --cron "0 9 * * *"

# 指定结果发送渠道
deepcobot cron add "定时提醒" "检查待办事项" \
    --every 30m \
    --channel telegram \
    --chat-id 123456789
```

### 启用/禁用任务
```bash
deepcobot cron enable <job_id>    # 启用任务
deepcobot cron disable <job_id>   # 禁用任务
```

### 删除任务
```bash
deepcobot cron remove <job_id>
```

### 立即执行
```bash
deepcobot cron run <job_id>   # 标记任务立即执行
```

### 查看状态
```bash
deepcobot cron status         # 显示服务状态和任务统计
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

## 工作流程

1. **启动调度服务**：
   ```bash
   # 方式一：启动 bot（包含调度服务）
   deepcobot bot

   # 方式二：启动 LangGraph 服务
   deepcobot serve
   ```

2. **添加任务**：
   ```bash
   deepcobot cron add "每日提醒" "早安！" --cron "0 8 * * *" --channel telegram --chat-id 123456
   ```

3. **服务自动感知**：
   - 服务每 5 秒检测存储文件变化
   - 新任务会自动加载并调度

## 完整参数

```bash
deepcobot cron add <name> <message> [options]

参数:
  name                  任务名称
  message               发送给 Agent 的消息

选项:
  --every, -e TEXT      间隔时间 (如: 30s, 5m, 1h, 1d, 2h30m)
  --cron TEXT           Cron 表达式 (5 字段)
  --channel TEXT        结果发送渠道 (如: telegram, discord)
  --chat-id TEXT        结果发送目标 ID
  --timeout, -t INT     执行超时秒数 (默认: 120)
  --config, -c PATH     配置文件路径
```

## 使用示例

### 定时问候
```bash
deepcobot cron add "早安问候" "早安！今天有什么计划？" \
    --cron "0 8 * * *" \
    --channel telegram \
    --chat-id 123456789
```

### 定期检查
```bash
deepcobot cron add "系统检查" "检查系统状态" --every 1h
```

### 工作日提醒
```bash
deepcobot cron add "下班提醒" "别忘了提交工作日志" \
    --cron "0 18 * * 1-5"
```

## 任务存储

- 任务保存在 `~/.deepcobot/cron_jobs.json`
- CLI 命令直接操作此文件
- 调度服务通过轮询检测文件变化

## 配置文件预定义任务

也可以在配置文件中预定义任务：

```toml
[cron]
enabled = true

[[cron.jobs]]
name = "每日报告"
schedule = "0 9 * * *"
message = "生成今日报告"
channel = "telegram"
chat_id = "123456789"
```

## 注意事项

- 调度服务未启动时，任务不会执行
- 使用 `deepcobot cron status` 检查服务状态
- 任务执行结果会发送到 `--channel` 和 `--chat-id` 指定的目标
- 如未指定投递目标，任务会静默执行
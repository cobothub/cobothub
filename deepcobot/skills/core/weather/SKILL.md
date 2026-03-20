---
name: weather
description: Get current weather and forecasts without API key.
homepage: https://wttr.in/:help
metadata:
  deepcobot:
    emoji: "🌤️"
    requires:
      bins: ["curl"]
---

# Weather - 天气查询

两个免费天气服务，无需 API Key。

## wttr.in (主要推荐)

### 快速查询
```bash
curl -s "wttr.in/Beijing?format=3"
# 输出: Beijing: ⛅️ +8°C
```

### 简洁格式
```bash
curl -s "wttr.in/Shanghai?format=%l:+%c+%t+%h+%w"
# 输出: Shanghai: ⛅️ +8°C 71% ↙5km/h
```

### 完整天气预报
```bash
curl -s "wttr.in/Guangzhou?T"
# 显示完整的3天天气预报
```

### 返回图片（适合发送到聊天）
```bash
curl -s "wttr.in/Shenzhen.png" -o /tmp/weather.png
```

## 格式代码

| 代码 | 含义 |
|------|------|
| `%c` | 天气状况图标 |
| `%t` | 温度 |
| `%h` | 湿度 |
| `%w` | 风速风向 |
| `%l` | 位置 |
| `%m` | 月相 |

## 常用选项

| 选项 | 说明 |
|------|------|
| `?0` | 仅当前天气 |
| `?1` | 仅今天 |
| `?m` | 公制单位（默认） |
| `?u` | 英制单位 |
| `?T` | 终端格式（无颜色） |

## Open-Meteo (备用，JSON 格式)

免费、无需 API Key，适合程序化处理：

```bash
# 先获取城市坐标，再查询天气
curl -s "https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&current_weather=true"
```

返回 JSON 格式，包含温度、风速、天气代码等。

常用城市坐标：
| 城市 | 纬度 | 经度 |
|------|------|------|
| 北京 | 39.9 | 116.4 |
| 上海 | 31.2 | 121.5 |
| 广州 | 23.1 | 113.3 |
| 深圳 | 22.5 | 114.1 |
| 杭州 | 30.3 | 120.2 |

文档: https://open-meteo.com/en/docs

## 使用建议

1. 用户问"今天天气怎么样"时，使用 `wttr.in/城市名?format=3` 获取简洁信息
2. 用户需要详细预报时，使用 `wttr.in/城市名?T` 获取完整信息
3. 如果需要发送天气图片，使用 `.png` 格式
4. URL 编码城市名中的空格：`New+York` 或 `New%20York`
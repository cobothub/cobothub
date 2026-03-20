---
name: news
description: Look up the latest news from specified sources - tech, finance, world, sports, entertainment. Summarize headlines for users.
metadata:
  deepcobot:
    emoji: "📰"
    requires: {}
---

# News - 新闻聚合

当用户询问"最新新闻"、"今天有什么新闻"或"某类新闻"时，使用此 skill 抓取并汇总新闻。

## 新闻来源

### 中文新闻源

| 类别 | 来源 | URL |
|------|------|-----|
| **科技** | 科技日报 | https://www.stdaily.com/ |
| **科技** | 36氪 | https://36kr.com/newsflashes |
| **科技** | InfoQ | https://www.infoq.cn/ |
| **财经** | 经济日报 | http://www.ce.cn/ |
| **财经** | 新浪财经 | https://finance.sina.com.cn/ |
| **社会** | 中国新闻网 | https://www.chinanews.com/ |
| **国际** | CGTN | https://www.cgtn.com/ |
| **体育** | 央视体育 | https://sports.cctv.com/ |
| **娱乐** | 新浪娱乐 | https://ent.sina.com.cn/ |

### 英文新闻源

| 类别 | 来源 | URL |
|------|------|-----|
| **Tech** | Hacker News | https://news.ycombinator.com/ |
| **Tech** | TechCrunch | https://techcrunch.com/ |
| **Tech** | The Verge | https://www.theverge.com/ |
| **World** | BBC | https://www.bbc.com/news |
| **World** | Reuters | https://www.reuters.com/ |
| **Finance** | Bloomberg | https://www.bloomberg.com/ |
| **Finance** | CNBC | https://www.cnbc.com/ |

## AI 领域新闻（中文）

| 来源 | URL | 说明 |
|------|-----|------|
| 机器之心 | https://www.jiqizhixin.com/ | AI 技术资讯 |
| 新智元 | https://www.jiqizhixin.com/ | AI 行业动态 |
| 量子位 | https://www.qbitai.com/ | AI 前沿技术 |
| InfoQ AI | https://www.infoq.cn/topic/ai | AI 技术文章 |

## AI 领域新闻（英文）

| 来源 | URL | 说明 |
|------|-----|------|
| AI News | https://artificialintelligence-news.com/ | AI 行业新闻 |
| VentureBeat AI | https://venturebeat.com/category/ai/ | AI 商业动态 |
| MIT TR AI | https://www.technologyreview.com/topic/artificial-intelligence/ | MIT 技术评论 |
| r/MachineLearning | https://www.reddit.com/r/MachineLearning/ | ML 社区讨论 |

## 使用方法

### 1. 确定用户需求

询问用户想了解哪个类别的新闻：
- 科技 / Tech
- 财经 / Finance
- 国际 / World
- 体育 / Sports
- 娱乐 / Entertainment
- AI（特别关注）

### 2. 获取网页内容

使用浏览器工具或 curl 获取页面：

```bash
# 使用 curl 获取页面
curl -s "https://news.ycombinator.com/" | grep -oP '<a[^>]*class="storylink"[^>]*>[^<]*</a>' | head -10

# 获取科技日报首页
curl -s "https://www.stdaily.com/"
```

### 3. 提取标题

从页面中提取标题和链接，按重要性排序。

### 4. 汇总回复

简洁格式返回：

```
📰 今日新闻速递

## 科技
1. [标题1] - 来源 | 时间
   简要描述...

2. [标题2] - 来源 | 时间
   简要描述...

## AI 领域
1. [标题] - 来源
   ...

---
来源链接: [原文链接]
```

## 快速新闻命令

### Hacker News 热门
```bash
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | \
  jq '.[:10]' | \
  jq -c '.[]' | \
  while read id; do
    curl -s "https://hacker-news.firebaseio.com/v0/item/${id}.json" | \
    jq -r '"\(.title) - \(.url // "https://news.ycombinator.com/item?id=\(.id)")"'
  done
```

### 获取 RSS Feed
```bash
# 使用 curl 和 xpath 解析 RSS
curl -s "https://feeds.bbci.co.uk/news/rss.xml" | \
  grep -oP '<title><!\[CDATA\[(.*?)\]\]></title>' | \
  sed 's/<title><!\[CDATA\[//;s/\]\]><\/title>//' | \
  head -10
```

### 36氪 快讯
```bash
curl -s "https://36kr.com/newsflashes" | \
  grep -oP '<a[^>]*class="item-title"[^>]*>[^<]*</a>' | \
  sed 's/<[^>]*>//g' | \
  head -10
```

## 提示

1. **平衡来源**: 同一类别提供多个来源
2. **时效性**: 优先显示最近的新闻
3. **简洁**: 每条新闻一句话概括
4. **链接**: 提供原文链接供用户深入了解
5. **本地化**: 根据用户语言选择新闻源

## 高级功能

### 新闻对比（多视角）
同一事件从多个来源获取报道，对比不同视角。

### 关键词追踪
追踪特定关键词的新闻更新：
- 公司名称
- 技术主题
- 行业动态

### 定期推送
结合 cron skill 实现每日新闻推送到指定频道。
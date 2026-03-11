---
name: search-brave
description: Brave Search API 综合搜索技能。支持网页搜索、视频搜索、图片搜索、新闻搜索、AI接地(RAG)、AI答案生成、本地POI查询、查询建议和拼写检查。当用户需要搜索互联网、获取实时信息、进行RAG接地、查找本地商家或需要AI生成答案时，请主动使用此技能。
---

# Brave Search API 综合搜索技能

Brave Search API 提供强大的搜索能力，包括传统搜索和 AI 增强功能。

> **API Key 配置**: 在 `~/.c4alpha/config.toml` 中配置:
> ```toml
> [[search.providers]]
> name = "brave"
> api-key = "your-api-key-here"
> ```
>
> **获取 API Key**: https://api.search.brave.com
>
> **认证方式**: `X-Subscription-Token: <API_KEY>` header

## 功能选择指南

根据你的需求选择合适的端点：

| 需求场景 | 推荐端点 | 说明 |
|----------|----------|------|
| 通用网页搜索 | **web-search** | 最全面的搜索，返回链接、摘要、结构化数据 |
| 查找视频 | **videos-search** | 专注视频结果，含时长、观看数、创作者信息 |
| 查找图片 | **images-search** | 图片搜索，最多返回 200 张，含尺寸信息 |
| 查找新闻 | **news-search** | 新闻文章，支持时间过滤和日期范围 |
| LLM/AI 接地 | **llm-context** | 返回预提取的网页内容，用于 RAG/Agent |
| AI 生成答案 | **answers** | OpenAI 兼容的 AI 答案，带引用 |
| 本地商家查询 | **local-pois** | 获取商家详情（评分、营业时间、联系方式） |
| 商家描述 | **local-descriptions** | AI 生成的 POI 描述文本 |
| 查询补全 | **suggest** | 搜索框自动补全，<100ms 响应 |
| 拼写纠正 | **spellcheck** | 独立拼写检查 |

## 快速决策流程

```
需要什么类型的结果？
├── 网页/综合 → web-search
├── 视频 → videos-search
├── 图片 → images-search
├── 新闻 → news-search
├── AI 相关
│   ├── 需要 LLM 接地内容 → llm-context
│   └── 需要完整 AI 答案 → answers
├── 本地/商家
│   ├── 需要结构化信息 → local-pois (需先 web-search 获取 ID)
│   └── 需要描述文本 → local-descriptions
├── 输入辅助
│   ├── 自动补全 → suggest
│   └── 拼写检查 → spellcheck
```

## 代码使用

使用 `scripts/brave_search_client.py` 中的 `BraveSearchClient` 类来调用 API：

```python
from scripts.brave_search_client import BraveSearchClient

# 初始化客户端（会自动从 ~/.c4alpha/config.toml 读取 API Key）
client = BraveSearchClient()

# 网页搜索
results = client.web_search("python tutorials", count=10)

# 视频搜索
videos = client.videos_search("rust programming")

# 图片搜索
images = client.images_search("landscape photography")

# 新闻搜索（过去7天）
news = client.news_search("AI news", freshness="pw")

# LLM 接地 / RAG
context = client.llm_context("what is machine learning")

# 查询建议
suggestions = client.suggest("how to")
```

## 共用参数说明

### 通用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `q` | string | - | **必填**，搜索查询（1-400 字符，最多 50 词） |
| `country` | string | `US` | 搜索国家（2 字母国家代码或 `ALL`） |
| `search_lang` | string | `en` | 语言偏好（2+ 字符语言代码） |
| `safesearch` | string | `moderate` | 成人内容过滤（`off`/`moderate`/`strict`） |
| `spellcheck` | bool | `true` | 自动纠正查询 |

### 时间过滤 (freshness)

| 值 | 说明 |
|----|------|
| `pd` | 过去 24 小时 |
| `pw` | 过去 7 天 |
| `pm` | 过去 31 天 |
| `py` | 过去 365 天 |
| `YYYY-MM-DDtoYYYY-MM-DD` | 自定义日期范围 |

### 搜索操作符

| 操作符 | 语法 | 说明 |
|--------|------|------|
| 站点限定 | `site:example.com` | 限定特定域名 |
| 文件类型 | `ext:pdf` | 特定文件扩展名 |
| 标题包含 | `intitle:关键词` | 标题含关键词 |
| 精确匹配 | `"精确短语"` | 完全匹配 |
| 排除 | `-关键词` | 排除含该词的结果 |

## Goggles 自定义排名（Brave 独有）

Goggles 允许你自定义搜索结果的排序规则。

**语法**: `$boost=N` / `$downrank=N` (1-10), `$discard`, `$site=example.com`

**使用方式**:
```bash
# 托管 Goggles（需注册）
--data-urlencode "goggles=https://raw.githubusercontent.com/.../goggle.goggle"

# 内联规则（无需注册）
--data-urlencode 'goggles=$discard\n$site=docs.python.org\n$site=developer.mozilla.org'
```

**常见规则**:
- **白名单**: `$discard\n$site=docs.python.org\n$site=developer.mozilla.org`
- **黑名单**: `$discard,site=pinterest.com\n$discard,site=quora.com`

## 位置感知头

用于获取位置相关的搜索结果：

| Header | 类型 | 说明 |
|--------|------|------|
| `X-Loc-Lat` | float | 纬度 (-90.0 到 90.0) |
| `X-Loc-Long` | float | 经度 (-180.0 到 180.0) |
| `X-Loc-City` | string | 城市名 |
| `X-Loc-State` | string | 州/区域代码 |
| `X-Loc-Country` | string | 2 字母国家代码 |

> **优先级**: `X-Loc-Lat` + `X-Loc-Long` 优先。提供坐标时，文本位置头不参与解析。

## 通用请求示例

```bash
# 基础网页搜索
curl -s "https://api.search.brave.com/res/v1/web/search?q=python+tutorials" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"

# 带参数的搜索
curl -s "https://api.search.brave.com/res/v1/web/search" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -G \
  --data-urlencode "q=rust programming" \
  --data-urlencode "country=US" \
  --data-urlencode "search_lang=en" \
  --data-urlencode "count=10" \
  --data-urlencode "freshness=pm"
```

## 详细 API 参考

各功能的完整文档请参考对应的 reference 文件：

| Reference | 说明 |
|-----------|------|
| [references/web-search.md](references/web-search.md) | 网页搜索完整参数和响应格式 |
| [references/videos-search.md](references/videos-search.md) | 视频搜索详细文档 |
| [references/images-search.md](references/images-search.md) | 图片搜索详细文档 |
| [references/news-search.md](references/news-search.md) | 新闻搜索详细文档 |
| [references/llm-context.md](references/llm-context.md) | LLM 接地/RAG 详细文档 |
| [references/answers.md](references/answers.md) | AI 答案生成详细文档 |
| [references/local-pois.md](references/local-pois.md) | 本地 POI 查询详细文档 |
| [references/local-descriptions.md](references/local-descriptions.md) | POI 描述详细文档 |
| [references/suggest.md](references/suggest.md) | 查询建议详细文档 |
| [references/spellcheck.md](references/spellcheck.md) | 拼写检查详细文档 |

## 常见使用场景

### 场景 1: 构建搜索界面
```
用户输入 → suggest (补全建议)
        → web-search (执行搜索)
        → 可选: videos-search / images-search (分类结果)
```

### 场景 2: AI Agent / RAG 系统
```
用户问题 → llm-context (获取接地内容)
        → 处理内容生成回答
```

### 场景 3: 深度研究
```
研究主题 → answers (enable_research=true)
        → 获取多轮搜索的综合答案
```

### 场景 4: 本地商家查询
```
商家搜索 → web-search (result_filter=locations)
        → local-pois (获取详细信息)
        → local-descriptions (获取描述)
```

## 计划说明

| 功能 | 所需计划 |
|------|----------|
| web-search, videos-search, images-search, news-search | Search |
| llm-context | Search |
| local-pois, local-descriptions | Search |
| answers | Answers |
| suggest | Suggest |
| spellcheck | Spellcheck |

查看订阅: https://api-dashboard.search.brave.com/app/subscriptions/subscribe

# Web Search 详细文档

主要的网页搜索端点，返回最全面的结果集。

## 端点

```http
GET https://api.search.brave.com/res/v1/web/search
POST https://api.search.brave.com/res/v1/web/search
```

**认证**: `X-Subscription-Token: <API_KEY>` header

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | **是** | - | 搜索查询（1-400 字符，最多 50 词） |
| `country` | string | 否 | `US` | 搜索国家（2 字母国家代码或 `ALL`） |
| `search_lang` | string | 否 | `en` | 语言偏好（2+ 字符语言代码） |
| `ui_lang` | string | 否 | `en-US` | UI 语言 |
| `count` | int | 否 | `20` | 每页最大结果数（1-20） |
| `offset` | int | 否 | `0` | 分页偏移（0-9） |
| `safesearch` | string | 否 | `moderate` | 成人内容过滤（`off`/`moderate`/`strict`） |
| `freshness` | string | 否 | - | 时间过滤（`pd`/`pw`/`pm`/`py` 或日期范围） |
| `text_decorations` | bool | 否 | `true` | 包含高亮标记 |
| `spellcheck` | bool | 否 | `true` | 自动纠正查询 |
| `result_filter` | string | 否 | - | 过滤结果类型（逗号分隔） |
| `goggles` | string | 否 | - | 自定义排名过滤 |
| `extra_snippets` | bool | 否 | - | 每个结果最多 5 个额外摘要 |
| `operators` | bool | 否 | `true` | 应用搜索操作符 |
| `units` | string | 否 | - | 度量单位（`metric`/`imperial`） |
| `enable_rich_callback` | bool | 否 | `false` | 启用富数据回调 |
| `include_fetch_metadata` | bool | 否 | `false` | 包含抓取时间戳 |

### 结果过滤器值

可用类型: `discussions`, `faq`, `infobox`, `news`, `query`, `videos`, `web`, `locations`

```bash
# 仅返回网页和视频结果
curl "...&result_filter=web,videos"
```

## 响应格式

```json
{
  "type": "search",
  "query": {
    "original": "python frameworks",
    "altered": "python web frameworks",
    "spellcheck_off": false,
    "more_results_available": true
  },
  "web": {
    "type": "search",
    "results": [
      {
        "title": "Top Python Web Frameworks",
        "url": "https://example.com/python-frameworks",
        "description": "A comprehensive guide...",
        "age": "2 days ago",
        "language": "en",
        "meta_url": {
          "scheme": "https",
          "netloc": "example.com",
          "hostname": "example.com",
          "path": "/python-frameworks"
        },
        "thumbnail": {
          "src": "https://...",
          "original": "https://original-image-url.com/img.jpg"
        },
        "extra_snippets": ["Additional excerpt 1...", "Additional excerpt 2..."]
      }
    ],
    "family_friendly": true
  },
  "mixed": {
    "type": "mixed",
    "main": [
      {"type": "web", "index": 0, "all": false},
      {"type": "videos", "all": true}
    ],
    "top": [],
    "side": []
  },
  "videos": { "...": "..." },
  "news": { "...": "..." }
}
```

### 主要响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 总是 `"search"` |
| `query.original` | string | 原始搜索查询 |
| `query.altered` | string? | 拼写纠正后的查询 |
| `query.more_results_available` | bool | 是否有更多结果 |
| `web.results[].title` | string | 页面标题 |
| `web.results[].url` | string | 页面 URL |
| `web.results[].description` | string? | 摘要文本 |
| `web.results[].age` | string? | 可读年龄（如 "2 days ago"） |
| `web.results[].language` | string? | 内容语言 |
| `web.results[].thumbnail` | object? | 缩略图信息 |
| `web.results[].extra_snippets` | list? | 额外摘要 |
| `web.results[].schemas` | list? | schema.org 结构化数据 |
| `mixed` | object | 推荐显示顺序 |

### Mixed Response 说明

`mixed` 对象定义跨类型结果的推荐显示顺序：

| 数组 | 用途 |
|------|------|
| `main` | 主要结果列表 |
| `top` | 显示在主结果上方 |
| `side` | 侧边显示（如信息框） |

## 富数据回调

对于天气、股票、体育等查询：

```bash
# 1. 启用富数据回调
curl "...&q=weather+san+francisco&enable_rich_callback=true"

# 响应包含: "rich": {"hint": {"callback_key": "abc123...", "vertical": "weather"}}

# 2. 使用回调键获取富数据
curl "https://api.search.brave.com/res/v1/web/rich?callback_key=abc123..."
```

**支持的富数据类型**: 计算器、定义、单位转换、股票、货币、加密货币、天气、体育赛事等

## 使用场景

- **通用搜索集成**: 一次调用获取最丰富的结果集
- **结构化数据提取**: 通过 `schemas` 和类型化字段获取产品、食谱、评分等
- **自定义搜索**: 使用 Goggles 进行完全自定义的排名

# News Search 详细文档

专注于新闻文章的搜索端点。

## 端点

```http
GET https://api.search.brave.com/res/v1/news/search
POST https://api.search.brave.com/res/v1/news/search
```

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | **是** | - | 搜索查询 |
| `country` | string | 否 | `US` | 搜索国家 |
| `search_lang` | string | 否 | `en` | 语言偏好 |
| `ui_lang` | string | 否 | `en-US` | UI 语言 |
| `count` | int | 否 | `20` | 结果数量（1-50） |
| `offset` | int | 否 | `0` | 分页偏移（0-9） |
| `safesearch` | string | 否 | `strict` | 成人内容过滤 |
| `freshness` | string | 否 | - | 时间过滤 |
| `spellcheck` | bool | 否 | `true` | 自动纠正 |
| `extra_snippets` | bool | 否 | - | 每个结果最多 5 个额外摘要 |
| `goggles` | string/array | 否 | - | 自定义排名过滤 |
| `operators` | bool | 否 | `true` | 应用搜索操作符 |
| `include_fetch_metadata` | bool | 否 | `false` | 包含抓取时间戳 |

## 响应格式

```json
{
  "type": "news",
  "query": {
    "original": "space exploration"
  },
  "results": [
    {
      "type": "news_result",
      "title": "New Developments in Space Exploration",
      "url": "https://news.example.com/space-exploration",
      "description": "Recent missions have advanced...",
      "age": "2 hours ago",
      "page_age": "2026-01-15T14:30:00",
      "page_fetched": "2026-01-15T15:00:00Z",
      "meta_url": {
        "scheme": "https",
        "netloc": "news.example.com",
        "hostname": "news.example.com",
        "favicon": "https://imgs.search.brave.com/favicon/..."
      },
      "thumbnail": {
        "src": "https://imgs.search.brave.com/..."
      }
    }
  ]
}
```

### 主要响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `results[].title` | string | 文章标题 |
| `results[].url` | string | 文章 URL |
| `results[].description` | string? | 文章摘要 |
| `results[].age` | string? | 可读年龄（如 "2 hours ago"） |
| `results[].page_age` | string? | 发布日期（ISO datetime） |
| `results[].page_fetched` | string? | 页面抓取时间（ISO datetime） |
| `results[].extra_snippets` | list? | 额外摘要 |

## Goggles 自定义排名

新闻搜索支持 Goggles 来提升可信来源或屏蔽特定站点：

```bash
# 托管 Goggles
--data-urlencode "goggles=https://raw.githubusercontent.com/.../hacker_news.goggle"

# 内联规则
--data-urlencode 'goggles=$discard\n$site=reuters.com\n$site=apnews.com'
```

## 使用场景

- **突发新闻监控**: 使用 `freshness=pd` 获取最新文章
- **自定义新闻源**: 使用 Goggles 提升可信来源
- **历史新闻研究**: 使用日期范围过滤
- **多语言新闻**: 结合 `country` 和 `search_lang`

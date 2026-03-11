# Videos Search 详细文档

专注于视频内容的搜索端点。

## 端点

```http
GET https://api.search.brave.com/res/v1/videos/search
POST https://api.search.brave.com/res/v1/videos/search
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
| `safesearch` | string | 否 | `moderate` | 成人内容过滤 |
| `freshness` | string | 否 | - | 时间过滤 |
| `spellcheck` | bool | 否 | `true` | 自动纠正查询 |
| `operators` | bool | 否 | `true` | 应用搜索操作符 |
| `include_fetch_metadata` | bool | 否 | `false` | 包含抓取时间戳 |

## 响应格式

```json
{
  "type": "videos",
  "query": {
    "original": "python tutorial",
    "spellcheck_off": false
  },
  "results": [
    {
      "type": "video_result",
      "title": "Python Tutorial for Beginners",
      "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
      "description": "Learn Python programming from scratch...",
      "age": "February 12, 2025",
      "page_age": "2025-02-12T00:00:00",
      "thumbnail": {
        "src": "https://imgs.search.brave.com/...",
        "original": "https://i.ytimg.com/vi/rfscVS0vtbw/hqdefault.jpg"
      },
      "video": {
        "duration": "03:45:00",
        "views": 1523000,
        "creator": "freeCodeCamp",
        "publisher": "YouTube",
        "requires_subscription": false,
        "tags": ["python", "programming"],
        "author": {
          "name": "freeCodeCamp.org",
          "url": "https://www.youtube.com/@freecodecamp"
        }
      },
      "meta_url": {
        "scheme": "https",
        "netloc": "youtube.com",
        "hostname": "www.youtube.com"
      }
    }
  ]
}
```

### 主要响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `results[].video.duration` | string? | 时长（格式不固定） |
| `results[].video.views` | int? | 观看次数 |
| `results[].video.creator` | string? | 频道/创作者名称 |
| `results[].video.publisher` | string? | 平台（YouTube, Vimeo 等） |
| `results[].video.requires_subscription` | bool? | 是否需要订阅 |
| `results[].video.tags` | list? | 视频标签 |
| `results[].video.author` | object? | 作者信息 |

## 搜索操作符

```bash
# 限定特定平台
site:youtube.com
site:vimeo.com

# 精确匹配
"exact phrase"

# 排除
-exclude
```

## 使用场景

- **视频内容研究**: 查找教程、解说、评论
- **新鲜视频监控**: 使用 `freshness=pd` 或 `freshness=pw` 追踪新发布内容
- **平台特定搜索**: 使用 `site:` 操作符定位特定平台
- **视频元数据提取**: 获取观看数、时长、创作者信息

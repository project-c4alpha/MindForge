# Images Search 详细文档

专注于图片内容的搜索端点。

## 端点

```http
GET https://api.search.brave.com/res/v1/images/search
```

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | **是** | - | 搜索查询 |
| `country` | string | 否 | `US` | 搜索国家 |
| `search_lang` | string | 否 | `en` | 语言代码 |
| `count` | int | 否 | 50 | 返回结果数（1-200） |
| `safesearch` | string | 否 | `strict` | `off` 或 `strict`（无 moderate） |
| `spellcheck` | bool | 否 | true | 自动纠正查询 |

## 响应格式

```json
{
  "type": "images",
  "query": {
    "original": "mountain landscape",
    "altered": null,
    "spellcheck_off": false,
    "show_strict_warning": false
  },
  "results": [
    {
      "type": "image_result",
      "title": "Beautiful Mountain Landscape",
      "url": "https://example.com/mountain-photo",
      "source": "example.com",
      "page_fetched": "2025-09-15T10:30:00Z",
      "thumbnail": {
        "src": "https://imgs.search.brave.com/...",
        "width": 200,
        "height": 150
      },
      "properties": {
        "url": "https://example.com/images/mountain.jpg",
        "placeholder": "https://imgs.search.brave.com/placeholder/...",
        "width": 1920,
        "height": 1080
      },
      "meta_url": {
        "scheme": "https",
        "netloc": "example.com",
        "hostname": "example.com"
      },
      "confidence": "high"
    }
  ]
}
```

### 主要响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `results[].title` | string? | 图片标题 |
| `results[].url` | string? | 发现图片的页面 URL |
| `results[].source` | string? | 来源域名 |
| `results[].thumbnail.src` | string? | Brave 代理缩略图（~500px 宽） |
| `results[].properties.url` | string? | 原始全尺寸图片 URL |
| `results[].properties.placeholder` | string? | 低分辨率占位图 |
| `results[].properties.width` | int? | 原图宽度 |
| `results[].properties.height` | int? | 原图高度 |
| `results[].confidence` | string? | 相关性：`low`/`medium`/`high` |

## 使用场景

- **视觉内容发现**: 构建图库、情绪板、视觉研究
- **内容丰富**: 为文章或生成内容添加相关图片
- **安全图片获取**: 默认 `safesearch=strict` 确保内容安全
- **批量检索**: 每次最多 200 张图片（web: 20, videos/news: 50）

## 注意事项

- **SafeSearch**: 图片默认 `strict`（比网页搜索更严格）
- **高容量**: 每次最多返回 200 个结果
- **缩略图**: Brave 代理以保护隐私（500px 宽度）
- **尺寸**: `properties.width/height` 可能缺失

# Local POIs 详细文档

获取本地商家/POI 详情的端点。

> **两步流程**: 此端点需要先从网页搜索获取 POI ID。
>
> 1. 调用 `web-search` 并设置 `result_filter=locations` 获取 POI ID
> 2. 将这些 ID 传给此端点获取完整商家详情

## 端点

```http
GET https://api.search.brave.com/res/v1/local/pois
```

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `ids` | string[] | **是** | — | 从网页搜索获取的 POI ID（1-20） |
| `search_lang` | string | 否 | `en` | 语言偏好 |
| `ui_lang` | string | 否 | `en-US` | UI 语言 |
| `units` | string | 否 | null | `metric`（公里）或 `imperial`（英里） |

### 位置头（可选）

用于计算距离用户位置的距离：

| Header | 类型 | 范围 | 说明 |
|--------|------|------|------|
| `X-Loc-Lat` | float | -90.0 到 90.0 | 用户纬度 |
| `X-Loc-Long` | float | -180.0 到 180.0 | 用户经度 |

## 响应格式

```json
{
  "type": "local_pois",
  "results": [
    {
      "type": "location_result",
      "title": "Park Mediterranean Grill",
      "url": "https://yelp.com/biz/park-mediterranean-grill-sf",
      "provider_url": "https://yelp.com/biz/park-mediterranean-grill-sf",
      "id": "loc4CQWMJWLD4VBEBZ62XQLJTGK6YCJEEJDNAAAAAAA=",
      "postal_address": {
        "type": "PostalAddress",
        "displayAddress": "123 Main St, San Francisco, CA 94102",
        "streetAddress": "123 Main St",
        "addressLocality": "San Francisco",
        "addressRegion": "CA",
        "postalCode": "94102",
        "country": "US"
      },
      "contact": { "telephone": "+1 415-555-0123" },
      "thumbnail": {
        "src": "https://example.com/thumb.jpg",
        "original": "https://example.com/original.jpg"
      },
      "rating": {
        "ratingValue": 4.5,
        "bestRating": 5.0,
        "reviewCount": 234
      },
      "opening_hours": {
        "current_day": [
          { "abbr_name": "Mon", "full_name": "Monday", "opens": "07:00", "closes": "21:00" }
        ]
      },
      "coordinates": [37.7749, -122.4194],
      "distance": { "value": 0.3, "units": "miles" },
      "categories": ["Mediterranean", "Greek"],
      "price_range": "$$",
      "serves_cuisine": ["Mediterranean", "Greek"],
      "timezone": "America/Los_Angeles"
    }
  ]
}
```

### 主要响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 商家/POI 名称 |
| `url` | string | 位置的规范 URL |
| `id` | string | POI 标识符（约 8 小时有效） |
| `postal_address.displayAddress` | string | 格式化显示地址 |
| `contact.telephone` | string? | 电话号码 |
| `contact.email` | string? | 电子邮件 |
| `rating.ratingValue` | float? | 平均评分（≥0） |
| `rating.reviewCount` | int? | 评论数 |
| `opening_hours.current_day` | array? | 今日营业时间 |
| `opening_hours.days` | array? | 每周营业时间 |
| `coordinates` | [float, float]? | [纬度, 经度] |
| `distance.value` | float? | 距用户位置距离 |
| `categories` | string[] | 商家类别 |
| `price_range` | string? | 价格指示（`$`/`$$`/`$$$`/`$$$$`） |
| `serves_cuisine` | string[]? | 菜系类型（餐厅） |

## 获取 POI ID

```bash
# 1. 搜索本地商家
curl -s "https://api.search.brave.com/res/v1/web/search?q=coffee+shops+near+me&result_filter=locations" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -H "X-Loc-Lat: 37.7749" \
  -H "X-Loc-Long: -122.4194"

# 2. 从 locations.results[].id 提取 POI ID
# 3. 使用这些 ID 调用此端点
```

## 使用场景

- **本地商家查询**: 获取网页搜索中出现的 POI 完整详情
- **餐厅发现流程**: 搜索餐厅，获取 POI 详情，按菜系/评分/价格过滤
- **营业时间检查**: 获取 opening_hours 判断是否营业
- **位置感知应用**: 结合位置头获取附近 POI 的距离计算

## 注意事项

- **ID 格式**: 不透明字符串（使用 `--data-urlencode` 处理 cURL）
- **单位**: `metric` 或 `imperial` 用于距离测量偏好
- **最大 ID**: 每次请求最多 20 个 ID
- **ID 有效期**: 约 8 小时

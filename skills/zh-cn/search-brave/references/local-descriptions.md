# Local Descriptions 详细文档

获取 AI 生成的 POI 文本描述的端点。

> **两步流程**: 此端点需要先从网页搜索获取 POI ID。
>
> 1. 调用 `web-search` 并设置 `result_filter=locations` 获取 POI ID
> 2. 将这些 ID 传给此端点获取 AI 生成的描述

## 端点

```http
GET https://api.search.brave.com/res/v1/local/descriptions
```

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `ids` | string[] | **是** | — | 从网页搜索 `locations.results[].id` 获取的 POI ID（1-20） |

## 响应格式

```json
{
  "type": "local_descriptions",
  "results": [
    {
      "type": "local_description",
      "id": "loc4CQWMJWLD4VBEBZ62XQLJTGK6YCJEEJDNAAAAAAA=",
      "description": "### Overview\nA cozy neighborhood cafe known for its **artisanal coffee**..."
    }
  ]
}
```

### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 总是 `"local_descriptions"` |
| `results` | array | 描述对象列表（条目可能为 `null`） |
| `results[].type` | string | 总是 `"local_description"` |
| `results[].id` | string | 匹配请求的 POI 标识符 |
| `results[].description` | string? | AI 生成的 markdown 描述，如不可用则为 `null` |

## 获取 POI ID

```bash
# 1. 搜索本地商家
curl -s "https://api.search.brave.com/res/v1/web/search?q=restaurants+san+francisco&result_filter=locations" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"

# 2. 从 locations.results[].id 提取 POI ID
# 3. 使用这些 ID 调用 local/pois 和 local/descriptions
```

## 使用场景

- **本地商家概览**: 与 `local-pois` 配合获取结构化数据（营业时间、评分）和叙述性描述
- **旅游/旅游丰富**: 为 POI 添加描述性上下文用于旅行规划或目的地指南
- **搜索结果增强**: 用 AI 生成的本地商家摘要补充网页搜索结果

## 注意事项

- **总是 markdown**: 描述使用 `###` 标题、项目列表、**粗体**/*斜体* — 总是格式化为 markdown
- **旅游指南语调**: 通常 200-400 字，描述 POI 的特色
- **AI 生成**: 描述基于网页搜索上下文由 AI 生成，非来自商家资料
- **可用性**: 并非所有 POI 都有描述 — `description` 可能为 `null`
- **最大 ID**: 每次请求最多 20 个 ID

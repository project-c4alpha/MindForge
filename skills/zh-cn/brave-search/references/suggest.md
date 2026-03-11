# Suggest 详细文档

查询自动补全/建议端点，专为实时搜索体验设计。

## 端点

```http
GET https://api.search.brave.com/res/v1/suggest/search
```

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | **是** | — | 建议搜索查询（1-400 字符，最多 50 词） |
| `lang` | string | 否 | `en` | 语言偏好（2+ 字符语言代码） |
| `country` | string | 否 | `US` | 搜索国家 |
| `count` | int | 否 | `5` | 建议数量（1-20） |
| `rich` | bool | 否 | `false` | 增强实体信息（需要 Paid Search 计划） |

## 响应格式

### 基础响应

```json
{
  "type": "suggest",
  "query": { "original": "albert" },
  "results": [
    { "query": "albert einstein" },
    { "query": "albert einstein quotes" }
  ]
}
```

### 富响应（rich=true）

```json
{
  "type": "suggest",
  "query": { "original": "albert" },
  "results": [
    {
      "query": "albert einstein",
      "is_entity": true,
      "title": "Albert Einstein",
      "description": "German-born theoretical physicist",
      "img": "https://imgs.search.brave.com/..."
    },
    { "query": "albert einstein quotes", "is_entity": false }
  ]
}
```

### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 总是 `"suggest"` |
| `query.original` | string | 原始建议搜索查询 |
| `results` | array | 建议列表（可能为空） |
| `results[].query` | string | 建议的查询补全 |
| `results[].is_entity` | bool? | 是否为实体（仅 rich） |
| `results[].title` | string? | 实体标题（仅 rich） |
| `results[].description` | string? | 实体描述（仅 rich） |
| `results[].img` | string? | 实体图片 URL（仅 rich） |

## 使用场景

- **搜索即输入 UI**: 实时自动补全下拉。防抖 150-300ms
- **RAG 查询优化**: 在调用 `web-search` 或 `llm-context` 前扩展不完整/模糊查询
- **实体检测**: 使用 `rich=true` 检测带标题、描述和图片的实体用于预览卡片
- **容错输入**: 从拼写错误的输入获取干净建议，无需单独拼写检查

## 注意事项

- **延迟**: 设计为 <100ms 响应时间
- **Country/lang**: 建议相关性的提示，非严格过滤
- **拼写处理**: 建议处理常见拼写错误，无需单独拼写检查

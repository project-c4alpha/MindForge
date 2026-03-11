# Spellcheck 详细文档

独立的拼写检查端点。

> **注意**: 大多数搜索端点内置拼写检查；仅在需要预搜索查询清理或"您是指？"UI 时使用此独立端点。

## 端点

```http
GET https://api.search.brave.com/res/v1/spellcheck/search
```

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | **是** | — | 要检查的查询（1-400 字符，最多 50 词） |
| `lang` | string | 否 | `en` | 语言偏好（51 种语言代码支持） |
| `country` | string | 否 | `US` | 搜索国家 |

## 响应格式

```json
{
  "type": "spellcheck",
  "query": {
    "original": "artifical inteligence"
  },
  "results": [
    {
      "query": "artificial intelligence"
    }
  ]
}
```

### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 总是 `"spellcheck"` |
| `query.original` | string | 提交的输入查询 |
| `results` | array | 拼写纠正建议。未找到纠正时可能为空 |
| `results[].query` | string | 纠正后的查询版本 |

## 使用场景

- **预搜索查询清理**: 在决定调用哪个搜索端点之前检查拼写
- **"您是指？" UI**: 在运行搜索前向用户显示纠正建议
- **批量查询规范化**: 批量清理用户输入

## 注意事项

- **内置替代**: Web Search 和 LLM Context 默认有 `spellcheck=true` — 仅在搜索前需要纠正时使用此独立端点
- **上下文感知**: 纠正考虑完整查询上下文，不只是单个词

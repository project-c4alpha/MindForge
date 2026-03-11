# LLM Context 详细文档

用于 RAG/LLM 接地的专用端点，返回预提取的网页内容。

## 与 AI Grounding 的区别

| 特性 | LLM Context (此端点) | AI Grounding (answers) |
|------|---------------------|------------------------|
| 输出 | 原始提取内容 | 端到端 AI 答案 |
| 接口 | REST API (GET/POST) | OpenAI 兼容 `/chat/completions` |
| 搜索次数 | 每次请求 1 次 | 多次（迭代研究） |
| 速度 | 快 (<1s) | 较慢 |
| 计划 | Search | Answers |
| 用途 | AI agents, RAG, tool calls | 聊天界面, 研究模式 |

## 端点

```http
GET  https://api.search.brave.com/res/v1/llm/context
POST https://api.search.brave.com/res/v1/llm/context
```

## 参数

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | string | **是** | - | 搜索查询 |
| `country` | string | 否 | `US` | 搜索国家 |
| `search_lang` | string | 否 | `en` | 语言偏好 |
| `count` | int | 否 | `20` | 考虑的最大搜索结果数（1-50） |

### 上下文大小参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `maximum_number_of_urls` | int | `20` | 响应中最大 URL 数（1-50） |
| `maximum_number_of_tokens` | int | `8192` | 上下文最大 token 数（1024-32768） |
| `maximum_number_of_snippets` | int | `50` | 所有 URL 的最大摘要数（1-100） |
| `maximum_number_of_tokens_per_url` | int | `4096` | 每个 URL 的最大 token 数（512-8192） |
| `maximum_number_of_snippets_per_url` | int | `50` | 每个 URL 的最大摘要数（1-100） |

### 过滤和本地参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `context_threshold_mode` | string | `balanced` | 相关性阈值（`strict`/`balanced`/`lenient`） |
| `enable_local` | bool | `null` | 本地召回控制 |
| `goggles` | string/list | `null` | Goggle URL 或内联定义 |

## 上下文大小指南

| 任务类型 | count | max_tokens | 示例 |
|----------|-------|------------|------|
| 简单事实 | 5 | 2048 | "Python 是哪年创建的？" |
| 标准查询 | 20 | 8192 | "React hooks 最佳实践" |
| 复杂研究 | 50 | 16384 | "比较 AI 生产框架" |

## 阈值模式

| 模式 | 行为 |
|------|------|
| `strict` | 更高阈值 - 更少但更相关的结果 |
| `balanced` | 默认 - 覆盖和相关性平衡 |
| `lenient` | 更低阈值 - 更多结果，可能包含不太相关的内容 |

## 本地召回

| 值 | 行为 |
|----|------|
| `null` (未设置) | **自动检测** - 提供位置头时启用 |
| `true` | **强制本地** - 始终使用本地召回 |
| `false` | **强制标准** - 始终使用标准网页排名 |

## 响应格式

```json
{
  "grounding": {
    "generic": [
      {
        "url": "https://example.com/page",
        "title": "Page Title",
        "snippets": [
          "Relevant text chunk extracted...",
          "Another relevant passage..."
        ]
      }
    ],
    "map": []
  },
  "sources": {
    "https://example.com/page": {
      "title": "Page Title",
      "hostname": "example.com",
      "age": ["Wednesday, January 15, 2025", "2025-01-15", "392 days ago"]
    }
  }
}
```

### 本地响应（启用 enable_local）

```json
{
  "grounding": {
    "generic": [...],
    "poi": {
      "name": "Business Name",
      "url": "https://business.com",
      "title": "Business website title",
      "snippets": ["Business details..."]
    },
    "map": [
      {
        "name": "Place Name",
        "url": "https://place.com",
        "title": "Place website title",
        "snippets": ["Place information..."]
      }
    ]
  },
  "sources": { "..." }
}
```

## 使用场景

- **AI Agents**: 为 agent 提供返回可用内容的搜索工具
- **RAG 管道**: 为 LLM 响应提供新鲜、相关的网页内容
- **AI 助手/聊天机器人**: 提供有来源支持的事实答案
- **问答系统**: 检索特定查询的聚焦上下文
- **事实核查**: 根据当前网页内容验证声明

## 最佳实践

- **Token 预算**: 从默认值开始，简单查询减少，复杂研究增加
- **来源质量**: 使用 Goggles 限制可信来源，精度优先时用 `strict` 模式
- **性能**: 使用满足需求的最小 `count` 和 `maximum_number_of_tokens`

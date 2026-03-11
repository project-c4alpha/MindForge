# Answers 详细文档

OpenAI 兼容的 AI 答案生成端点，支持单次搜索和深度研究模式。

## 端点

```http
POST https://api.search.brave.com/res/v1/chat/completions
```

**认证**: `X-Subscription-Token: <API_KEY>` 或 `Authorization: Bearer <API_KEY>`

**SDK 兼容**: 通过 `base_url="https://api.search.brave.com/res/v1"` 与 OpenAI SDK 兼容

## 两种模式

| 特性 | 单次搜索（默认） | 研究（enable_research=true） |
|------|-----------------|------------------------------|
| 速度 | 快 | 慢 |
| 搜索次数 | 1 | 多次（迭代） |
| 流式 | 可选 | **必须**（stream=true） |
| 引用 | enable_citations=true | 内置（在 `<answer>` 标签中） |
| 进度事件 | 无 | 有（`<progress>` 标签） |
| 阻塞响应 | 是（stream=false） | 否 |

## 参数

### 标准参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `messages` | array | **是** | - | 单个用户消息（必须恰好 1 条） |
| `model` | string | **是** | - | 使用 `"brave"` |
| `stream` | bool | 否 | true | 启用 SSE 流式 |
| `country` | string | 否 | "US" | 搜索国家 |
| `language` | string | 否 | "en" | 响应语言 |
| `safesearch` | string | 否 | "moderate" | 安全级别 |
| `max_completion_tokens` | int | 否 | null | 完成令牌上限 |
| `enable_citations` | bool | 否 | false | 内联引用标签（仅单次搜索流式） |
| `web_search_options` | object | 否 | null | OpenAI 兼容；`search_context_size`: `low`/`medium`/`high` |

### 研究参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enable_research` | bool | `false` | **启用研究模式** |
| `research_allow_thinking` | bool | `true` | 启用扩展思考 |
| `research_maximum_number_of_tokens_per_query` | int | `8192` | 每次查询最大 token（1024-16384） |
| `research_maximum_number_of_queries` | int | `20` | 最大总搜索查询数（1-50） |
| `research_maximum_number_of_iterations` | int | `4` | 最大研究迭代次数（1-5） |
| `research_maximum_number_of_seconds` | int | `180` | 时间预算（秒）（1-300） |
| `research_maximum_number_of_results_per_query` | int | `60` | 每次搜索的结果数（1-60） |

### 约束（重要）

| 约束 | 错误 |
|------|------|
| `enable_research=true` 需要 `stream=true` | "Blocking response doesn't support 'enable_research' option" |
| `enable_research=true` 与 `enable_citations=true` 不兼容 | "Research mode doesn't support 'enable_citations' option" |
| `enable_citations=true` 需要 `stream=true` | "Blocking response doesn't support 'enable_citations' option" |

## OpenAI SDK 使用

### 阻塞模式（单次搜索）

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.search.brave.com/res/v1",
    api_key="your-brave-api-key",
)

response = client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "James Webb 太空望远镜如何工作？"}],
    stream=False,
)
print(response.choices[0].message.content)
```

### 流式带引用（单次搜索）

```python
stream = client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "可再生能源的最新趋势？"}],
    stream=True,
    extra_body={"enable_citations": True}
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 研究模式

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://api.search.brave.com/res/v1",
    api_key="your-brave-api-key",
)

stream = await client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "比较量子计算方法"}],
    stream=True,
    extra_body={
        "enable_research": True,
        "research_maximum_number_of_iterations": 3,
        "research_maximum_number_of_seconds": 120
    }
)

async for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## 流式标签

### 单次搜索（enable_citations=true）

| 标签 | 用途 |
|------|------|
| `<citation>` | 内联引用参考 |
| `<usage>` | JSON 成本/计费数据 |

### 研究模式

| 标签 | 用途 | 保留？ |
|------|------|--------|
| `<queries>` | 生成的搜索查询 | 调试 |
| `<analyzing>` | URL 计数（详细） | 调试 |
| `<thinking>` | URL 选择推理 | 调试 |
| `<progress>` | 统计：时间、迭代、查询、URL、token | 监控 |
| `<blindspots>` | 识别的知识缺口 | **是** |
| `<answer>` | 最终综合答案 | **是** |
| `<usage>` | JSON 成本/计费数据 | **是** |

## 使用场景

- **聊天界面集成**: OpenAI SDK 的直接替代，带网页接地
- **深度研究**: 使用研究模式处理需要多源综合的复杂问题
- **OpenAI SDK 兼容**: 相同 SDK，相同流式格式 — 只需更改 base_url 和 api_key
- **带引用的答案**: 单次搜索启用 enable_citations 或使用研究模式

## 注意事项

- **超时**: 单次搜索至少 30s，研究模式至少 300s（5 分钟）
- **单条消息**: messages 数组必须恰好包含 1 条用户消息
- **成本监控**: 解析流式响应中的 `<usage>` 标签来追踪成本

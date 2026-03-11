# Answers Detailed Documentation

OpenAI-compatible AI answer generation endpoint, supporting single-search and deep research modes.

## Endpoint

```http
POST https://api.search.brave.com/res/v1/chat/completions
```

**Authentication**: `X-Subscription-Token: <API_KEY>` header or `Authorization: Bearer <API_KEY>`

**SDK Compatible**: Works with OpenAI SDK via `base_url="https://api.search.brave.com/res/v1"`

## Two Modes

| Feature | Single-Search (default) | Research (`enable_research=true`) |
|---------|------------------------|----------------------------------|
| Speed | Fast | Slow |
| Searches | 1 | Multiple (iterative) |
| Streaming | Optional (`stream=true/false`) | **Required** (`stream=true`) |
| Citations | `enable_citations=true` (streaming only) | Built-in (in `<answer>` tag) |
| Progress events | No | Yes (`<progress>` tags) |
| Blocking response | Yes (`stream=false`) | No |

## Parameters

### Standard Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `messages` | array | **Yes** | - | Single user message (exactly 1 message) |
| `model` | string | **Yes** | - | Use `"brave"` |
| `stream` | bool | No | true | Enable SSE streaming |
| `country` | string | No | "US" | Search country |
| `language` | string | No | "en" | Response language |
| `safesearch` | string | No | "moderate" | Search safety level |
| `max_completion_tokens` | int | No | null | Upper bound on completion tokens |
| `enable_citations` | bool | No | false | Include inline citation tags (single-search streaming only) |
| `web_search_options` | object | No | null | OpenAI-compatible; `search_context_size`: `low`/`medium`/`high` |

### Research Parameters

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `enable_research` | bool | `false` | **Enable research mode** |
| `research_allow_thinking` | bool | `true` | Enable extended thinking |
| `research_maximum_number_of_tokens_per_query` | int | `8192` | Max tokens per query (1024-16384) |
| `research_maximum_number_of_queries` | int | `20` | Max total search queries (1-50) |
| `research_maximum_number_of_iterations` | int | `4` | Max research iterations (1-5) |
| `research_maximum_number_of_seconds` | int | `180` | Time budget in seconds (1-300) |
| `research_maximum_number_of_results_per_query` | int | `60` | Results per search query (1-60) |

### Constraints (IMPORTANT)

| Constraint | Error |
|------------|-------|
| `enable_research=true` requires `stream=true` | "Blocking response doesn't support 'enable_research' option" |
| `enable_research=true` incompatible with `enable_citations=true` | "Research mode doesn't support 'enable_citations' option" |
| `enable_citations=true` requires `stream=true` | "Blocking response doesn't support 'enable_citations' option" |

## OpenAI SDK Usage

### Blocking (Single-Search)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.search.brave.com/res/v1",
    api_key="your-brave-api-key",
)

response = client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "How does the James Webb Space Telescope work?"}],
    stream=False,
)
print(response.choices[0].message.content)
```

### Streaming with Citations (Single-Search)

```python
stream = client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "What are current trends in renewable energy?"}],
    stream=True,
    extra_body={"enable_citations": True}
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Research Mode

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://api.search.brave.com/res/v1",
    api_key="your-brave-api-key",
)

stream = await client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "Compare quantum computing approaches"}],
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

## Streaming Tags by Mode

### Single-Search (with `enable_citations=true`)

| Tag | Purpose |
|-----|---------|
| `<citation>` | Inline citation references |
| `<usage>` | JSON cost/billing data |

### Research Mode

| Tag | Purpose | Keep? |
|-----|---------|-------|
| `<queries>` | Generated search queries | Debug |
| `<analyzing>` | URL counts (verbose) | Debug |
| `<thinking>` | URL selection reasoning | Debug |
| `<progress>` | Stats: time, iterations, queries, URLs, tokens | Monitor |
| `<blindspots>` | Knowledge gaps identified | **Yes** |
| `<answer>` | Final synthesized answer | **Yes** |
| `<usage>` | JSON cost/billing data | **Yes** |

## Use Cases

- **Chat interface integration**: Drop-in OpenAI SDK replacement with web-grounded answers
- **Deep research / comprehensive topic research**: Use research mode for complex questions needing multi-source synthesis
- **OpenAI SDK drop-in**: Same SDK, same streaming format — just change `base_url` and `api_key`
- **Cited answers**: Enable `enable_citations=true` in single-search mode, or use research mode

## Notes

- **Timeout**: Set client timeout to at least 30s for single-search, 300s (5 min) for research
- **Single message**: The `messages` array must contain exactly 1 user message
- **Cost monitoring**: Parse the `<usage>` tag from streaming responses to track costs

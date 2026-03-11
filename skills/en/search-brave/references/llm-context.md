# LLM Context Detailed Documentation

Dedicated endpoint for RAG/LLM grounding, returning pre-extracted web content.

## Comparison with AI Grounding

| Feature | LLM Context (this) | AI Grounding (answers) |
|---------|-------------------|------------------------|
| Output | Raw extracted content | End-to-end AI answers |
| Interface | REST API (GET/POST) | OpenAI-compatible `/chat/completions` |
| Searches | Single search per request | Multiple (iterative research) |
| Speed | Fast (<1s) | Slower |
| Plan | Search | Answers |
| Best for | AI agents, RAG, tool calls | Chat interfaces, research mode |

## Endpoint

```http
GET  https://api.search.brave.com/res/v1/llm/context
POST https://api.search.brave.com/res/v1/llm/context
```

## Parameters

### Query Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | string | **Yes** | - | Search query |
| `country` | string | No | `US` | Search country |
| `search_lang` | string | No | `en` | Language preference |
| `count` | int | No | `20` | Max search results to consider (1-50) |

### Context Size Parameters

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `maximum_number_of_urls` | int | `20` | Max URLs in response (1-50) |
| `maximum_number_of_tokens` | int | `8192` | Approximate max tokens in context (1024-32768) |
| `maximum_number_of_snippets` | int | `50` | Max snippets across all URLs (1-100) |
| `maximum_number_of_tokens_per_url` | int | `4096` | Max tokens per individual URL (512-8192) |
| `maximum_number_of_snippets_per_url` | int | `50` | Max snippets per individual URL (1-100) |

### Filtering & Local Parameters

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `context_threshold_mode` | string | `balanced` | Relevance threshold (`strict`/`balanced`/`lenient`) |
| `enable_local` | bool | `null` | Local recall control |
| `goggles` | string/list | `null` | Goggle URL or inline definition |

## Context Size Guidelines

| Task Type | count | max_tokens | Example |
|-----------|-------|------------|---------|
| Simple factual | 5 | 2048 | "What year was Python created?" |
| Standard queries | 20 | 8192 | "Best practices for React hooks" |
| Complex research | 50 | 16384 | "Compare AI frameworks for production" |

## Threshold Modes

| Mode | Behavior |
|------|----------|
| `strict` | Higher threshold — fewer but more relevant results |
| `balanced` | Default — good balance between coverage and relevance |
| `lenient` | Lower threshold — more results, may include less relevant content |

## Local Recall

| Value | Behavior |
|-------|----------|
| `null` (not set) | **Auto-detect** — local recall enabled when location headers provided |
| `true` | **Force local** — always use local recall |
| `false` | **Force standard** — always use standard web ranking |

## Response Format

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

### Local Response (with enable_local)

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

## Use Cases

- **AI Agents**: Give your agent a web search tool that returns ready-to-use content
- **RAG Pipelines**: Ground LLM responses in fresh, relevant web content
- **AI Assistants & Chatbots**: Provide factual answers backed by real sources
- **Question Answering**: Retrieve focused context for specific queries
- **Fact Checking**: Verify claims against current web content

## Best Practices

- **Token budget**: Start with defaults, reduce for simple lookups, increase for complex research
- **Source quality**: Use Goggles to restrict to trusted sources. Set `context_threshold_mode=strict` when precision > recall.
- **Performance**: Use smallest `count` and `maximum_number_of_tokens` that meet your needs

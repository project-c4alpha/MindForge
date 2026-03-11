# Suggest Detailed Documentation

Query autocomplete/suggestion endpoint, designed for real-time search experiences.

## Endpoint

```http
GET https://api.search.brave.com/res/v1/suggest/search
```

## Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | string | **Yes** | — | Suggest search query (1-400 chars, max 50 words) |
| `lang` | string | No | `en` | Language preference (2+ char language code) |
| `country` | string | No | `US` | Search country |
| `count` | int | No | `5` | Number of suggestions (1-20) |
| `rich` | bool | No | `false` | Enhance with entity info (requires Paid Search plan) |

## Response Format

### Basic Response

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

### Rich Response (`rich=true`)

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

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"suggest"` |
| `query.original` | string | The original suggest search query |
| `results` | array | List of suggestions (may be empty) |
| `results[].query` | string | Suggested query completion |
| `results[].is_entity` | bool? | Whether the enriched query is an entity (rich only) |
| `results[].title` | string? | Entity title (rich only) |
| `results[].description` | string? | Entity description (rich only) |
| `results[].img` | string? | Entity image URL (rich only) |

## Use Cases

- **Search-as-you-type UI**: Real-time autocomplete dropdown. Debounce 150-300ms.
- **Query refinement for RAG**: Expand partial/ambiguous queries before calling `web-search` or `llm-context`.
- **Entity detection**: Use `rich=true` to detect entities with title, description, and image for preview cards.
- **Typo-tolerant input**: Get clean suggestions from misspelled input without separate spellcheck.

## Notes

- **Latency**: Designed for <100ms response times
- **Country/lang**: Hints for suggestion relevance, not strict filters
- **Typo handling**: Suggestions handle common typos without separate spellcheck

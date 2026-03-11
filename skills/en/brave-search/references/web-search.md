# Web Search Detailed Documentation

The primary web search endpoint, returning the most comprehensive result set.

## Endpoint

```http
GET https://api.search.brave.com/res/v1/web/search
POST https://api.search.brave.com/res/v1/web/search
```

**Authentication**: `X-Subscription-Token: <API_KEY>` header

## Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | string | **Yes** | - | Search query (1-400 chars, max 50 words) |
| `country` | string | No | `US` | Search country (2-letter country code or `ALL`) |
| `search_lang` | string | No | `en` | Language preference (2+ char language code) |
| `ui_lang` | string | No | `en-US` | UI language |
| `count` | int | No | `20` | Max results per page (1-20) |
| `offset` | int | No | `0` | Page offset for pagination (0-9) |
| `safesearch` | string | No | `moderate` | Adult content filter (`off`/`moderate`/`strict`) |
| `freshness` | string | No | - | Time filter (`pd`/`pw`/`pm`/`py` or date range) |
| `text_decorations` | bool | No | `true` | Include highlight markers |
| `spellcheck` | bool | No | `true` | Auto-correct query |
| `result_filter` | string | No | - | Filter result types (comma-separated) |
| `goggles` | string | No | - | Custom ranking filter |
| `extra_snippets` | bool | No | - | Get up to 5 extra snippets per result |
| `operators` | bool | No | `true` | Apply search operators |
| `units` | string | No | - | Measurement units (`metric`/`imperial`) |
| `enable_rich_callback` | bool | No | `false` | Enable rich 3rd party data callback |
| `include_fetch_metadata` | bool | No | `false` | Include `fetched_content_timestamp` on results |

### Result Filter Values

Available types: `discussions`, `faq`, `infobox`, `news`, `query`, `videos`, `web`, `locations`

```bash
# Only web and video results
curl "...&result_filter=web,videos"
```

## Response Format

```json
{
  "type": "search",
  "query": {
    "original": "python frameworks",
    "altered": "python web frameworks",
    "spellcheck_off": false,
    "more_results_available": true
  },
  "web": {
    "type": "search",
    "results": [
      {
        "title": "Top Python Web Frameworks",
        "url": "https://example.com/python-frameworks",
        "description": "A comprehensive guide...",
        "age": "2 days ago",
        "language": "en",
        "meta_url": {
          "scheme": "https",
          "netloc": "example.com",
          "hostname": "example.com",
          "path": "/python-frameworks"
        },
        "thumbnail": {
          "src": "https://...",
          "original": "https://original-image-url.com/img.jpg"
        },
        "extra_snippets": ["Additional excerpt 1...", "Additional excerpt 2..."]
      }
    ],
    "family_friendly": true
  },
  "mixed": {
    "type": "mixed",
    "main": [
      {"type": "web", "index": 0, "all": false},
      {"type": "videos", "all": true}
    ],
    "top": [],
    "side": []
  },
  "videos": { "...": "..." },
  "news": { "...": "..." }
}
```

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"search"` |
| `query.original` | string | The original search query |
| `query.altered` | string? | Spellcheck-corrected query |
| `query.more_results_available` | bool | Whether more pages exist |
| `web.results[].title` | string | Page title |
| `web.results[].url` | string | Page URL |
| `web.results[].description` | string? | Snippet text |
| `web.results[].age` | string? | Human-readable age (e.g., "2 days ago") |
| `web.results[].language` | string? | Content language |
| `web.results[].thumbnail` | object? | Thumbnail info |
| `web.results[].extra_snippets` | list? | Additional excerpts |
| `web.results[].schemas` | list? | schema.org structured data |
| `mixed` | object | Preferred display order |

### Mixed Response Explanation

The `mixed` object defines the recommended display order across result types:

| Array | Purpose |
|-------|---------|
| `main` | Primary result list |
| `top` | Display above main results |
| `side` | Display alongside main results (e.g., infobox) |

## Rich Data Callback

For queries about weather, stocks, sports, etc.:

```bash
# 1. Enable rich callback
curl "...&q=weather+san+francisco&enable_rich_callback=true"

# Response includes: "rich": {"hint": {"callback_key": "abc123...", "vertical": "weather"}}

# 2. Get rich data with callback key
curl "https://api.search.brave.com/res/v1/web/rich?callback_key=abc123..."
```

**Supported Rich Types**: Calculator, Definitions, Unit Conversion, Stock, Currency, Cryptocurrency, Weather, Sports, etc.

## Use Cases

- **General-purpose search integration**: Get the richest result set in one call
- **Structured data extraction**: Get products, recipes, ratings via `schemas` and typed fields
- **Custom search**: Use Goggles for fully customized ranking

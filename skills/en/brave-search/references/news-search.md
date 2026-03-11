# News Search Detailed Documentation

Search endpoint focused on news articles.

## Endpoint

```http
GET https://api.search.brave.com/res/v1/news/search
POST https://api.search.brave.com/res/v1/news/search
```

## Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | string | **Yes** | - | Search query |
| `country` | string | No | `US` | Search country |
| `search_lang` | string | No | `en` | Language preference |
| `ui_lang` | string | No | `en-US` | UI language |
| `count` | int | No | `20` | Number of results (1-50) |
| `offset` | int | No | `0` | Page offset (0-9) |
| `safesearch` | string | No | `strict` | Adult content filter |
| `freshness` | string | No | - | Time filter |
| `spellcheck` | bool | No | `true` | Auto-correct |
| `extra_snippets` | bool | No | - | Up to 5 additional excerpts per result |
| `goggles` | string/array | No | - | Custom ranking filter |
| `operators` | bool | No | `true` | Apply search operators |
| `include_fetch_metadata` | bool | No | `false` | Include fetch timestamps |

## Response Format

```json
{
  "type": "news",
  "query": {
    "original": "space exploration"
  },
  "results": [
    {
      "type": "news_result",
      "title": "New Developments in Space Exploration",
      "url": "https://news.example.com/space-exploration",
      "description": "Recent missions have advanced...",
      "age": "2 hours ago",
      "page_age": "2026-01-15T14:30:00",
      "page_fetched": "2026-01-15T15:00:00Z",
      "meta_url": {
        "scheme": "https",
        "netloc": "news.example.com",
        "hostname": "news.example.com",
        "favicon": "https://imgs.search.brave.com/favicon/..."
      },
      "thumbnail": {
        "src": "https://imgs.search.brave.com/..."
      }
    }
  ]
}
```

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `results[].title` | string | Article title |
| `results[].url` | string | Article URL |
| `results[].description` | string? | Article summary |
| `results[].age` | string? | Human-readable age (e.g., "2 hours ago") |
| `results[].page_age` | string? | Publication date (ISO datetime) |
| `results[].page_fetched` | string? | Page fetch time (ISO datetime) |
| `results[].extra_snippets` | list? | Additional excerpts |

## Goggles Custom Ranking

News search supports Goggles to boost trusted sources or block unwanted sites:

```bash
# Hosted Goggles
--data-urlencode "goggles=https://raw.githubusercontent.com/.../hacker_news.goggle"

# Inline rules
--data-urlencode 'goggles=$discard\n$site=reuters.com\n$site=apnews.com'
```

## Use Cases

- **Breaking news monitoring**: Use `freshness=pd` for most recent articles
- **Custom news feeds with Goggles**: Boost trusted sources — unique to Brave
- **Historical news research**: Use date range filtering
- **Multilingual news**: Combine `country` and `search_lang` for cross-locale results

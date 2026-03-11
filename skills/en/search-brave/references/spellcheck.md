# Spellcheck Detailed Documentation

Standalone spell checking endpoint.

> **Note**: Most search endpoints have spellcheck built-in; use this standalone endpoint only when you need pre-search query cleanup or "Did you mean?" UI.

## Endpoint

```http
GET https://api.search.brave.com/res/v1/spellcheck/search
```

## Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | string | **Yes** | — | Query to spell check (1-400 chars, max 50 words) |
| `lang` | string | No | `en` | Language preference (51 codes supported) |
| `country` | string | No | `US` | Search country |

## Response Format

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

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"spellcheck"` |
| `query.original` | string | The input query as submitted |
| `results` | array | Spell-corrected suggestions. May be empty when no correction is found |
| `results[].query` | string | A corrected version of the query |

## Use Cases

- **Pre-search query cleanup**: Check spelling before deciding which search endpoint to call
- **"Did you mean?" UI**: Show users a corrected suggestion before running the search
- **Batch query normalization**: Clean up user inputs in bulk

## Notes

- **Built-in alternative**: Web Search and LLM Context have `spellcheck=true` by default — use this standalone endpoint only when you need the correction before searching
- **Context-aware**: Corrections consider the full query context, not just individual words

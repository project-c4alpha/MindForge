# Local Descriptions Detailed Documentation

Endpoint for getting AI-generated POI text descriptions.

> **Two-step flow**: This endpoint requires POI IDs from a prior web search.
>
> 1. Call `web-search` with `result_filter=locations` to get POI IDs
> 2. Pass those IDs to this endpoint to get AI-generated descriptions

## Endpoint

```http
GET https://api.search.brave.com/res/v1/local/descriptions
```

## Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `ids` | string[] | **Yes** | — | POI IDs from web search `locations.results[].id` (1-20) |

## Response Format

```json
{
  "type": "local_descriptions",
  "results": [
    {
      "type": "local_description",
      "id": "loc4CQWMJWLD4VBEBZ62XQLJTGK6YCJEEJDNAAAAAAA=",
      "description": "### Overview\nA cozy neighborhood cafe known for its **artisanal coffee**..."
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"local_descriptions"` |
| `results` | array | List of description objects (entries may be `null`) |
| `results[].type` | string | Always `"local_description"` |
| `results[].id` | string | POI identifier matching the request |
| `results[].description` | string? | AI-generated markdown description, or `null` if unavailable |

## Getting POI IDs

```bash
# 1. Search for local businesses
curl -s "https://api.search.brave.com/res/v1/web/search?q=restaurants+san+francisco&result_filter=locations" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"

# 2. Extract POI IDs from locations.results[].id
# 3. Use those IDs with local/pois and local/descriptions
```

## Use Cases

- **Local business overview**: Pair with `local-pois` to get both structured data (hours, ratings) and narrative descriptions
- **Travel/tourism enrichment**: Add descriptive context to POIs for travel planning or destination guides
- **Search results augmentation**: Supplement web search results with AI-generated summaries of local businesses

## Notes

- **Always markdown**: Descriptions use `###` headings, bullet lists, **bold**/*italics* — always formatted as markdown
- **Travel-guide tone**: Typically 200-400 words covering what makes the POI notable
- **AI-generated**: Descriptions are AI-generated based on web search context, not sourced from business profiles
- **Availability**: Not all POIs have descriptions — `description` may be `null`
- **Max IDs**: Up to 20 IDs per request

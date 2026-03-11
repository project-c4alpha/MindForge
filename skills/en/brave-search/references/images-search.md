# Images Search Detailed Documentation

Search endpoint focused on image content.

## Endpoint

```http
GET https://api.search.brave.com/res/v1/images/search
```

## Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | string | **Yes** | - | Search query |
| `country` | string | No | `US` | Search country |
| `search_lang` | string | No | `en` | Language code |
| `count` | int | No | 50 | Results to return (1-200) |
| `safesearch` | string | No | `strict` | `off` or `strict` (no moderate for images) |
| `spellcheck` | bool | No | true | Auto-correct query |

## Response Format

```json
{
  "type": "images",
  "query": {
    "original": "mountain landscape",
    "altered": null,
    "spellcheck_off": false,
    "show_strict_warning": false
  },
  "results": [
    {
      "type": "image_result",
      "title": "Beautiful Mountain Landscape",
      "url": "https://example.com/mountain-photo",
      "source": "example.com",
      "page_fetched": "2025-09-15T10:30:00Z",
      "thumbnail": {
        "src": "https://imgs.search.brave.com/...",
        "width": 200,
        "height": 150
      },
      "properties": {
        "url": "https://example.com/images/mountain.jpg",
        "placeholder": "https://imgs.search.brave.com/placeholder/...",
        "width": 1920,
        "height": 1080
      },
      "meta_url": {
        "scheme": "https",
        "netloc": "example.com",
        "hostname": "example.com"
      },
      "confidence": "high"
    }
  ]
}
```

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `results[].title` | string? | Image title |
| `results[].url` | string? | Page URL where image was found |
| `results[].source` | string? | Source domain |
| `results[].thumbnail.src` | string? | Brave-proxied thumbnail (~500px width) |
| `results[].properties.url` | string? | Original full-size image URL |
| `results[].properties.placeholder` | string? | Low-res placeholder URL |
| `results[].properties.width` | int? | Original image width |
| `results[].properties.height` | int? | Original image height |
| `results[].confidence` | string? | Relevance: `low`/`medium`/`high` |

## Use Cases

- **Visual content discovery**: Build image galleries, mood boards, visual research tools
- **Content enrichment**: Add relevant images to articles or generated content
- **Safe image retrieval**: Default `safesearch=strict` ensures family-friendly results
- **High-volume batch retrieval**: Up to 200 images per request

## Notes

- **SafeSearch**: Defaults to `strict` for images (stricter than web search)
- **High volume**: Can return up to 200 results per request
- **Thumbnails**: Brave-proxied for privacy (500px width). Use `properties.url` for full resolution.
- **Dimensions**: `properties.width/height` may be missing for some images

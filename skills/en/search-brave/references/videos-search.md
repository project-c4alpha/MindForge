# Videos Search Detailed Documentation

Search endpoint focused on video content.

## Endpoint

```http
GET https://api.search.brave.com/res/v1/videos/search
POST https://api.search.brave.com/res/v1/videos/search
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
| `safesearch` | string | No | `moderate` | Adult content filter |
| `freshness` | string | No | - | Time filter |
| `spellcheck` | bool | No | `true` | Auto-correct query |
| `operators` | bool | No | `true` | Apply search operators |
| `include_fetch_metadata` | bool | No | `false` | Include fetch timestamps |

## Response Format

```json
{
  "type": "videos",
  "query": {
    "original": "python tutorial",
    "spellcheck_off": false
  },
  "results": [
    {
      "type": "video_result",
      "title": "Python Tutorial for Beginners",
      "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
      "description": "Learn Python programming from scratch...",
      "age": "February 12, 2025",
      "page_age": "2025-02-12T00:00:00",
      "thumbnail": {
        "src": "https://imgs.search.brave.com/...",
        "original": "https://i.ytimg.com/vi/rfscVS0vtbw/hqdefault.jpg"
      },
      "video": {
        "duration": "03:45:00",
        "views": 1523000,
        "creator": "freeCodeCamp",
        "publisher": "YouTube",
        "requires_subscription": false,
        "tags": ["python", "programming"],
        "author": {
          "name": "freeCodeCamp.org",
          "url": "https://www.youtube.com/@freecodecamp"
        }
      },
      "meta_url": {
        "scheme": "https",
        "netloc": "youtube.com",
        "hostname": "www.youtube.com"
      }
    }
  ]
}
```

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `results[].video.duration` | string? | Duration (variable format) |
| `results[].video.views` | int? | View count |
| `results[].video.creator` | string? | Channel/creator name |
| `results[].video.publisher` | string? | Platform (YouTube, Vimeo, etc.) |
| `results[].video.requires_subscription` | bool? | Whether subscription required |
| `results[].video.tags` | list? | Video tags |
| `results[].video.author` | object? | Author info |

## Search Operators

```bash
# Platform-specific search
site:youtube.com
site:vimeo.com

# Exact match
"exact phrase"

# Exclude
-exclude
```

## Use Cases

- **Video content research**: Find tutorials, explainers, reviews
- **Fresh video monitoring**: Use `freshness=pd` or `freshness=pw` to track newly published content
- **Platform-specific search**: Use `site:` operator to target specific platforms
- **Video metadata extraction**: Get view counts, durations, creator info

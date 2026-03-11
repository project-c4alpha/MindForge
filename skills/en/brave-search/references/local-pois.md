# Local POIs Detailed Documentation

Endpoint for getting local business/POI details.

> **Two-step flow**: This endpoint requires POI IDs from a prior web search.
>
> 1. Call `web-search` with `result_filter=locations` to get POI IDs
> 2. Pass those IDs to this endpoint to get full business details

## Endpoint

```http
GET https://api.search.brave.com/res/v1/local/pois
```

## Parameters

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `ids` | string[] | **Yes** | — | POI IDs from web search results (1-20) |
| `search_lang` | string | No | `en` | Language preference |
| `ui_lang` | string | No | `en-US` | UI language |
| `units` | string | No | null | `metric` (km) or `imperial` (miles) |

### Location Headers (Optional)

For distance calculation from user location:

| Header | Type | Range | Description |
|--------|------|-------|-------------|
| `X-Loc-Lat` | float | -90.0 to 90.0 | User latitude |
| `X-Loc-Long` | float | -180.0 to 180.0 | User longitude |

## Response Format

```json
{
  "type": "local_pois",
  "results": [
    {
      "type": "location_result",
      "title": "Park Mediterranean Grill",
      "url": "https://yelp.com/biz/park-mediterranean-grill-sf",
      "provider_url": "https://yelp.com/biz/park-mediterranean-grill-sf",
      "id": "loc4CQWMJWLD4VBEBZ62XQLJTGK6YCJEEJDNAAAAAAA=",
      "postal_address": {
        "type": "PostalAddress",
        "displayAddress": "123 Main St, San Francisco, CA 94102",
        "streetAddress": "123 Main St",
        "addressLocality": "San Francisco",
        "addressRegion": "CA",
        "postalCode": "94102",
        "country": "US"
      },
      "contact": { "telephone": "+1 415-555-0123" },
      "thumbnail": {
        "src": "https://example.com/thumb.jpg",
        "original": "https://example.com/original.jpg"
      },
      "rating": {
        "ratingValue": 4.5,
        "bestRating": 5.0,
        "reviewCount": 234
      },
      "opening_hours": {
        "current_day": [
          { "abbr_name": "Mon", "full_name": "Monday", "opens": "07:00", "closes": "21:00" }
        ]
      },
      "coordinates": [37.7749, -122.4194],
      "distance": { "value": 0.3, "units": "miles" },
      "categories": ["Mediterranean", "Greek"],
      "price_range": "$$",
      "serves_cuisine": ["Mediterranean", "Greek"],
      "timezone": "America/Los_Angeles"
    }
  ]
}
```

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Business/POI name |
| `url` | string | Canonical URL for the location |
| `id` | string | POI identifier (valid ~8 hours) |
| `postal_address.displayAddress` | string | Formatted display address |
| `contact.telephone` | string? | Phone number |
| `contact.email` | string? | Email address |
| `rating.ratingValue` | float? | Average rating (≥0) |
| `rating.reviewCount` | int? | Number of reviews |
| `opening_hours.current_day` | array? | Today's hours |
| `opening_hours.days` | array? | Hours for each day of week |
| `coordinates` | [float, float]? | [latitude, longitude] tuple |
| `distance.value` | float? | Distance from user location |
| `categories` | string[] | Business categories |
| `price_range` | string? | Price indicator (`$`/`$$`/`$$$`/`$$$$`) |
| `serves_cuisine` | string[]? | Cuisine types (restaurants) |

## Getting POI IDs

```bash
# 1. Search for local businesses
curl -s "https://api.search.brave.com/res/v1/web/search?q=coffee+shops+near+me&result_filter=locations" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -H "X-Loc-Lat: 37.7749" \
  -H "X-Loc-Long: -122.4194"

# 2. Extract POI IDs from locations.results[].id
# 3. Use those IDs with this endpoint
```

## Use Cases

- **Local business lookup**: Retrieve full details for POIs surfaced in web search
- **Restaurant discovery pipeline**: Search for restaurants, fetch POI details, filter by cuisine/rating/price
- **Business hours checker**: Get opening_hours to determine if currently open
- **Location-aware application**: Combine with location headers for distance calculations

## Notes

- **ID format**: Opaque strings (use `--data-urlencode` for cURL)
- **Units**: `metric` or `imperial` for distance measurement preference
- **Max IDs**: Up to 20 IDs per request
- **ID validity**: ~8 hours

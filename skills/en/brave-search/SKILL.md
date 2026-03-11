---
name: brave-search
description: Comprehensive Brave Search API skill. Supports web search, video search, image search, news search, AI grounding (RAG), AI answer generation, local POI queries, query suggestions, and spell checking. Use this skill proactively when users need to search the internet, get real-time information, perform RAG grounding, find local businesses, or need AI-generated answers.
---

# Brave Search API Comprehensive Skill

Brave Search API provides powerful search capabilities, including traditional search and AI-enhanced features.

> **API Key**: Get one at https://api.search.brave.com
>
> **Authentication**: `X-Subscription-Token: <API_KEY>` header

## Feature Selection Guide

Choose the appropriate endpoint based on your needs:

| Use Case | Recommended Endpoint | Description |
|----------|---------------------|-------------|
| General web search | **web-search** | Most comprehensive search, returns links, snippets, structured data |
| Find videos | **videos-search** | Focused on video results, includes duration, views, creator info |
| Find images | **images-search** | Image search, up to 200 results, includes dimensions |
| Find news | **news-search** | News articles, supports time filtering and date ranges |
| LLM/AI grounding | **llm-context** | Returns pre-extracted web content for RAG/Agents |
| AI-generated answers | **answers** | OpenAI-compatible AI answers with citations |
| Local business lookup | **local-pois** | Get business details (ratings, hours, contact info) |
| Business descriptions | **local-descriptions** | AI-generated POI description text |
| Query autocomplete | **suggest** | Search box autocomplete, <100ms response |
| Spell correction | **spellcheck** | Standalone spell checking |

## Quick Decision Flow

```
What type of results do you need?
├── Web/General → web-search
├── Videos → videos-search
├── Images → images-search
├── News → news-search
├── AI-related
│   ├── Need LLM grounding content → llm-context
│   └── Need complete AI answer → answers
├── Local/Business
│   ├── Need structured info → local-pois (requires ID from web-search first)
│   └── Need description text → local-descriptions
├── Input assistance
│   ├── Autocomplete → suggest
│   └── Spell checking → spellcheck
```

## Common Parameters

### General Parameters

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `q` | string | - | **Required**, search query (1-400 chars, max 50 words) |
| `country` | string | `US` | Search country (2-letter country code or `ALL`) |
| `search_lang` | string | `en` | Language preference (2+ char language code) |
| `safesearch` | string | `moderate` | Adult content filter (`off`/`moderate`/`strict`) |
| `spellcheck` | bool | `true` | Auto-correct query |

### Freshness Filters

| Value | Description |
|-------|-------------|
| `pd` | Past 24 hours |
| `pw` | Past 7 days |
| `pm` | Past 31 days |
| `py` | Past 365 days |
| `YYYY-MM-DDtoYYYY-MM-DD` | Custom date range |

### Search Operators

| Operator | Syntax | Description |
|----------|--------|-------------|
| Site limit | `site:example.com` | Limit to specific domain |
| File type | `ext:pdf` | Specific file extension |
| Title contains | `intitle:keyword` | Title contains keyword |
| Exact match | `"exact phrase"` | Exact match |
| Exclude | `-keyword` | Exclude results containing term |

## Goggles Custom Ranking (Unique to Brave)

Goggles allow you to customize search result ranking rules.

**Syntax**: `$boost=N` / `$downrank=N` (1-10), `$discard`, `$site=example.com`

**Usage**:
```bash
# Hosted Goggles (requires registration)
--data-urlencode "goggles=https://raw.githubusercontent.com/.../goggle.goggle"

# Inline rules (no registration needed)
--data-urlencode 'goggles=$discard\n$site=docs.python.org\n$site=developer.mozilla.org'
```

**Common patterns**:
- **Allow list**: `$discard\n$site=docs.python.org\n$site=developer.mozilla.org`
- **Block list**: `$discard,site=pinterest.com\n$discard,site=quora.com`

## Location-Aware Headers

For location-relevant search results:

| Header | Type | Description |
|--------|------|-------------|
| `X-Loc-Lat` | float | Latitude (-90.0 to 90.0) |
| `X-Loc-Long` | float | Longitude (-180.0 to 180.0) |
| `X-Loc-City` | string | City name |
| `X-Loc-State` | string | State/region code |
| `X-Loc-Country` | string | 2-letter country code |

> **Priority**: `X-Loc-Lat` + `X-Loc-Long` take precedence. When coordinates are provided, text-based location headers are not used for resolution.

## Common Request Example

```bash
# Basic web search
curl -s "https://api.search.brave.com/res/v1/web/search?q=python+tutorials" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"

# Search with parameters
curl -s "https://api.search.brave.com/res/v1/web/search" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -G \
  --data-urlencode "q=rust programming" \
  --data-urlencode "country=US" \
  --data-urlencode "search_lang=en" \
  --data-urlencode "count=10" \
  --data-urlencode "freshness=pm"
```

## Detailed API References

For complete documentation of each feature, see the corresponding reference files:

| Reference | Description |
|-----------|-------------|
| [references/web-search.md](references/web-search.md) | Web search complete parameters and response format |
| [references/videos-search.md](references/videos-search.md) | Video search detailed documentation |
| [references/images-search.md](references/images-search.md) | Image search detailed documentation |
| [references/news-search.md](references/news-search.md) | News search detailed documentation |
| [references/llm-context.md](references/llm-context.md) | LLM grounding/RAG detailed documentation |
| [references/answers.md](references/answers.md) | AI answer generation detailed documentation |
| [references/local-pois.md](references/local-pois.md) | Local POI query detailed documentation |
| [references/local-descriptions.md](references/local-descriptions.md) | POI description detailed documentation |
| [references/suggest.md](references/suggest.md) | Query suggestion detailed documentation |
| [references/spellcheck.md](references/spellcheck.md) | Spell check detailed documentation |

## Common Use Case Scenarios

### Scenario 1: Building a Search Interface
```
User input → suggest (completion suggestions)
          → web-search (execute search)
          → Optional: videos-search / images-search (categorized results)
```

### Scenario 2: AI Agent / RAG System
```
User question → llm-context (get grounding content)
             → Process content to generate answer
```

### Scenario 3: Deep Research
```
Research topic → answers (enable_research=true)
              → Get multi-iteration synthesized answer
```

### Scenario 4: Local Business Query
```
Business search → web-search (result_filter=locations)
               → local-pois (get detailed info)
               → local-descriptions (get descriptions)
```

## Plan Requirements

| Feature | Required Plan |
|---------|---------------|
| web-search, videos-search, images-search, news-search | Search |
| llm-context | Search |
| local-pois, local-descriptions | Search |
| answers | Answers |
| suggest | Suggest |
| spellcheck | Spellcheck |

Subscribe at: https://api-dashboard.search.brave.com/app/subscriptions/subscribe

---
name: tick-alltick-api
description: Alltick-exclusive real-time market data API for stocks, forex, and cryptocurrency. Use this skill to fetch K-line/candlestick data, latest trade prices, order book depth, and stock fundamentals. Proactively use this skill when users need to query stock quotes, K-line chart data, real-time prices, order book data, forex rates, or cryptocurrency prices. This skill only supports Alltick API (https://alltick.co/).
---

# Alltick Market Data API Skill

This is an [Alltick](https://alltick.co/)-exclusive skill for retrieving real-time financial market data, supporting stocks, forex, cryptocurrency, precious metals, and other financial instruments.

## Supported Data Types

### Product Categories
- **Stocks**: US stocks, Hong Kong stocks, A-shares, index data
- **Forex**: Major currency pairs
- **Cryptocurrency**: Mainstream digital currencies
- **Commodities**: Precious metals, crude oil, CFD indices, etc.

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kline` | GET | Single product historical K-line query (max 500 candles) |
| `/batch-kline` | POST | Batch query for latest 2 K-lines |
| `/trade-tick` | GET | Latest trade price/tick data query |
| `/depth-tick` | GET | Latest order book query |
| `/static_info` | GET | Stock product basic information query |

## API Endpoints

### Stock API
- Base URL: `https://quote.alltick.co/quote-stock-b-api`

### Forex/Crypto/Commodities API
- Base URL: `https://quote.alltick.co/quote-b-api`

## API Key Configuration

API Key can be provided through one of the following methods:

1. **Config file**: Configure in `~/.c4alpha/config.toml` (Recommended)
   ```toml
   [[tick.providers]]
   name = "alltick"
   api-key = "your-alltick-api-key-here"
   ```

2. **Environment variable**: Set `ALLTICK_TOKEN` environment variable

3. **Direct parameter**: Pass token parameter directly when calling

## Code Usage

Use the `AlltickClient` class from `scripts/alltick_client.py` to call the API:

```python
from scripts.alltick_client import AlltickClient

# Initialize client (automatically reads API Key from config)
client = AlltickClient()

# Or pass token directly
client = AlltickClient(token="your-token-here")

# Query stock K-line
kline_data = client.get_kline(
    code="700.HK",           # Stock code
    kline_type=1,            # 1=1-minute K-line
    query_kline_num=10       # Query 10 K-lines
)

# Batch query latest trade prices
tick_data = client.get_trade_tick(
    codes=["700.HK", "AAPL.US"]
)

# Query order book depth
depth_data = client.get_depth_tick(
    codes=["700.HK"]
)

# Get stock basic information
info = client.get_static_info(
    codes=["700.HK", "AAPL.US"]
)
```

## K-line Types

| Value | Type |
|-------|------|
| 1 | 1-minute |
| 2 | 5-minute |
| 3 | 15-minute |
| 4 | 30-minute |
| 5 | 1-hour |
| 6 | 2-hour (not supported for stocks) |
| 7 | 4-hour (not supported for stocks) |
| 8 | Daily |
| 9 | Weekly |
| 10 | Monthly |

## Stock Code Format

- **Hong Kong Stocks**: `{code}.HK`, e.g., `700.HK` (Tencent), `9988.HK` (Alibaba)
- **US Stocks**: `{code}.US`, e.g., `AAPL.US` (Apple), `GOOGL.US` (Google)
- **A-shares**: `{code}.SH` or `{code}.SZ`, e.g., `600519.SH` (Kweichow Moutai)

## Rate Limits

Rate limits vary by subscription plan:

| Plan | Single Request | Daily Limit |
|------|----------------|-------------|
| Free | 1 per 10 seconds | 14,400 requests |
| Basic | 1 per second | 86,400 requests |
| Premium | 10 per second | 864,000 requests |
| Professional | 20 per second | 1,728,000 requests |

**Note**: The `/batch-kline` endpoint has additional time interval requirements, please refer to the API documentation.

## Detailed API Reference

For complete API documentation, please refer to:
- [K-line Query](references/kline_api.md)
- [Trade Price Query](references/trade_tick_api.md)
- [Order Book Query](references/depth_tick_api.md)

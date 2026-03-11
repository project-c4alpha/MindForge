# K-line Query API Reference

## Single Product Historical K-line Query

### Endpoint
- Stocks: `GET /quote-stock-b-api/kline`
- Forex/Crypto: `GET /quote-b-api/kline`

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| code | string | Yes | Product code |
| kline_type | int | Yes | K-line type (1-10) |
| kline_timestamp_end | int | Yes | End timestamp, 0 for latest |
| query_kline_num | int | Yes | Number of K-lines, max 500 |
| adjust_type | int | Yes | Adjustment type (0=ex-rights, 1=front-adjusted) |

### K-line Types
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

### Response Example
```json
{
  "ret": 200,
  "msg": "ok",
  "data": {
    "code": "700.HK",
    "kline_type": 1,
    "kline_list": [
      {
        "timestamp": "1677829200",
        "open_price": "136.421",
        "close_price": "136.412",
        "high_price": "136.422",
        "low_price": "136.407",
        "volume": "0",
        "turnover": "0"
      }
    ]
  }
}
```

## Batch Query Latest K-lines

### Endpoint
- Stocks: `POST /quote-stock-b-api/batch-kline`
- Forex/Crypto: `POST /quote-b-api/batch-kline`

### Request Body
```json
{
  "trace": "uuid",
  "data": {
    "data_list": [
      {
        "code": "700.HK",
        "kline_type": 1,
        "kline_timestamp_end": 0,
        "query_kline_num": 2,
        "adjust_type": 0
      }
    ]
  }
}
```

### Notes
- Batch query can only retrieve up to 2 K-lines
- Different subscription plans have different request interval requirements

# Trade Price Query API Reference

## Latest Trade Price Batch Query

### Endpoint
- Stocks: `GET /quote-stock-b-api/trade-tick`
- Forex/Crypto: `GET /quote-b-api/trade-tick`

### Request Parameters

Query parameters need to be URL encoded:

```json
{
  "trace": "uuid",
  "data": {
    "symbol_list": [
      {"code": "700.HK"},
      {"code": "AAPL.US"}
    ]
  }
}
```

### Response Example
```json
{
  "ret": 200,
  "msg": "ok",
  "data": {
    "tick_list": [
      {
        "code": "700.HK",
        "seq": "30841439",
        "tick_time": "1677831545217",
        "price": "136.302",
        "volume": "0",
        "turnover": "0",
        "trade_direction": 0
      }
    ]
  }
}
```

### Field Descriptions
| Field | Description |
|-------|-------------|
| code | Product code |
| seq | Sequence number |
| tick_time | Timestamp (milliseconds) |
| price | Trade price |
| volume | Volume |
| turnover | Turnover |
| trade_direction | Trade direction (0=default, 1=BUY, 2=SELL) |

### Notes
- Supports batch query, recommended max 50 products per request
- Historical data query not supported

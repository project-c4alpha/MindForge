# Order Book Query API Reference

## Latest Order Book Query

### Endpoint
- Stocks: `GET /quote-stock-b-api/depth-tick`
- Forex/Crypto: `GET /quote-b-api/depth-tick`

### Order Book Depth by Product Type

| Product Type | Max Depth |
|--------------|-----------|
| Forex, precious metals, crude oil, CFD indices | 1 level |
| Cryptocurrency | 5 levels |
| Hong Kong stocks | 10 levels |
| US stocks | 1 level |
| A-shares | 5 levels |

### Request Parameters

Query parameters need to be URL encoded:

```json
{
  "trace": "uuid",
  "data": {
    "symbol_list": [
      {"code": "700.HK"}
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
        "seq": "30686349",
        "tick_time": "1677830357227",
        "bids": [
          {
            "price": "136.424",
            "volume": "100000.00"
          }
        ],
        "asks": [
          {
            "price": "136.427",
            "volume": "400000.00"
          }
        ]
      }
    ]
  }
}
```

### Field Descriptions
| Field | Description |
|-------|-------------|
| code | Product code |
| seq | Quote sequence number |
| tick_time | Quote timestamp (milliseconds) |
| bids | Bid list (sorted by price descending) |
| asks | Ask list (sorted by price ascending) |
| price | Order price |
| volume | Order volume |

### Notes
- Inactive products may have fewer depth levels
- One-sided order book may be empty during limit up/down
- Volume not provided for forex, precious metals, and CFD indices

# 成交价查询 API 参考

## 最新成交价批量查询

### 端点
- 股票: `GET /quote-stock-b-api/trade-tick`
- 外汇/加密货币: `GET /quote-b-api/trade-tick`

### 请求参数

Query 参数需要进行 URL 编码：

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

### 响应示例
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

### 字段说明
| 字段 | 说明 |
|------|------|
| code | 产品代码 |
| seq | 序号 |
| tick_time | 时间戳 (毫秒) |
| price | 成交价 |
| volume | 成交量 |
| turnover | 成交额 |
| trade_direction | 交易方向 (0=默认, 1=BUY, 2=SELL) |

### 注意事项
- 支持批量查询，建议每次最多50个产品
- 不支持历史数据查询

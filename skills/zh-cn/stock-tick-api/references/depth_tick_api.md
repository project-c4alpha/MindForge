# 盘口查询 API 参考

## 最新盘口(Order Book)查询

### 端点
- 股票: `GET /quote-stock-b-api/depth-tick`
- 外汇/加密货币: `GET /quote-b-api/depth-tick`

### 盘口深度说明

| 产品类型 | 最大深度 |
|----------|----------|
| 外汇、贵金属、原油、CFD指数 | 1档 |
| 加密货币 | 5档 |
| 港股 | 10档 |
| 美股 | 1档 |
| 沪深A股 | 5档 |

### 请求参数

Query 参数需要进行 URL 编码：

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

### 响应示例
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

### 字段说明
| 字段 | 说明 |
|------|------|
| code | 产品代码 |
| seq | 报价序号 |
| tick_time | 报价时间戳 (毫秒) |
| bids | 买盘列表 (按价格降序) |
| asks | 卖盘列表 (按价格升序) |
| price | 委托价 |
| volume | 委托量 |

### 注意事项
- 不活跃产品可能档位较少
- 涨跌停时单边盘口可能为空
- 外汇、贵金属、CFD指数不提供 volume

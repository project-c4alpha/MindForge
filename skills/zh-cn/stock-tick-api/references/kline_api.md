# K线查询 API 参考

## 单产品历史K线查询

### 端点
- 股票: `GET /quote-stock-b-api/kline`
- 外汇/加密货币: `GET /quote-b-api/kline`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 产品代码 |
| kline_type | int | 是 | K线类型 (1-10) |
| kline_timestamp_end | int | 是 | 结束时间戳，0表示最新 |
| query_kline_num | int | 是 | K线数量，最多500 |
| adjust_type | int | 是 | 复权类型 (0=除权, 1=前复权) |

### K线类型
| 值 | 类型 |
|----|------|
| 1 | 1分钟K |
| 2 | 5分钟K |
| 3 | 15分钟K |
| 4 | 30分钟K |
| 5 | 小时K |
| 6 | 2小时K (股票不支持) |
| 7 | 4小时K (股票不支持) |
| 8 | 日K |
| 9 | 周K |
| 10 | 月K |

### 响应示例
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

## 批量查询最新K线

### 端点
- 股票: `POST /quote-stock-b-api/batch-kline`
- 外汇/加密货币: `POST /quote-b-api/batch-kline`

### 请求体
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

### 注意事项
- 批量查询最多只能获取2根K线
- 根据订阅计划有不同的请求间隔要求

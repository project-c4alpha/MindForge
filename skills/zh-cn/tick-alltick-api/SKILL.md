---
name: tick-alltick-api
description: Alltick 专属的股票、外汇、加密货币实时行情数据获取技能。使用此技能获取K线数据、最新成交价、盘口深度、股票基础信息等。当用户需要查询股票行情、K线图数据、实时价格、盘口数据、外汇行情、加密货币价格时，请主动使用此技能。此技能仅支持 Alltick API (https://alltick.co/)。
---

# Alltick 行情数据 API 技能

这是 [Alltick](https://alltick.co/) 专属的金融行情数据获取技能，支持股票、外汇、加密货币、贵金属等多种金融产品的实时数据查询。

## 支持的数据类型

### 产品类别
- **股票**: 美股、港股、A股、大盘数据
- **外汇**: 主要货币对
- **加密货币**: 主流数字货币
- **商品**: 贵金属、原油、CFD指数等

### 数据接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/kline` | GET | 单产品历史K线查询（最多500根） |
| `/batch-kline` | POST | 批量查询最新2根K线 |
| `/trade-tick` | GET | 最新成交价/逐笔数据查询 |
| `/depth-tick` | GET | 最新盘口(Order Book)查询 |
| `/static_info` | GET | 股票产品基础信息查询 |

## API 端点

### 股票 API
- 基础路径: `https://quote.alltick.co/quote-stock-b-api`

### 外汇/加密货币/商品 API
- 基础路径: `https://quote.alltick.co/quote-b-api`

## API Key 配置

API Key 需要通过以下方式之一提供：

1. **配置文件**: 在 `~/.c4alpha/config.toml` 中配置（推荐）
   ```toml
   [[tick.providers]]
   name = "alltick"
   api-key = "your-alltick-api-key-here"
   ```

2. **环境变量**: 设置 `ALLTICK_TOKEN` 环境变量

3. **直接传入**: 在调用时直接传入 token 参数

## 代码使用

使用 `scripts/alltick_client.py` 中的 `AlltickClient` 类来调用 API：

```python
from scripts.alltick_client import AlltickClient

# 初始化客户端（会自动从配置文件读取 API Key）
client = AlltickClient()

# 或直接传入 token
client = AlltickClient(token="your-token-here")

# 查询股票K线
kline_data = client.get_kline(
    code="700.HK",           # 股票代码
    kline_type=1,            # 1=1分钟K线
    query_kline_num=10       # 查询10根K线
)

# 批量查询最新成交价
tick_data = client.get_trade_tick(
    codes=["700.HK", "AAPL.US"]
)

# 查询盘口深度
depth_data = client.get_depth_tick(
    codes=["700.HK"]
)

# 获取股票基础信息
info = client.get_static_info(
    codes=["700.HK", "AAPL.US"]
)
```

## K线类型说明

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

## 股票代码格式

- **港股**: `{代码}.HK`，如 `700.HK` (腾讯)、`9988.HK` (阿里巴巴)
- **美股**: `{代码}.US`，如 `AAPL.US` (苹果)、`GOOGL.US` (谷歌)
- **A股**: `{代码}.SH` 或 `{代码}.SZ`，如 `600519.SH` (贵州茅台)

## 请求频率限制

根据订阅计划不同，请求频率限制不同：

| 计划 | 单独请求 | 每日限额 |
|------|----------|----------|
| 免费 | 每10秒1次 | 14,400 次 |
| 基础 | 每1秒1次 | 86,400 次 |
| 高级 | 每1秒10次 | 864,000 次 |
| 专业 | 每1秒20次 | 1,728,000 次 |

**注意**: `/batch-kline` 接口有额外的时间间隔要求，请参考接口文档。

## 批量获取脚本

使用 `scripts/fetch_all_ticks.py` 可以按顺序获取多种 K 线数据，自动控制调用间隔：

```bash
# 获取所有类型（1分钟、5分钟、日K），默认间隔 10 秒
python3 scripts/fetch_all_ticks.py --code 700.HK

# 保存到指定目录
python3 scripts/fetch_all_ticks.py --code 700.HK --output-dir ~/stock_data

# 自定义类型和间隔
python3 scripts/fetch_all_ticks.py --code 700.HK --types 1min,daily --interval 15

# 输出到单个文件
python3 scripts/fetch_all_ticks.py --code 700.HK --dump-file result.json
```

**可用类型**: `1min`, `5min`, `15min`, `30min`, `hour`, `daily`, `week`, `month`

## 详细 API 参考

完整的 API 文档请参考：
- [K线查询](references/kline_api.md)
- [成交价查询](references/trade_tick_api.md)
- [盘口查询](references/depth_tick_api.md)

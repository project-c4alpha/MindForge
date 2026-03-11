#!/usr/bin/env python3
"""
Alltick 金融数据 API 客户端

支持股票、外汇、加密货币、贵金属等金融产品的实时行情数据查询。

使用示例:
    from alltick_client import AlltickClient

    client = AlltickClient()

    # 查询K线
    kline = client.get_kline("700.HK", kline_type=1, query_kline_num=10)

    # 查询最新成交价
    tick = client.get_trade_tick(["700.HK", "AAPL.US"])

    # 查询盘口
    depth = client.get_depth_tick(["700.HK"])

    # 获取股票基础信息
    info = client.get_static_info(["700.HK"])
"""

# 抑制 macOS LibreSSL 兼容性警告
import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import os
import json
import uuid
import urllib.parse
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass
from enum import IntEnum

import requests
try:
    import tomllib
except ImportError:
    import tomli as tomllib


class KlineType(IntEnum):
    """K线类型枚举"""
    MINUTE_1 = 1      # 1分钟K
    MINUTE_5 = 2      # 5分钟K
    MINUTE_15 = 3     # 15分钟K
    MINUTE_30 = 4     # 30分钟K
    HOUR_1 = 5        # 小时K
    HOUR_2 = 6        # 2小时K (股票不支持)
    HOUR_4 = 7        # 4小时K (股票不支持)
    DAY = 8           # 日K
    WEEK = 9          # 周K
    MONTH = 10        # 月K


class AdjustType(IntEnum):
    """复权类型枚举"""
    NONE = 0          # 除权
    FRONT = 1         # 前复权


class MarketType(IntEnum):
    """市场类型枚举"""
    STOCK = 1         # 股票 (美股、港股、A股、大盘)
    FOREX_CRYPTO = 2  # 外汇、加密货币、贵金属、商品


@dataclass
class APIConfig:
    """API 配置"""
    stock_base_url: str = "https://quote.alltick.co/quote-stock-b-api"
    forex_crypto_base_url: str = "https://quote.alltick.co/quote-b-api"
    timeout: int = 30


class AlltickClient:
    """
    Alltick 金融数据 API 客户端

    支持获取K线数据、最新成交价、盘口深度、股票基础信息等。

    Token 优先级:
        1. 构造函数传入的 token
        2. 环境变量 ALLTICK_TOKEN
        3. 配置文件 ~/.c4alpha/config.toml 中的 [[tick.providers]] (name="alltick")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        config: Optional[APIConfig] = None
    ):
        """
        初始化客户端

        Args:
            token: API Token，如果不传则从配置文件或环境变量读取
            config: API 配置，默认使用默认配置
        """
        self.config = config or APIConfig()
        self._token = token or self._load_token()

    def _load_token(self) -> str:
        """
        从配置文件或环境变量加载 Token

        Returns:
            Token 字符串

        Raises:
            ValueError: 如果找不到 Token
        """
        # 1. 尝试从环境变量读取
        token = os.environ.get("ALLTICK_TOKEN")
        if token:
            return token

        # 2. 尝试从配置文件读取
        config_path = os.path.expanduser("~/.c4alpha/config.toml")
        if os.path.exists(config_path):
            try:
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)
                    # 新格式: [[tick.providers]] 数组表
                    providers = config_data.get("tick", {}).get("providers", [])
                    for provider in providers:
                        if provider.get("name") == "alltick":
                            token = provider.get("api-key")
                            if token:
                                return token
                    # 兼容旧格式: tickProvider.token
                    token = config_data.get("tickProvider", {}).get("token")
                    if token:
                        return token
            except Exception as e:
                pass

        raise ValueError(
            "未找到 API Token。请通过以下方式之一提供 Token:\n"
            "1. 在构造函数中传入 token 参数\n"
            "2. 设置环境变量 ALLTICK_TOKEN\n"
            "3. 在 ~/.c4alpha/config.toml 中配置:\n"
            "   [[tick.providers]]\n"
            "   name = \"alltick\"\n"
            "   api-key = \"your-api-key\""
        )

    def _get_base_url(self, market: MarketType) -> str:
        """获取对应市场的基础 URL"""
        if market == MarketType.STOCK:
            return self.config.stock_base_url
        return self.config.forex_crypto_base_url

    def _generate_trace(self) -> str:
        """生成唯一的追踪 ID"""
        return str(uuid.uuid4())

    def _detect_market(self, code: str) -> MarketType:
        """
        根据股票代码自动检测市场类型

        Args:
            code: 股票代码，如 "700.HK", "AAPL.US", "BTCUSD"

        Returns:
            市场类型
        """
        # 股票代码格式: XXX.HK, XXX.US, XXX.SH, XXX.SZ
        if code.endswith((".HK", ".US", ".SH", ".SZ")):
            return MarketType.STOCK
        # 外汇、加密货币等
        return MarketType.FOREX_CRYPTO

    def _make_get_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        market: Optional[MarketType] = None
    ) -> Dict[str, Any]:
        """
        发送 GET 请求

        Args:
            endpoint: API 端点
            data: 请求数据
            market: 市场类型，如果不传则自动检测

        Returns:
            API 响应数据
        """
        if market is None:
            # 从 data 中的 codes 检测市场
            codes = data.get("data", {}).get("symbol_list", [])
            if codes:
                market = self._detect_market(codes[0].get("code", ""))
            else:
                market = MarketType.STOCK

        base_url = self._get_base_url(market)
        query_str = urllib.parse.quote(json.dumps(data))

        url = f"{base_url}/{endpoint}?token={self._token}&query={query_str}"

        response = requests.get(url, timeout=self.config.timeout)
        response.raise_for_status()

        result = response.json()
        if result.get("ret") != 200:
            raise APIError(
                result.get("ret"),
                result.get("msg", "Unknown error"),
                result.get("trace")
            )

        return result

    def _make_post_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        market: Optional[MarketType] = None
    ) -> Dict[str, Any]:
        """
        发送 POST 请求

        Args:
            endpoint: API 端点
            data: 请求数据
            market: 市场类型

        Returns:
            API 响应数据
        """
        if market is None:
            # 从 data 中的 data_list 检测市场
            data_list = data.get("data", {}).get("data_list", [])
            if data_list:
                market = self._detect_market(data_list[0].get("code", ""))
            else:
                market = MarketType.STOCK

        base_url = self._get_base_url(market)
        url = f"{base_url}/{endpoint}?token={self._token}"

        response = requests.post(
            url,
            json=data,
            timeout=self.config.timeout,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        result = response.json()
        if result.get("ret") != 200:
            raise APIError(
                result.get("ret"),
                result.get("msg", "Unknown error"),
                result.get("trace")
            )

        return result

    def get_kline(
        self,
        code: str,
        kline_type: int = KlineType.MINUTE_1,
        query_kline_num: int = 100,
        kline_timestamp_end: int = 0,
        adjust_type: int = AdjustType.NONE,
        market: Optional[MarketType] = None
    ) -> Dict[str, Any]:
        """
        查询单产品历史K线

        Args:
            code: 产品代码，如 "700.HK", "AAPL.US"
            kline_type: K线类型，见 KlineType 枚举
            query_kline_num: 查询K线数量，最多500根
            kline_timestamp_end: 结束时间戳，0表示从最新开始
            adjust_type: 复权类型，见 AdjustType 枚举
            market: 市场类型，如果不传则自动检测

        Returns:
            K线数据，包含:
            - code: 产品代码
            - kline_type: K线类型
            - kline_list: K线列表，每根K线包含:
                - timestamp: 时间戳
                - open_price: 开盘价
                - close_price: 收盘价
                - high_price: 最高价
                - low_price: 最低价
                - volume: 成交量
                - turnover: 成交额

        Example:
            >>> client = AlltickClient()
            >>> kline = client.get_kline("700.HK", kline_type=1, query_kline_num=10)
            >>> for k in kline["data"]["kline_list"]:
            ...     print(f"时间: {k['timestamp']}, 收盘价: {k['close_price']}")
        """
        if market is None:
            market = self._detect_market(code)

        data = {
            "trace": self._generate_trace(),
            "data": {
                "code": code,
                "kline_type": kline_type,
                "kline_timestamp_end": kline_timestamp_end,
                "query_kline_num": min(query_kline_num, 500),
                "adjust_type": adjust_type
            }
        }

        return self._make_get_request("kline", data, market)

    def get_batch_kline(
        self,
        codes: List[str],
        kline_type: int = KlineType.MINUTE_1,
        query_kline_num: int = 2,
        kline_timestamp_end: int = 0,
        adjust_type: int = AdjustType.NONE,
        market: Optional[MarketType] = None
    ) -> Dict[str, Any]:
        """
        批量查询多个产品的最新K线

        注意: 此接口只能查询最新的2根K线

        Args:
            codes: 产品代码列表
            kline_type: K线类型
            query_kline_num: 查询K线数量，最多2根
            kline_timestamp_end: 结束时间戳
            adjust_type: 复权类型
            market: 市场类型

        Returns:
            批量K线数据

        Example:
            >>> client = AlltickClient()
            >>> klines = client.get_batch_kline(
            ...     ["700.HK", "AAPL.US"],
            ...     kline_type=KlineType.DAY
            ... )
        """
        if market is None and codes:
            market = self._detect_market(codes[0])

        data_list = [
            {
                "code": code,
                "kline_type": kline_type,
                "kline_timestamp_end": kline_timestamp_end,
                "query_kline_num": min(query_kline_num, 2),
                "adjust_type": adjust_type
            }
            for code in codes
        ]

        data = {
            "trace": self._generate_trace(),
            "data": {
                "data_list": data_list
            }
        }

        return self._make_post_request("batch-kline", data, market)

    def get_trade_tick(
        self,
        codes: List[str],
        market: Optional[MarketType] = None
    ) -> Dict[str, Any]:
        """
        查询最新成交价（逐笔tick数据）

        Args:
            codes: 产品代码列表
            market: 市场类型

        Returns:
            成交价数据，包含:
            - tick_list: 成交列表，每个包含:
                - code: 产品代码
                - seq: 序号
                - tick_time: 时间戳
                - price: 成交价
                - volume: 成交量
                - turnover: 成交额
                - trade_direction: 交易方向 (0=默认, 1=BUY, 2=SELL)

        Example:
            >>> client = AlltickClient()
            >>> tick = client.get_trade_tick(["700.HK", "AAPL.US"])
            >>> for t in tick["data"]["tick_list"]:
            ...     print(f"{t['code']}: {t['price']}")
        """
        if market is None and codes:
            market = self._detect_market(codes[0])

        data = {
            "trace": self._generate_trace(),
            "data": {
                "symbol_list": [{"code": code} for code in codes]
            }
        }

        return self._make_get_request("trade-tick", data, market)

    def get_depth_tick(
        self,
        codes: List[str],
        market: Optional[MarketType] = None
    ) -> Dict[str, Any]:
        """
        查询最新盘口(Order Book)

        Args:
            codes: 产品代码列表
            market: 市场类型

        Returns:
            盘口数据，包含:
            - tick_list: 盘口列表，每个包含:
                - code: 产品代码
                - seq: 报价序号
                - tick_time: 报价时间戳
                - bids: 买盘列表 [{price, volume}, ...]
                - asks: 卖盘列表 [{price, volume}, ...]

        Example:
            >>> client = AlltickClient()
            >>> depth = client.get_depth_tick(["700.HK"])
            >>> for t in depth["data"]["tick_list"]:
            ...     print(f"买一: {t['bids'][0]['price'] if t['bids'] else 'N/A'}")
            ...     print(f"卖一: {t['asks'][0]['price'] if t['asks'] else 'N/A'}")
        """
        if market is None and codes:
            market = self._detect_market(codes[0])

        data = {
            "trace": self._generate_trace(),
            "data": {
                "symbol_list": [{"code": code} for code in codes]
            }
        }

        return self._make_get_request("depth-tick", data, market)

    def get_static_info(
        self,
        codes: List[str]
    ) -> Dict[str, Any]:
        """
        查询股票产品基础信息

        注意: 此接口仅支持股票产品

        Args:
            codes: 股票代码列表

        Returns:
            股票基础信息，包含:
            - static_info_list: 信息列表，每个包含:
                - symbol: 产品代码
                - name_cn: 中文名称
                - name_en: 英文名称
                - name_hk: 繁体中文名称
                - exchange: 交易所
                - currency: 交易币种
                - lot_size: 每手股数
                - total_shares: 总股本
                - circulating_shares: 流通股本
                - eps: 每股盈利
                - bps: 每股净资产
                - dividend_yield: 股息率

        Example:
            >>> client = AlltickClient()
            >>> info = client.get_static_info(["700.HK", "AAPL.US"])
            >>> for s in info["data"]["static_info_list"]:
            ...     print(f"{s['symbol']}: {s['name_cn']}")
        """
        data = {
            "trace": self._generate_trace(),
            "data": {
                "symbol_list": [{"code": code} for code in codes]
            }
        }

        # static_info 只有股票 API
        return self._make_get_request("static_info", data, MarketType.STOCK)


class APIError(Exception):
    """API 错误"""

    def __init__(self, code: int, message: str, trace: Optional[str] = None):
        self.code = code
        self.message = message
        self.trace = trace
        super().__init__(f"API Error {code}: {message}")


# 便捷函数
def get_client(token: Optional[str] = None) -> AlltickClient:
    """
    获取 Alltick 客户端实例

    Args:
        token: API Token，可选

    Returns:
        AlltickClient 实例
    """
    return AlltickClient(token=token)


def get_stock_price(codes: List[str], token: Optional[str] = None) -> Dict[str, Any]:
    """
    快速获取股票最新价格

    Args:
        codes: 股票代码列表
        token: API Token，可选

    Returns:
        价格数据
    """
    client = get_client(token)
    return client.get_trade_tick(codes)


def get_stock_kline(
    code: str,
    kline_type: int = KlineType.DAY,
    num: int = 30,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    快速获取股票K线

    Args:
        code: 股票代码
        kline_type: K线类型
        num: K线数量
        token: API Token，可选

    Returns:
        K线数据
    """
    client = get_client(token)
    return client.get_kline(code, kline_type=kline_type, query_kline_num=num)


if __name__ == "__main__":
    # 测试代码
    import argparse

    parser = argparse.ArgumentParser(description="Alltick 金融数据 API 客户端")
    parser.add_argument("--token", help="API Token")
    parser.add_argument("--code", default="700.HK", help="产品代码")
    parser.add_argument(
        "--action",
        choices=["kline", "tick", "depth", "info"],
        default="tick",
        help="操作类型"
    )
    parser.add_argument(
        "--kline-type",
        type=int,
        default=8,
        dest="kline_type",
        help="K线类型: 1=1分钟, 2=5分钟, 3=15分钟, 4=30分钟, 5=小时, 8=日K, 9=周K, 10=月K (默认: 8)"
    )
    parser.add_argument(
        "--query-kline-num",
        type=int,
        default=60,
        dest="query_kline_num",
        help="查询K线数量，最多500根 (默认: 60)"
    )
    parser.add_argument(
        "--dump-file",
        dest="dump_file",
        help="将 API 返回的原始 JSON 写入指定文件路径"
    )

    args = parser.parse_args()

    try:
        client = AlltickClient(token=args.token)

        if args.action == "kline":
            result = client.get_kline(args.code, kline_type=args.kline_type, query_kline_num=args.query_kline_num)
        elif args.action == "tick":
            result = client.get_trade_tick([args.code])
        elif args.action == "depth":
            result = client.get_depth_tick([args.code])
        elif args.action == "info":
            result = client.get_static_info([args.code])

        # 如果指定了 dump-file，将原始 JSON 写入文件
        if args.dump_file:
            dump_path = os.path.expanduser(args.dump_file)
            # 确保目录存在
            dump_dir = os.path.dirname(dump_path)
            if dump_dir and not os.path.exists(dump_dir):
                os.makedirs(dump_dir, exist_ok=True)
            with open(dump_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"JSON dumped to: {dump_path}")

        # 打印简要结果到 stdout
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

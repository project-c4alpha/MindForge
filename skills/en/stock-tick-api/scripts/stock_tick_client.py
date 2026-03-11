#!/usr/bin/env python3
"""
Alltick Financial Data API Client

Supports real-time market data queries for stocks, forex, cryptocurrency,
precious metals, and other financial instruments.

Usage:
    from stock_tick_client import AlltickClient

    client = AlltickClient()

    # Query K-line
    kline = client.get_kline("700.HK", kline_type=1, query_kline_num=10)

    # Query latest trade prices
    tick = client.get_trade_tick(["700.HK", "AAPL.US"])

    # Query order book
    depth = client.get_depth_tick(["700.HK"])

    # Get stock basic info
    info = client.get_static_info(["700.HK"])
"""

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
    """K-line type enumeration"""
    MINUTE_1 = 1      # 1-minute
    MINUTE_5 = 2      # 5-minute
    MINUTE_15 = 3     # 15-minute
    MINUTE_30 = 4     # 30-minute
    HOUR_1 = 5        # 1-hour
    HOUR_2 = 6        # 2-hour (not supported for stocks)
    HOUR_4 = 7        # 4-hour (not supported for stocks)
    DAY = 8           # Daily
    WEEK = 9          # Weekly
    MONTH = 10        # Monthly


class AdjustType(IntEnum):
    """Adjustment type enumeration"""
    NONE = 0          # No adjustment (ex-rights)
    FRONT = 1         # Front adjustment


class MarketType(IntEnum):
    """Market type enumeration"""
    STOCK = 1         # Stocks (US, HK, A-shares, indices)
    FOREX_CRYPTO = 2  # Forex, crypto, precious metals, commodities


@dataclass
class APIConfig:
    """API configuration"""
    stock_base_url: str = "https://quote.alltick.co/quote-stock-b-api"
    forex_crypto_base_url: str = "https://quote.alltick.co/quote-b-api"
    timeout: int = 30


class AlltickClient:
    """
    Alltick Financial Data API Client

    Supports fetching K-line data, latest trade prices, order book depth,
    and stock basic information.

    Token priority:
        1. Token passed to constructor
        2. ALLTICK_TOKEN environment variable
        3. tickProvider.token in ~/.c4alpha/config.toml
    """

    def __init__(
        self,
        token: Optional[str] = None,
        config: Optional[APIConfig] = None
    ):
        """
        Initialize the client

        Args:
            token: API Token, if not provided will be read from config or env
            config: API configuration, defaults to default config
        """
        self.config = config or APIConfig()
        self._token = token or self._load_token()

    def _load_token(self) -> str:
        """
        Load Token from config file or environment variable

        Returns:
            Token string

        Raises:
            ValueError: If token cannot be found
        """
        # 1. Try environment variable
        token = os.environ.get("ALLTICK_TOKEN")
        if token:
            return token

        # 2. Try config file
        config_path = os.path.expanduser("~/.c4alpha/config.toml")
        if os.path.exists(config_path):
            try:
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)
                    token = config_data.get("tickProvider", {}).get("token")
                    if token:
                        return token
            except Exception as e:
                pass

        raise ValueError(
            "API Token not found. Please provide Token via one of:\n"
            "1. Pass token parameter to constructor\n"
            "2. Set ALLTICK_TOKEN environment variable\n"
            "3. Configure tickProvider.token in ~/.c4alpha/config.toml"
        )

    def _get_base_url(self, market: MarketType) -> str:
        """Get base URL for the corresponding market"""
        if market == MarketType.STOCK:
            return self.config.stock_base_url
        return self.config.forex_crypto_base_url

    def _generate_trace(self) -> str:
        """Generate unique trace ID"""
        return str(uuid.uuid4())

    def _detect_market(self, code: str) -> MarketType:
        """
        Auto-detect market type based on product code

        Args:
            code: Product code, e.g., "700.HK", "AAPL.US", "BTCUSD"

        Returns:
            Market type
        """
        # Stock code format: XXX.HK, XXX.US, XXX.SH, XXX.SZ
        if code.endswith((".HK", ".US", ".SH", ".SZ")):
            return MarketType.STOCK
        # Forex, crypto, etc.
        return MarketType.FOREX_CRYPTO

    def _make_get_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        market: Optional[MarketType] = None
    ) -> Dict[str, Any]:
        """
        Send GET request

        Args:
            endpoint: API endpoint
            data: Request data
            market: Market type, auto-detected if not provided

        Returns:
            API response data
        """
        if market is None:
            # Detect market from codes in data
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
        Send POST request

        Args:
            endpoint: API endpoint
            data: Request data
            market: Market type

        Returns:
            API response data
        """
        if market is None:
            # Detect market from data_list in data
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
        Query single product historical K-line

        Args:
            code: Product code, e.g., "700.HK", "AAPL.US"
            kline_type: K-line type, see KlineType enum
            query_kline_num: Number of K-lines to query, max 500
            kline_timestamp_end: End timestamp, 0 means from latest
            adjust_type: Adjustment type, see AdjustType enum
            market: Market type, auto-detected if not provided

        Returns:
            K-line data containing:
            - code: Product code
            - kline_type: K-line type
            - kline_list: K-line list, each containing:
                - timestamp: Timestamp
                - open_price: Open price
                - close_price: Close price
                - high_price: High price
                - low_price: Low price
                - volume: Volume
                - turnover: Turnover

        Example:
            >>> client = AlltickClient()
            >>> kline = client.get_kline("700.HK", kline_type=1, query_kline_num=10)
            >>> for k in kline["data"]["kline_list"]:
            ...     print(f"Time: {k['timestamp']}, Close: {k['close_price']}")
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
        Batch query latest K-lines for multiple products

        Note: This endpoint can only query the latest 2 K-lines

        Args:
            codes: List of product codes
            kline_type: K-line type
            query_kline_num: Number of K-lines to query, max 2
            kline_timestamp_end: End timestamp
            adjust_type: Adjustment type
            market: Market type

        Returns:
            Batch K-line data

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
        Query latest trade prices (tick data)

        Args:
            codes: List of product codes
            market: Market type

        Returns:
            Trade price data containing:
            - tick_list: Trade list, each containing:
                - code: Product code
                - seq: Sequence number
                - tick_time: Timestamp
                - price: Trade price
                - volume: Volume
                - turnover: Turnover
                - trade_direction: Trade direction (0=default, 1=BUY, 2=SELL)

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
        Query latest order book

        Args:
            codes: List of product codes
            market: Market type

        Returns:
            Order book data containing:
            - tick_list: Order book list, each containing:
                - code: Product code
                - seq: Quote sequence number
                - tick_time: Quote timestamp
                - bids: Bid list [{price, volume}, ...]
                - asks: Ask list [{price, volume}, ...]

        Example:
            >>> client = AlltickClient()
            >>> depth = client.get_depth_tick(["700.HK"])
            >>> for t in depth["data"]["tick_list"]:
            ...     print(f"Bid 1: {t['bids'][0]['price'] if t['bids'] else 'N/A'}")
            ...     print(f"Ask 1: {t['asks'][0]['price'] if t['asks'] else 'N/A'}")
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
        Query stock product basic information

        Note: This endpoint only supports stock products

        Args:
            codes: List of stock codes

        Returns:
            Stock basic information containing:
            - static_info_list: Info list, each containing:
                - symbol: Product code
                - name_cn: Chinese name
                - name_en: English name
                - name_hk: Traditional Chinese name
                - exchange: Exchange
                - currency: Trading currency
                - lot_size: Shares per lot
                - total_shares: Total shares
                - circulating_shares: Circulating shares
                - eps: Earnings per share
                - bps: Book value per share
                - dividend_yield: Dividend yield

        Example:
            >>> client = AlltickClient()
            >>> info = client.get_static_info(["700.HK", "AAPL.US"])
            >>> for s in info["data"]["static_info_list"]:
            ...     print(f"{s['symbol']}: {s['name_en']}")
        """
        data = {
            "trace": self._generate_trace(),
            "data": {
                "symbol_list": [{"code": code} for code in codes]
            }
        }

        # static_info only available in stock API
        return self._make_get_request("static_info", data, MarketType.STOCK)


class APIError(Exception):
    """API Error"""

    def __init__(self, code: int, message: str, trace: Optional[str] = None):
        self.code = code
        self.message = message
        self.trace = trace
        super().__init__(f"API Error {code}: {message}")


# Convenience functions
def get_client(token: Optional[str] = None) -> AlltickClient:
    """
    Get Alltick client instance

    Args:
        token: API Token, optional

    Returns:
        AlltickClient instance
    """
    return AlltickClient(token=token)


def get_stock_price(codes: List[str], token: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick get stock latest prices

    Args:
        codes: List of stock codes
        token: API Token, optional

    Returns:
        Price data
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
    Quick get stock K-line

    Args:
        code: Stock code
        kline_type: K-line type
        num: Number of K-lines
        token: API Token, optional

    Returns:
        K-line data
    """
    client = get_client(token)
    return client.get_kline(code, kline_type=kline_type, query_kline_num=num)


if __name__ == "__main__":
    # Test code
    import argparse

    parser = argparse.ArgumentParser(description="Alltick Financial Data API Client")
    parser.add_argument("--token", help="API Token")
    parser.add_argument("--code", default="700.HK", help="Product code")
    parser.add_argument(
        "--action",
        choices=["kline", "tick", "depth", "info"],
        default="tick",
        help="Action type"
    )

    args = parser.parse_args()

    try:
        client = AlltickClient(token=args.token)

        if args.action == "kline":
            result = client.get_kline(args.code, kline_type=KlineType.DAY, query_kline_num=5)
        elif args.action == "tick":
            result = client.get_trade_tick([args.code])
        elif args.action == "depth":
            result = client.get_depth_tick([args.code])
        elif args.action == "info":
            result = client.get_static_info([args.code])

        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

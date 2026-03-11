#!/usr/bin/env python3
"""
Brave Search API 客户端

支持网页搜索、视频搜索、图片搜索、新闻搜索、AI接地(RAG)、AI答案生成等功能。

使用示例:
    from brave_search_client import BraveSearchClient

    client = BraveSearchClient()

    # 网页搜索
    results = client.web_search("python tutorials")

    # 视频搜索
    videos = client.videos_search("rust programming")

    # AI接地 (RAG)
    context = client.llm_context("what is machine learning")
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import requests
try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class APIConfig:
    """API 配置"""
    base_url: str = "https://api.search.brave.com/res/v1"
    timeout: int = 30


class BraveSearchClient:
    """
    Brave Search API 客户端

    支持网页搜索、视频搜索、图片搜索、新闻搜索、AI接地、AI答案等功能。

    API Key 优先级:
        1. 构造函数传入的 api_key
        2. 环境变量 BRAVE_SEARCH_API_KEY
        3. 配置文件 ~/.c4alpha/config.toml 中的 [[search.providers]] (name="brave")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[APIConfig] = None
    ):
        """
        初始化客户端

        Args:
            api_key: API Key，如果不传则从配置文件或环境变量读取
            config: API 配置，默认使用默认配置
        """
        self.config = config or APIConfig()
        self._api_key = api_key or self._load_api_key()

    def _load_api_key(self) -> str:
        """
        从配置文件或环境变量加载 API Key

        Returns:
            API Key 字符串

        Raises:
            ValueError: 如果找不到 API Key
        """
        # 1. 尝试从环境变量读取
        api_key = os.environ.get("BRAVE_SEARCH_API_KEY")
        if api_key:
            return api_key

        # 2. 尝试从配置文件读取
        config_path = os.path.expanduser("~/.c4alpha/config.toml")
        if os.path.exists(config_path):
            try:
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)
                    # 新格式: [[search.providers]] 数组表
                    providers = config_data.get("search", {}).get("providers", [])
                    for provider in providers:
                        if provider.get("name") == "brave":
                            api_key = provider.get("api-key")
                            if api_key:
                                return api_key
            except Exception as e:
                pass

        raise ValueError(
            "未找到 Brave Search API Key。请通过以下方式之一提供:\n"
            "1. 在构造函数中传入 api_key 参数\n"
            "2. 设置环境变量 BRAVE_SEARCH_API_KEY\n"
            "3. 在 ~/.c4alpha/config.toml 中配置:\n"
            "   [[search.providers]]\n"
            "   name = \"brave\"\n"
            "   api-key = \"your-api-key\""
        )

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Accept": "application/json",
            "X-Subscription-Token": self._api_key
        }

    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        发送 GET 请求

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            API 响应数据
        """
        url = f"{self.config.base_url}/{endpoint}"
        response = requests.get(
            url,
            headers=self._get_headers(),
            params=params,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def web_search(
        self,
        query: str,
        country: str = "US",
        search_lang: str = "en",
        count: int = 10,
        offset: int = 0,
        freshness: Optional[str] = None,
        safesearch: str = "moderate",
        **kwargs
    ) -> Dict[str, Any]:
        """
        网页搜索

        Args:
            query: 搜索查询
            country: 搜索国家
            search_lang: 语言偏好
            count: 返回结果数量
            offset: 偏移量
            freshness: 时间过滤 (pd/pw/pm/py 或日期范围)
            safesearch: 成人内容过滤

        Returns:
            搜索结果
        """
        params = {
            "q": query,
            "country": country,
            "search_lang": search_lang,
            "count": count,
            "offset": offset,
            "safesearch": safesearch,
            **kwargs
        }
        if freshness:
            params["freshness"] = freshness

        return self._make_request("web/search", params)

    def videos_search(
        self,
        query: str,
        country: str = "US",
        search_lang: str = "en",
        count: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        视频搜索

        Args:
            query: 搜索查询
            country: 搜索国家
            search_lang: 语言偏好
            count: 返回结果数量

        Returns:
            视频搜索结果
        """
        params = {
            "q": query,
            "country": country,
            "search_lang": search_lang,
            "count": count,
            **kwargs
        }
        return self._make_request("videos/search", params)

    def images_search(
        self,
        query: str,
        country: str = "US",
        search_lang: str = "en",
        count: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        图片搜索

        Args:
            query: 搜索查询
            country: 搜索国家
            search_lang: 语言偏好
            count: 返回结果数量

        Returns:
            图片搜索结果
        """
        params = {
            "q": query,
            "country": country,
            "search_lang": search_lang,
            "count": count,
            **kwargs
        }
        return self._make_request("images/search", params)

    def news_search(
        self,
        query: str,
        country: str = "US",
        search_lang: str = "en",
        count: int = 10,
        freshness: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        新闻搜索

        Args:
            query: 搜索查询
            country: 搜索国家
            search_lang: 语言偏好
            count: 返回结果数量
            freshness: 时间过滤

        Returns:
            新闻搜索结果
        """
        params = {
            "q": query,
            "country": country,
            "search_lang": search_lang,
            "count": count,
            **kwargs
        }
        if freshness:
            params["freshness"] = freshness

        return self._make_request("news/search", params)

    def llm_context(
        self,
        query: str,
        country: str = "US",
        search_lang: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """
        LLM 接地 / RAG

        返回预提取的网页内容，用于 RAG/Agent 系统。

        Args:
            query: 搜索查询
            country: 搜索国家
            search_lang: 语言偏好

        Returns:
            接地内容
        """
        params = {
            "q": query,
            "country": country,
            "search_lang": search_lang,
            **kwargs
        }
        return self._make_request("websearch/llm-context", params)

    def suggest(
        self,
        query: str,
        country: str = "US",
        search_lang: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """
        查询建议 / 自动补全

        Args:
            query: 搜索查询
            country: 搜索国家
            search_lang: 语言偏好

        Returns:
            补全建议
        """
        params = {
            "q": query,
            "country": country,
            "search_lang": search_lang,
            **kwargs
        }
        return self._make_request("suggest", params)


# 便捷函数
def get_client(api_key: Optional[str] = None) -> BraveSearchClient:
    """
    获取 Brave Search 客户端实例

    Args:
        api_key: API Key，可选

    Returns:
        BraveSearchClient 实例
    """
    return BraveSearchClient(api_key=api_key)


def search(query: str, api_key: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    快速搜索

    Args:
        query: 搜索查询
        api_key: API Key，可选
        **kwargs: 其他参数

    Returns:
        搜索结果
    """
    client = get_client(api_key)
    return client.web_search(query, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Brave Search API 客户端")
    parser.add_argument("--api-key", help="API Key")
    parser.add_argument("--query", "-q", required=True, help="搜索查询")
    parser.add_argument(
        "--type",
        choices=["web", "videos", "images", "news", "llm"],
        default="web",
        help="搜索类型"
    )

    args = parser.parse_args()

    try:
        client = BraveSearchClient(api_key=args.api_key)

        if args.type == "web":
            result = client.web_search(args.query)
        elif args.type == "videos":
            result = client.videos_search(args.query)
        elif args.type == "images":
            result = client.images_search(args.query)
        elif args.type == "news":
            result = client.news_search(args.query)
        elif args.type == "llm":
            result = client.llm_context(args.query)

        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

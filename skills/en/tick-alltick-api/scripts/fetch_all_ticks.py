#!/usr/bin/env python3
"""
Alltick 批量行情获取脚本

按顺序获取指定股票的多种 K 线数据，每次调用间隔 10 秒。

使用示例:
    python fetch_all_ticks.py --code 700.HK
    python fetch_all_ticks.py --code 700.HK --output-dir ~/stock_data
    python fetch_all_ticks.py --code 700.HK --interval 15 --types 1min,daily
"""

# 抑制 macOS LibreSSL 兼容性警告
import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from alltick_client import AlltickClient, KlineType, APIError


def main():
    parser = argparse.ArgumentParser(description="Alltick 批量行情获取")
    parser.add_argument("--code", "-c", required=True, help="股票代码")
    parser.add_argument("--output-dir", "-o", help="输出目录")
    parser.add_argument("--interval", "-i", type=float, default=10.0, help="调用间隔秒数")
    parser.add_argument("--types", "-t", default="1min,5day,daily", help="K线类型: 1min,5min,5day,15min,30min,hour,daily,week,month")
    parser.add_argument("--dump-file", help="合并输出到单个文件")
    args = parser.parse_args()

    # K线类型映射
    type_map = {
        "1min": (KlineType.MINUTE_1, 240),
        "5min": (KlineType.MINUTE_5, 48),
        "5day": (KlineType.DAY, 5),       # 5 日 K 线
        "15min": (KlineType.MINUTE_15, 16),
        "30min": (KlineType.MINUTE_30, 8),
        "hour": (KlineType.HOUR_1, 24),
        "daily": (KlineType.DAY, 60),
        "week": (KlineType.WEEK, 26),
        "month": (KlineType.MONTH, 12),
    }

    # 解析要获取的类型
    types = [(t.strip().lower(), *type_map[t.strip().lower()])
             for t in args.types.split(",") if t.strip().lower() in type_map]

    if not types:
        print("错误: 无效的 K 线类型")
        sys.exit(1)

    client = AlltickClient()
    results = {}
    output_dir = os.path.expanduser(args.output_dir) if args.output_dir else None

    print(f"股票: {args.code} | 类型: {', '.join(t[0] for t in types)} | 间隔: {args.interval}s")
    print("-" * 50)

    for i, (name, kline_type, count) in enumerate(types):
        if i > 0:
            print(f"等待 {args.interval}s...")
            time.sleep(args.interval)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 获取 {name}...", end=" ")

        try:
            data = client.get_kline(args.code, kline_type=kline_type, query_kline_num=count)
            kline_count = len(data.get("data", {}).get("kline_list", []))
            print(f"✓ {kline_count} 根")
            results[name] = data

            # 保存单个文件
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M")
                path = os.path.join(output_dir, f"tick_{name}_{ts}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"✗ {e}")
            results[name] = {"error": str(e)}

    # 合并输出
    if args.dump_file:
        path = os.path.expanduser(args.dump_file)
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n已保存: {path}")

    # 输出 JSON
    print("\n" + json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

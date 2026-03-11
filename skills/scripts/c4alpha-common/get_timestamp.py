#!/usr/bin/env python3
"""
获取当前系统时间戳，支持多种格式。

用法:
    python3 get_timestamp.py [格式]

格式:
    default / 无参数  - yyMMddHHmm (例: 2603112155)
    iso               - ISO 8601 格式 (例: 2026-03-11T21:55:00)
    date              - 仅日期 (例: 2026-03-11)
    datetime          - 日期和时间 (例: 2026-03-11 21:55:00)
    filename          - 与 default 相同，用于报告文件名
"""

import sys
from datetime import datetime


def get_timestamp(format_type: str = "default") -> str:
    """获取指定格式的当前时间戳。"""
    now = datetime.now()

    formats = {
        "default": now.strftime("%y%m%d%H%M"),
        "filename": now.strftime("%y%m%d%H%M"),
        "iso": now.isoformat(timespec="seconds"),
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return formats.get(format_type, formats["default"])


def main():
    format_type = sys.argv[1] if len(sys.argv) > 1 else "default"
    print(get_timestamp(format_type))


if __name__ == "__main__":
    main()

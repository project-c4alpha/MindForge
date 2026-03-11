#!/usr/bin/env python3
"""
Get current system timestamp in various formats.

Usage:
    python3 get_timestamp.py [format]

Formats:
    default / no arg  - yyMMddHHmm (e.g., 2603112155)
    iso               - ISO 8601 format (e.g., 2026-03-11T21:55:00)
    date              - Date only (e.g., 2026-03-11)
    datetime          - Date and time (e.g., 2026-03-11 21:55:00)
    filename          - Same as default, for report filenames
"""

import sys
from datetime import datetime


def get_timestamp(format_type: str = "default") -> str:
    """Get current timestamp in specified format."""
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

#!/usr/bin/env python3
"""
Get storage configuration from ~/.c4alpha/config.toml.

Usage:
    python3 get_storage_config.py [options]

Options:
    --format json    Output as JSON (default)
    --format shell   Output as shell variables (STORAGE_MODE=..., STORAGE_PATH=...)

Default values (if config not found):
    mode: local
    path: ~/.c4alpha/report
"""

import json
import os
import sys
from pathlib import Path


def get_config_path() -> Path:
    """Get the path to config.toml."""
    return Path.home() / ".c4alpha" / "config.toml"


def parse_toml_simple(content: str) -> dict:
    """
    Simple TOML parser for basic key-value pairs.
    Only handles simple cases like:
    [storage]
    mode = "local"
    path = "~/.c4alpha/report"
    """
    result = {}
    current_section = None

    for line in content.split('\n'):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Section header
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            result[current_section] = {}
            continue

        # Key-value pair
        if '=' in line and current_section:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes from string values
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            result[current_section][key] = value

    return result


def get_storage_config() -> dict:
    """Get storage configuration from config.toml."""
    default_config = {
        "mode": "local",
        "path": "~/.c4alpha/report"
    }

    config_path = get_config_path()

    if not config_path.exists():
        return default_config

    try:
        content = config_path.read_text()
        config = parse_toml_simple(content)

        if "storage" in config:
            storage = config["storage"]
            return {
                "mode": storage.get("mode", default_config["mode"]),
                "path": storage.get("path", default_config["path"])
            }
    except Exception:
        pass

    return default_config


def format_output(config: dict, output_format: str) -> str:
    """Format the config output."""
    if output_format == "shell":
        return f"STORAGE_MODE={config['mode']}\nSTORAGE_PATH={config['path']}"
    else:
        return json.dumps(config)


def main():
    output_format = "json"

    # Parse arguments
    args = sys.argv[1:]
    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            output_format = args[idx + 1]

    config = get_storage_config()
    print(format_output(config, output_format))


if __name__ == "__main__":
    main()

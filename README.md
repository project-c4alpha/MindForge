# MindForge - AI Toolkit for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[中文文档](docs/README-zhcn.md) | English

MindForge is a lightweight, focused AI Toolkit for Claude Code, providing specialized skills for web search and financial market data.

## Features

- **Multi-language Support**: English and Simplified Chinese (zh-cn)
- **Easy Setup**: One-command installation script
- **Centralized Config**: API keys managed in `~/.c4alpha/config.toml`

## Quick Start

```bash
# Use default language (English)
./setup-claude.sh

# Use Chinese
./setup-claude.sh --lang=zh-cn

# Use English (explicit)
./setup-claude.sh --lang=en
```

After setup:
1. Edit `~/.c4alpha/config.toml` to add your API keys
2. Claude Code will automatically discover these skills

## Available Skills

### search-brave
Comprehensive Brave Search API skill supporting:
- Web, video, image, and news search
- AI grounding (RAG) with `llm-context`
- AI answer generation with `answers`
- Local POI queries and query suggestions

### tick-alltick-api
Alltick-exclusive real-time market data API for:
- K-line/candlestick data
- Latest trade prices
- Order book depth
- Stock, forex, and cryptocurrency data

### stock-trading-analysis
Stock trading analysis skill for:
- K-line chart analysis
- Profit/loss calculations based on holding cost
- Multi-market strategies (A-share, US stock, crypto)
- Structured investment reports

## Configuration

Copy the example config and add your API keys:

```bash
cp config.toml.example ~/.c4alpha/config.toml
```

Edit `~/.c4alpha/config.toml`:

```toml
# Brave Search API
[[search.providers]]
name = "brave"
api-key = "your-brave-search-api-key"

# Alltick Market Data API
[[tick.providers]]
name = "alltick"
api-key = "your-alltick-api-key"
```

## Project Structure

```
mindforge/
├── skills/                 # Skills (multi-language)
│   ├── en/                # English versions
│   │   ├── search-brave/
│   │   ├── tick-alltick-api/
│   │   └── stock-trading-analysis/
│   ├── zh-cn/             # Chinese versions
│   │   ├── search-brave/
│   │   ├── tick-alltick-api/
│   │   └── stock-trading-analysis/
│   └── scripts/           # Shared scripts
├── commands/              # Slash commands
│   ├── en/
│   └── zh-cn/
├── templates/             # Templates for new resources
├── user_claude_md/        # User-level Claude instructions
├── config.toml.example    # Configuration template
└── setup-claude.sh        # Setup script
```

## Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `zh-cn` | Simplified Chinese |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

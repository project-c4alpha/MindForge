---
name: c4a.analyze
description: Comprehensive stock analysis workflow. Input a stock symbol to automatically search news and fetch market data (intraday, 5-day, daily K-line) in parallel, generating a complete investment analysis report. Trigger this skill when user enters /c4a.analyze or requests comprehensive stock analysis.
argument-hint: [Stock symbol, e.g. 700.HK / AAPL.US / 600519.SH]
---

# Comprehensive Stock Analysis Workflow

This is an automated stock analysis workflow that collects data through parallel subagent calls and generates structured investment analysis reports.

## Dependencies

- **c4alpha-common**: Provides timestamp generation and common utilities
- **search-brave**: For news search
- **tick-alltick-api**: For market data

## Workflow

When user calls `/c4a.analyze [stock symbol]`, execute the following steps:

### Step 0: Get Timestamp and Read Storage Configuration (Main Agent)

**Main agent** is responsible for preparing all parameters and checking storage mode:

```bash
# Get timestamp from c4alpha-common (short format: YYMMDDHHMM)
timestamp=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py filename)

# Get storage configuration from c4alpha-common
storageConfig=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py)

# Parse stock symbol
symbol="[stock symbol]"  # e.g., AAPL.US
stockName="${symbol%%.*}"  # Extract stock name: AAPL
```

The `storageConfig` output is a JSON object with the following structure:
```json
{
  "mode": "local",  // or "none"
  "path": "~/.c4alpha/report"
}
```

### Step 1: Conditional Directory Creation (Main Agent)

Based on the storage configuration, conditionally create the report directory:

```bash
# Check storage mode
storageMode=$(echo "$storageConfig" | python3 -c "import sys, json; print(json.load(sys.stdin)['mode'])")

if [ "$storageMode" = "local" ]; then
  # Get storage path from config
  storagePath=$(echo "$storageConfig" | python3 -c "import sys, json; print(json.load(sys.stdin)['path'])")
  # Expand ~ to home directory
  storagePath="${storagePath/#\~/$HOME}"

  # Create report directory
  dumpDir="${storagePath}/${stockName}/${timestamp}"
  mkdir -p "${dumpDir}"
  # Example: ~/.c4alpha/report/AAPL/2603112214/
else
  # No persistence mode - data will not be saved to disk
  dumpDir=""
fi
```

Identify the symbol format and market type:

| Symbol Format | Market | Example |
|---------------|--------|---------|
| `{number}.HK` | Hong Kong | 700.HK (Tencent), 9988.HK (Alibaba) |
| `{code}.US` | US Market | AAPL.US (Apple), GOOGL.US (Google) |
| `{number}.SH` | A-Share Shanghai | 600519.SH (Kweichow Moutai) |
| `{number}.SZ` | A-Share Shenzhen | 000001.SZ (Ping An Bank) |

### Step 2: Parallel Data Collection (Subagents)

Launch two subagents in parallel using the Agent tool. The parameters passed depend on storage mode:

**When storage mode = "local"**:
- `dumpDir`: Report directory path (e.g., ~/.c4alpha/report/AAPL/2603112214/)
- `symbol`: Stock symbol (e.g., AAPL.US)
- `stockName`: Stock name (e.g., AAPL)
- Subagents will save data to JSON files in the dumpDir

**When storage mode = "none"**:
- `dumpDir`: Empty string (no file persistence)
- `symbol`: Stock symbol (e.g., AAPL.US)
- `stockName`: Stock name (e.g., AAPL)
- Subagents will return data directly without saving to files

**IMPORTANT**: Subagents must NOT create .py files in report directory. All Python scripts should be in skill directories.

**Data Storage Format Requirements**:
- All data files must be pure JSON format (.json files)
- DO NOT wrap JSON data in markdown code blocks
- File naming convention: Use English names only

**Subagent A - News Search**:
```
subagent_type: general-purpose
prompt: |
  You are a professional financial news researcher.

  Parameters passed from main agent:
  - dumpDir: {dumpDir}
  - symbol: {symbol}
  - stockName: {stockName}

  Task: Search for latest news related to stock {symbol}

  IMPORTANT RULES:
  - DO NOT create any .py files in the report directory
  - Use existing skill scripts only
  - Save results as pure JSON files (NOT markdown with JSON)

  Steps:
  1. Navigate to search-brave skill directory: ~/.claude/skills/search-brave/scripts/
  2. If dumpDir is provided (storage mode = "local"):
     python3 brave_search_client.py news-search "{symbol}" --dump-file "{dumpDir}/news_{stockName}.json"
     The script will save news data to the specified JSON file.
  3. If dumpDir is empty (storage mode = "none"):
     python3 brave_search_client.py news-search "{symbol}"
     Return the news data directly without saving to file.

  Output: News data (file path if dumpDir provided, or direct JSON output)
```

**Subagent B - Market Data Fetching**:
```
subagent_type: general-purpose
prompt: |
  You are a professional market data analyst.

  Parameters passed from main agent:
  - dumpDir: {dumpDir}
  - symbol: {symbol}
  - stockName: {stockName}

  Task: Fetch market data for stock {symbol}

  IMPORTANT RULES:
  - DO NOT create any .py files in the report directory
  - Use tick-alltick-api skill scripts from ~/.claude/skills/tick-alltick-api/scripts/
  - Save results as pure JSON files (NOT markdown with JSON)

  Steps:
  1. Navigate to tick-alltick-api skill directory: ~/.claude/skills/tick-alltick-api/scripts/
  2. If dumpDir is provided (storage mode = "local"):
     python3 fetch_all_ticks.py --code {symbol} --output-dir "{dumpDir}" --types 1min
     The script will save K-line data to the dumpDir directory (file name format: tick_1min_{timestamp}.json).
  3. If dumpDir is empty (storage mode = "none"):
     python3 fetch_all_ticks.py --code {symbol} --types 1min
     Return the K-line data directly without saving to file.

  Output: K-line data (file path if dumpDir provided, or direct JSON output)
```

### Step 3: Data Summary and Analysis

After both subagents complete:

**When storage mode = "local"**:
1. Read news data from `{dumpDir}/news_{stockName}.json`
2. Read market data from `{dumpDir}/tick_1min_{stockName}.json`
3. Apply the `stock-trading-analysis` skill's analysis framework
4. Generate a complete investment analysis report

**When storage mode = "none"**:
1. Collect news data directly from subagent output
2. Collect market data directly from subagent output
3. Apply the `stock-trading-analysis` skill's analysis framework
4. Generate a complete investment analysis report (output to user only, no file saved)

### Step 4: Output Report

**When storage mode = "local"**:

Generate report file in the same directory:

**File name format**: `{dumpDir}/report.md`

**Example**: `~/.c4alpha/report/AAPL/2603112214/report.md`

```bash
report_file="${dumpDir}/report.md"
# Example: ~/.c4alpha/report/AAPL/2603112214/report.md
```

**When storage mode = "none"**:

Output the report directly to the user without saving to file. The analysis results are returned in the conversation output only.

## Directory Structure

**When storage mode = "local"**, after the workflow completes, the directory structure will be:

```
~/.c4alpha/report/
└── AAPL/                       # Stock name (without exchange suffix)
    └── 2603112214/             # Timestamp (YYMMDDHHMM)
        ├── report.md           # Final analysis report
        ├── news_AAPL.json      # News data (pure JSON)
        └── tick_1min_AAPL.json # 1-minute K-line data (pure JSON)
```

**When storage mode = "none"**, no files are created. Analysis results are returned directly to the user.

## Report Template

The report should follow the format in [Output Template](references/output-template.md), including:

1. **Basic Info** - Symbol, name, market, current price
2. **Market Overview** - Intraday movement, 5-day trend, daily K analysis
3. **Technical Analysis** - Key levels, indicators, pattern recognition
4. **News Analysis** - Recent important news and impact assessment
5. **Investment Recommendations** - Action suggestions, target prices, stop-loss levels
6. **Risk Warning** - Main risk points

## Cleanup

**Only applies when storage mode = "local"**:

Check for and remove any accidentally created .py files in the report directory:

```bash
rm ~/.c4alpha/report/**/*.py 2>/dev/null
```

## Usage Example

**With storage mode = "local"**:
```
User: /c4a.analyze AAPL.US

Claude: Analyzing Apple (AAPL.US)...

[Main agent prepares parameters]
- symbol: AAPL.US
- stockName: AAPL
- storageMode: local
- dumpDir: ~/.c4alpha/report/AAPL/2603112214/

[Launching subagents in parallel...]

Report generated: ~/.c4alpha/report/AAPL/2603112214/report.md
Data files:
  - news_AAPL.json
  - tick_1min_AAPL.json
```

**With storage mode = "none"**:
```
User: /c4a.analyze AAPL.US

Claude: Analyzing Apple (AAPL.US)...

[Main agent prepares parameters]
- symbol: AAPL.US
- stockName: AAPL
- storageMode: none
- dumpDir: (not created)

[Launching subagents in parallel...]

Report generated (output to user):
[Analysis report content displayed directly in conversation]
```

## Notes

1. **API Configuration**: Ensure `~/.c4alpha/config.toml` is configured with:
   - Brave Search API Key (for news search)
   - Alltick API Token (for market data)

2. **Storage Configuration**: The `[storage]` section in `~/.c4alpha/config.toml` controls data persistence:
   - `mode = "local"`: Reports and data are saved to local filesystem
   - `mode = "none"`: No files are created, analysis results are returned directly

3. **Network Requirements**: Stable internet connection required for external API access

4. **Rate Limits**: Alltick API has rate limits, do not exceed quota

5. **Data Timeliness**: Market data is real-time, news data is from the past 7 days

6. **No Python in Output Directory**: Never create .py files in ~/.c4alpha/, use skill scripts only

7. **Pure JSON Format**: All data files are stored as pure JSON (.json), not wrapped in markdown

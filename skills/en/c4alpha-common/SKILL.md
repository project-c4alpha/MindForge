---
name: c4alpha-common
description: Common utilities for C4Alpha skills. Provides timestamp generation, file naming, and other shared functions. Other skills should reference this skill for common operations.
---

# C4Alpha Common Utilities

This skill provides common utility functions shared across C4Alpha skills.

## Available Scripts

### get_timestamp.py

Get current system timestamp in various formats.

**Usage**:
```bash
python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py [format]
```

**Formats**:
| Format | Description | Example |
|--------|-------------|---------|
| `default` or no arg | yyMMddHHmm | 2603112155 |
| `iso` | ISO 8601 format | 2026-03-11T21:55:00 |
| `date` | Date only | 2026-03-11 |
| `datetime` | Date and time | 2026-03-11 21:55:00 |
| `filename` | For report filenames | 2603112155 |

**Example**:
```bash
# Get timestamp for report filename
timestamp=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py filename)
echo "Report: 700.HK_${timestamp}.md"
# Output: Report: 700.HK_2603112155.md
```

### get_storage_config.py

Get storage configuration from `~/.c4alpha/config.toml`.

**Usage**:
```bash
python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py [--format json|shell]
```

**Options**:
| Option | Description |
|--------|-------------|
| `--format json` | Output as JSON (default) |
| `--format shell` | Output as shell variables |

**Default values** (if config not found):
- mode: `local`
- path: `~/.c4alpha/report`

**Examples**:
```bash
# Get config as JSON (default)
python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py
# Output: {"mode": "local", "path": "~/.c4alpha/report"}

# Get config as shell variables for sourcing
python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py --format shell
# Output:
# STORAGE_MODE=local
# STORAGE_PATH=~/.c4alpha/report

# Use in shell script
eval $(python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py --format shell)
echo "Storage mode: $STORAGE_MODE"
echo "Storage path: $STORAGE_PATH"
```

## Integration Guide

When creating reports or output files, use this pattern:

```bash
# 1. Get timestamp
timestamp=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py filename)

# 2. Generate filename (no prefix, just symbol_timestamp.md)
filename="${symbol}_${timestamp}.md"
# Example: 700.HK_2603112155.md

# 3. Full path
output_path="$HOME/.c4alpha/${filename}"
```

## Important Notes

1. **No temporary files in ~/.c4alpha/**: Subagents should NOT create .py files in ~/.c4alpha/. Use the scripts in this skill instead.

2. **File naming convention**:
   - Use symbol directly (no prefix like "股票_" or "stock_")
   - Format: `{symbol}_{timestamp}.md`
   - Example: `700.HK_2603112155.md`

3. **Cleanup**: Always clean up temporary .md files after generating final report.

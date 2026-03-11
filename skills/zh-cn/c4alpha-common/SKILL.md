---
name: c4alpha-common
description: C4Alpha 技能通用工具。提供时间戳生成、文件命名等共享功能。其他技能应引用此技能获取通用功能。
---

# C4Alpha 通用工具

此技能提供 C4Alpha 各技能共享的通用工具函数。

## 可用脚本

### get_timestamp.py

获取当前系统时间戳，支持多种格式。

**用法**:
```bash
python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py [格式]
```

**格式说明**:
| 格式 | 描述 | 示例 |
|------|------|------|
| `default` 或无参数 | yyMMddHHmm | 2603112155 |
| `iso` | ISO 8601 格式 | 2026-03-11T21:55:00 |
| `date` | 仅日期 | 2026-03-11 |
| `datetime` | 日期和时间 | 2026-03-11 21:55:00 |
| `filename` | 用于报告文件名 | 2603112155 |

**示例**:
```bash
# 获取用于报告文件名的时间戳
timestamp=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py filename)
echo "报告: 700.HK_${timestamp}.md"
# 输出: 报告: 700.HK_2603112155.md
```

### get_storage_config.py

从 `~/.c4alpha/config.toml` 获取存储配置。

**用法**:
```bash
python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py [--format json|shell]
```

**选项**:
| 选项 | 描述 |
|------|------|
| `--format json` | 输出为 JSON 格式（默认） |
| `--format shell` | 输出为 Shell 变量格式 |

**默认值**（配置不存在时）：
- mode: `local`
- path: `~/.c4alpha/report`

**示例**:
```bash
# 获取 JSON 格式配置（默认）
python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py
# 输出: {"mode": "local", "path": "~/.c4alpha/report"}

# 获取 Shell 变量格式，用于 source
python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py --format shell
# 输出:
# STORAGE_MODE=local
# STORAGE_PATH=~/.c4alpha/report

# 在 shell 脚本中使用
eval $(python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py --format shell)
echo "存储模式: $STORAGE_MODE"
echo "存储路径: $STORAGE_PATH"
```

## 集成指南

创建报告或输出文件时，使用以下模式：

```bash
# 1. 获取时间戳
timestamp=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py filename)

# 2. 生成文件名（无前缀，直接用代码_时间戳.md）
filename="${symbol}_${timestamp}.md"
# 示例: 700.HK_2603112155.md

# 3. 完整路径
output_path="$HOME/.c4alpha/${filename}"
```

## 重要注意事项

1. **禁止在 ~/.c4alpha/ 目录下创建临时 .py 文件**：Subagent 不应在 ~/.c4alpha/ 目录下创建 .py 文件，应使用本技能提供的脚本。

2. **文件命名规范**：
   - 直接使用股票代码（不加"股票_"或"stock_"前缀）
   - 格式：`{代码}_{时间戳}.md`
   - 示例：`700.HK_2603112155.md`

3. **清理工作**：生成最终报告后，务必清理临时 .md 文件。

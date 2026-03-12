---
name: c4a.analyze
description: 股票综合分析工作流。输入股票代码后，自动并行搜索新闻和获取行情数据（分时、五日、日K），生成完整的投资分析报告。当用户输入 /c4a.analyze 或请求股票综合分析时触发此技能。
argument-hint: [股票代码，如 700.HK / AAPL.US / 600519.SH]
---

# 股票综合分析工作流

这是一个自动化的股票分析工作流，通过并行调用 subagent 收集数据，生成结构化的投资分析报告。

## 依赖技能

- **c4alpha-common**: 提供时间戳生成和通用工具
- **search-brave**: 用于新闻搜索
- **tick-alltick-api**: 用于行情数据

## 工作流程

当用户调用 `/c4a.analyze [股票代码]` 时，执行以下步骤：

### 第零步：获取时间戳并读取存储配置（主 Agent）

**主 agent** 负责准备所有参数并检查存储模式：

```bash
# 从 c4alpha-common 获取时间戳（短格式：YYMMDDHHMM）
timestamp=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_timestamp.py filename)

# 从 c4alpha-common 获取存储配置
storageConfig=$(python3 ~/.claude/skills/c4alpha-common/scripts/get_storage_config.py)

# 解析股票代码
symbol="[股票代码]"  # 如：AAPL.US
stockName="${symbol%%.*}"  # 提取股票名称：AAPL
```

`storageConfig` 输出为 JSON 对象，结构如下：
```json
{
  "mode": "local",  // 或 "none"
  "path": "~/.c4alpha/report"
}
```

### 第一步：条件性创建目录（主 Agent）

根据存储配置决定是否创建报告目录：

```bash
# 检查存储模式
storageMode=$(echo "$storageConfig" | python3 -c "import sys, json; print(json.load(sys.stdin)['mode'])")

if [ "$storageMode" = "local" ]; then
  # 从配置中获取存储路径
  storagePath=$(echo "$storageConfig" | python3 -c "import sys, json; print(json.load(sys.stdin)['path'])")
  # 展开 ~ 为家目录
  storagePath="${storagePath/#\~/$HOME}"

  # 创建报告目录
  dumpDir="${storagePath}/${stockName}/${timestamp}"
  mkdir -p "${dumpDir}"
  # 示例: ~/.c4alpha/report/AAPL/2603112214/
else
  # 无持久化模式 - 数据不会保存到磁盘
  dumpDir=""
fi
```

识别股票代码的格式并确定市场类型：

| 代码格式 | 市场 | 示例 |
|----------|------|------|
| `{数字}.HK` | 港股 | 700.HK (腾讯), 9988.HK (阿里巴巴) |
| `{代码}.US` | 美股 | AAPL.US (苹果), GOOGL.US (谷歌) |
| `{数字}.SH` | A股上海 | 600519.SH (贵州茅台) |
| `{数字}.SZ` | A股深圳 | 000001.SZ (平安银行) |

### 第二步：并行数据收集（Subagent）

使用 Agent 工具并行启动两个 subagent。传入的参数根据存储模式决定：

**当存储模式为 "local" 时**：
- `dumpDir`: 报告目录路径（如 ~/.c4alpha/report/AAPL/2603112214/）
- `symbol`: 股票代码（如 AAPL.US）
- `stockName`: 股票名称（如 AAPL）
- Subagent 将数据保存到 dumpDir 中的 JSON 文件

**当存储模式为 "none" 时**：
- `dumpDir`: 空字符串（无文件持久化）
- `symbol`: 股票代码（如 AAPL.US）
- `stockName`: 股票名称（如 AAPL）
- Subagent 直接返回数据，不保存到文件

**重要规则**：Subagent 禁止在报告目录下创建 .py 文件，所有 Python 脚本应在技能目录中。

**数据存储格式要求**：
- 所有数据文件必须为纯 JSON 格式（.json 文件）
- 不再使用 markdown 包裹 JSON 数据
- 文件命名统一使用英文名称

**Subagent A - 新闻搜索**：
```
subagent_type: general-purpose
prompt: |
  你是一个专业的财经新闻搜索员。

  主 agent 传入的参数：
  - dumpDir: {dumpDir}
  - symbol: {symbol}
  - stockName: {stockName}

  任务：搜索股票 {symbol} 的最新相关新闻

  重要规则：
  - 禁止在报告目录下创建任何 .py 文件
  - 只使用现有技能脚本
  - 结果保存为纯 JSON 文件（不是 markdown 包裹的 JSON）

  步骤：
  1. 进入 search-brave 技能目录：~/.claude/skills/search-brave/scripts/
  2. 如果 dumpDir 有值（存储模式 = "local"）：
     python3 brave_search_client.py news-search "{symbol}" --dump-file "{dumpDir}/news_{stockName}.json"
     脚本会将新闻数据保存到指定的 JSON 文件。
  3. 如果 dumpDir 为空（存储模式 = "none"）：
     python3 brave_search_client.py news-search "{symbol}"
     直接返回新闻数据，不保存到文件。

  输出：新闻数据（如果 dumpDir 有值则为文件路径，否则为直接 JSON 输出）
```

**Subagent B - 行情数据获取**：
```
subagent_type: general-purpose
prompt: |
  你是一个专业的行情数据分析师。

  主 agent 传入的参数：
  - dumpDir: {dumpDir}
  - symbol: {symbol}
  - stockName: {stockName}

  任务：获取股票 {symbol} 的行情数据

  重要规则：
  - 禁止在报告目录下创建任何 .py 文件
  - 使用 ~/.claude/skills/tick-alltick-api/scripts/ 中的脚本
  - 结果保存为纯 JSON 文件（不是 markdown 包裹的 JSON）

  步骤：
  1. 进入 tick-alltick-api 技能目录：~/.claude/skills/tick-alltick-api/scripts/
  2. 如果 dumpDir 有值（存储模式 = "local"）：
     python3 fetch_all_ticks.py --code {symbol} --output-dir "{dumpDir}" --types 1min
     脚本会将 K 线数据保存到 dumpDir 目录中（文件名格式：tick_1min_{timestamp}.json）。
  3. 如果 dumpDir 为空（存储模式 = "none"）：
     python3 fetch_all_ticks.py --code {symbol} --types 1min
     直接返回 K 线数据，不保存到文件。

  输出：K 线数据（如果 dumpDir 有值则为文件路径，否则为直接 JSON 输出）
```

### 第三步：数据汇总与分析

等待两个 subagent 完成后：

**当存储模式为 "local" 时**：
1. 从 `{dumpDir}/news_{stockName}.json` 读取新闻数据
2. 从 `{dumpDir}/tick_1min_{stockName}.json` 读取行情数据
3. 结合 `stock-trading-analysis` skill 的分析框架
4. 生成完整的投资分析报告

**当存储模式为 "none" 时**：
1. 从 subagent 输出直接收集新闻数据
2. 从 subagent 输出直接收集行情数据
3. 结合 `stock-trading-analysis` skill 的分析框架
4. 生成完整的投资分析报告（仅输出给用户，不保存文件）

### 第四步：输出报告

**当存储模式为 "local" 时**：

在同一目录下生成报告文件：

**文件名格式**：`{dumpDir}/report.md`

**示例**：`~/.c4alpha/report/AAPL/2603112214/report.md`

```bash
report_file="${dumpDir}/report.md"
# 示例: ~/.c4alpha/report/AAPL/2603112214/report.md
```

**当存储模式为 "none" 时**：

直接向用户输出报告，不保存到文件。分析结果仅在对话输出中返回。

## 目录结构

**当存储模式为 "local" 时**，工作流完成后，目录结构如下：

```
~/.c4alpha/report/
└── AAPL/                       # 股票名称（不含交易所后缀）
    └── 2603112214/             # 时间戳（YYMMDDHHMM）
        ├── report.md           # 最终分析报告
        ├── news_AAPL.json      # 新闻数据（纯 JSON）
        └── tick_1min_AAPL.json # 1分钟K线数据（纯 JSON）
```

**当存储模式为 "none" 时**，不创建任何文件。分析结果直接返回给用户。

## 报告模板

报告应遵循 [输出模板](references/output-template.md) 的格式，包含：

1. **基本信息** - 股票代码、名称、市场、当前价格
2. **行情概览** - 分时走势、五日趋势、日K分析
3. **技术分析** - 关键价位、技术指标、形态识别
4. **新闻分析** - 近期重要新闻及影响评估
5. **投资建议** - 操作建议、目标价位、止损位
6. **风险提示** - 主要风险点

## 清理

**仅适用于存储模式为 "local" 时**：

检查并删除报告目录中意外创建的 .py 文件：

```bash
rm ~/.c4alpha/report/**/*.py 2>/dev/null
```

## 使用示例

**存储模式为 "local" 时**：
```
用户: /c4a.analyze AAPL.US

Claude: 正在分析苹果(AAPL.US)...

[主 agent 准备参数]
- symbol: AAPL.US
- stockName: AAPL
- storageMode: local
- dumpDir: ~/.c4alpha/report/AAPL/2603112214/

[并行启动 subagent...]

生成分析报告: ~/.c4alpha/report/AAPL/2603112214/report.md
数据文件:
  - news_AAPL.json
  - tick_1min_AAPL.json
```

**存储模式为 "none" 时**：
```
用户: /c4a.analyze AAPL.US

Claude: 正在分析苹果(AAPL.US)...

[主 agent 准备参数]
- symbol: AAPL.US
- stockName: AAPL
- storageMode: none
- dumpDir: (不创建)

[并行启动 subagent...]

生成分析报告（输出给用户）:
[分析报告内容直接显示在对话中]
```

## 注意事项

1. **API 配置**：确保 `~/.c4alpha/config.toml` 中已配置：
   - Brave Search API Key（用于新闻搜索）
   - Alltick API Token（用于行情数据）

2. **存储配置**：`~/.c4alpha/config.toml` 中的 `[storage]` 部分控制数据持久化：
   - `mode = "local"`：报告和数据保存到本地文件系统
   - `mode = "none"`：不创建文件，分析结果直接返回

3. **网络要求**：需要稳定的网络连接访问外部 API

4. **请求频率**：Alltick API 有频率限制，注意不要超过配额

5. **数据时效**：行情数据为实时数据，新闻数据为过去7天

6. **禁止在输出目录创建 Python 文件**：永远不要在 ~/.c4alpha/ 创建 .py 文件，只使用技能脚本

7. **纯 JSON 格式**：所有数据文件存储为纯 JSON（.json），不使用 markdown 包裹

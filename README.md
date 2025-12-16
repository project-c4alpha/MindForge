# AITK - AI Toolkit for Claude Code

AITK 是一个内部的工具集合，用于管理 MCP 服务、AI Agents 和 Skills。

## 项目结构

```
aitk/
├── mcp/              # MCP 服务集合
│   ├── _template/    # MCP 服务模板
│   └── mcp-*/        # 具体的 MCP 服务
├── agents/           # Agent 集合
│   ├── _template/    # Agent 模板
│   └── */            # 具体的 Agent
├── skills/           # Skill 集合
│   ├── _template/    # Skill 模板
│   └── */            # 具体的 Skill
└── Makefile          # 主 Makefile
```

## 快速开始

### 查看资源

```sh
# 列出所有 MCP 服务
make list-mcp

# 列出所有 Agents
make list-agents

# 列出所有 Skills
make list-skills
```

### 创建资源

```sh
# 创建新的 MCP 服务
make init-mcp SERVICE=mcp-foo

# 创建新的 Agent
make init-agent AGENT=my-agent

# 创建新的 Skill
make init-skill SKILL=my-skill
```

### 为 Agent 添加 Skill

```sh
# 将 skill 添加到 agent
make add-skill AGENT=my-agent SKILL=my-skill
```

### 构建和测试

```sh
# 构建单个 MCP 服务
make build SERVICE=mcp-foo

# 构建单个 Agent
make build AGENT=my-agent

# 构建单个 Skill
make build SKILL=my-skill

# 构建所有资源
make build-all

# 测试所有资源
make test-all

# 清理所有资源
make clean-all
```

## 资源约定

每个 MCP 服务、Agent 或 Skill 都应该提供自己的 `Makefile`，至少包含以下目标：

- `build` - 构建
- `test` - 测试
- `clean` - 清理

可选目标：

- `fmt` - 格式化代码
- `lint` - 代码检查

每个资源可以使用自己的技术栈（Go/Node/Python/Rust/etc.）

## 技术栈

- MCP 服务：可以使用任何支持 MCP 协议的语言和框架
- Agents：AI 代理，用于执行特定任务
- Skills：可复用的能力模块，可以被 Agent 引用


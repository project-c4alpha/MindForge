# 获取 tickProvider Token

从 `~/.c4alpha/config.toml` 配置文件中读取 tickProvider 的 token。

## 用法

```
/get-tick-token
```

## 说明

此命令会读取 `~/.c4alpha/config.toml` 文件中的 `[tickProvider]` 部分的 `token` 字段。

## 配置文件格式

```toml
[tickProvider]
token = "your-alltick-api-token-here"
```

## 示例

```bash
# 查看当前配置的 token
/get-tick-token

# 输出示例
# Token: your-alltick-api-token-here
```

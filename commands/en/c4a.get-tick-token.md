# Get Tick Provider Token

Read the tickProvider token from `~/.c4alpha/config.toml` configuration file.

## Usage

```
/get-tick-token
```

## Description

This command reads the `token` field from the `[tickProvider]` section in `~/.c4alpha/config.toml`.

## Configuration File Format

```toml
[tickProvider]
token = "your-alltick-api-token-here"
```

## Example

```bash
# View the currently configured token
/get-tick-token

# Output example
# Token: your-alltick-api-token-here
```

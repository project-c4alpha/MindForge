# MCP Service Template

Rename this folder to your service name (recommended: `mcp-<name>`), then implement your own MCP server.

This workspace does not enforce any tech stack. Pick what you need (Go/Node/Python/Rust/etc.) and wire it into the `Makefile` targets.

## Targets expected by the workspace

- `make build` — produce the service artifact (binary/docker image/etc.)
- `make test` — run tests (or a no-op if you don’t have tests yet)
- `make clean` — remove generated outputs

Optional:

- `make fmt`
- `make lint`


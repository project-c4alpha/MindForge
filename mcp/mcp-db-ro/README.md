# mcp-db-ro

Read-only MCP server for inspecting multiple databases (PostgreSQL/MySQL).

## Build

```sh
make build
```

Cross compile (examples):

```sh
make build GOOS=linux GOARCH=amd64
make build GOOS=darwin GOARCH=arm64
make build-all
```

## Run

This server speaks MCP over stdio. Point your MCP client at the built binary.

Config is JSON (multiple connections supported). Provide it via `--db`.

```sh
./dist/mcp-db-ro --db ./config.example.json
```

### Config schema

- `connections[]`
  - `name`: unique connection name used in tool arguments
  - `driver`: `postgres` | `mysql`
  - `host`, `port`
  - `username`, `password`
  - `database` (optional): initial database to connect to (MySQL can be omitted to connect to server only; Postgres will use the driver default if omitted)
  - `defaultDatabase` (optional): used when a tool needs a database name (mainly MySQL table metadata tools)
  - `sslMode` (optional, postgres)
  - `tls` (optional, mysql)
  - `params` (optional): driver params as key/value strings

## Tools

All tools require `connection` (the configured connection name).

- `db.listConnections`
- `db.listDatabases`
- `db.listSchemas` (Postgres)
- `db.listTables`
- `db.describeTable`
- `db.listIndexes`
- `db.tablePartitions`
- `db.explain`
- `db.query` (read-only; blocks obvious write statements)
- `db.getDDL` (best effort; mysql uses SHOW CREATE TABLE; postgres reconstructs from catalogs)
- `db.useDatabase` (select default database for subsequent operations)

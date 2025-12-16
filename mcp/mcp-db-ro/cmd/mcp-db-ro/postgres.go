package main

import (
	"context"
	"database/sql"
	"fmt"
	"strings"
)

type postgresDriver struct{}

func (postgresDriver) Kind() DriverKind { return DriverPostgres }

func (postgresDriver) ListDatabases(ctx context.Context, db *sql.DB) ([]map[string]any, error) {
	return queryAll(ctx, db, `SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname`)
}

func (postgresDriver) ListSchemas(ctx context.Context, db *sql.DB) ([]map[string]any, error) {
	return queryAll(ctx, db, `SELECT schema_name FROM information_schema.schemata ORDER BY schema_name`)
}

func (postgresDriver) ListTables(ctx context.Context, db *sql.DB, scope TableScope) ([]map[string]any, error) {
	return queryAll(ctx, db, `
SELECT table_name
FROM information_schema.tables
WHERE table_schema = $1 AND table_type = 'BASE TABLE'
ORDER BY table_name`, scope.Schema)
}

func (postgresDriver) DescribeTable(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error) {
	return queryAll(ctx, db, `
SELECT
  ordinal_position,
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = $1 AND table_name = $2
ORDER BY ordinal_position`, ref.Schema, ref.Table)
}

func (postgresDriver) ListIndexes(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error) {
	return queryAll(ctx, db, `
SELECT
  i.relname AS index_name,
  ix.indisunique AS is_unique,
  ix.indisprimary AS is_primary,
  pg_get_indexdef(ix.indexrelid) AS index_def
FROM pg_class t
JOIN pg_namespace ns ON ns.oid = t.relnamespace
JOIN pg_index ix ON t.oid = ix.indrelid
JOIN pg_class i ON i.oid = ix.indexrelid
WHERE ns.nspname = $1 AND t.relname = $2
ORDER BY i.relname`, ref.Schema, ref.Table)
}

func (postgresDriver) TablePartitions(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error) {
	return queryAll(ctx, db, `
SELECT
  parent.relname AS parent_table,
  child.relname  AS partition_table,
  pg_get_expr(child.relpartbound, child.oid) AS partition_bound
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child  ON pg_inherits.inhrelid = child.oid
JOIN pg_namespace ns ON ns.oid = parent.relnamespace
WHERE ns.nspname = $1 AND parent.relname = $2
ORDER BY child.relname`, ref.Schema, ref.Table)
}

func (postgresDriver) Explain(ctx context.Context, db *sql.DB, query, format string) ([]map[string]any, error) {
	f := strings.ToLower(strings.TrimSpace(format))
	switch f {
	case "", "text":
		return queryAll(ctx, db, "EXPLAIN "+query)
	case "json":
		return queryAll(ctx, db, "EXPLAIN (FORMAT JSON) "+query)
	default:
		return nil, fmt.Errorf("unsupported format: %s (postgres supports: text, json)", format)
	}
}

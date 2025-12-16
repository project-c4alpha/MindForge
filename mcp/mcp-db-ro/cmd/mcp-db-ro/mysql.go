package main

import (
	"context"
	"database/sql"
	"strings"
)

type mysqlDriver struct{}

func (mysqlDriver) Kind() DriverKind { return DriverMySQL }

func (mysqlDriver) ListDatabases(ctx context.Context, db *sql.DB) ([]map[string]any, error) {
	return queryAll(ctx, db, `SHOW DATABASES`)
}

func (mysqlDriver) ListSchemas(ctx context.Context, db *sql.DB) ([]map[string]any, error) {
	return []map[string]any{}, nil
}

func (mysqlDriver) ListTables(ctx context.Context, db *sql.DB, scope TableScope) ([]map[string]any, error) {
	if strings.TrimSpace(scope.Database) == "" {
		return queryAll(ctx, db, `
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
ORDER BY table_schema, table_name
LIMIT 500`)
	}
	return queryAll(ctx, db, `
SELECT table_name
FROM information_schema.tables
WHERE table_schema = ? AND table_type = 'BASE TABLE'
ORDER BY table_name`, scope.Database)
}

func (mysqlDriver) DescribeTable(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error) {
	return queryAll(ctx, db, `
SELECT
  ordinal_position,
  column_name,
  column_type,
  is_nullable,
  column_default,
  column_key,
  extra
FROM information_schema.columns
WHERE table_schema = ? AND table_name = ?
ORDER BY ordinal_position`, ref.Database, ref.Table)
}

func (mysqlDriver) ListIndexes(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error) {
	return queryAll(ctx, db, `
SELECT
  index_name,
  non_unique,
  seq_in_index,
  column_name,
  collation,
  cardinality,
  sub_part,
  packed,
  nullable,
  index_type,
  comment,
  index_comment
FROM information_schema.statistics
WHERE table_schema = ? AND table_name = ?
ORDER BY index_name, seq_in_index`, ref.Database, ref.Table)
}

func (mysqlDriver) TablePartitions(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error) {
	return queryAll(ctx, db, `
SELECT
  partition_name,
  subpartition_name,
  partition_ordinal_position,
  subpartition_ordinal_position,
  partition_method,
  subpartition_method,
  partition_expression,
  subpartition_expression,
  partition_description,
  table_rows,
  data_length,
  index_length
FROM information_schema.partitions
WHERE table_schema = ? AND table_name = ?
ORDER BY partition_ordinal_position, subpartition_ordinal_position`, ref.Database, ref.Table)
}

func (mysqlDriver) Explain(ctx context.Context, db *sql.DB, query, _ string) ([]map[string]any, error) {
	return queryAll(ctx, db, "EXPLAIN "+query)
}

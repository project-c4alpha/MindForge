package main

import (
	"context"
	"database/sql"
	"strings"
	"time"
)

func isReadOnlySQL(q string) bool {
	s := strings.ToLower(strings.TrimSpace(q))
	if s == "" {
		return false
	}
	for strings.HasPrefix(s, "--") {
		nl := strings.Index(s, "\n")
		if nl == -1 {
			return false
		}
		s = strings.TrimSpace(s[nl+1:])
	}
	for strings.HasPrefix(s, "/*") {
		end := strings.Index(s, "*/")
		if end == -1 {
			return false
		}
		s = strings.TrimSpace(s[end+2:])
	}
	switch {
	case strings.HasPrefix(s, "select "):
		return true
	case strings.HasPrefix(s, "with "):
		return true
	case strings.HasPrefix(s, "show "):
		return true
	case strings.HasPrefix(s, "explain "):
		return true
	case s == "select" || s == "with" || s == "show" || s == "explain":
		return true
	default:
		return false
	}
}

func queryAll(ctx context.Context, db *sql.DB, query string, args ...any) ([]map[string]any, error) {
	return queryAllLimited(ctx, db, query, 0, args...)
}

func queryAllLimited(ctx context.Context, db *sql.DB, query string, limit int, args ...any) ([]map[string]any, error) {
	ctx, cancel := context.WithTimeout(ctx, 20*time.Second)
	defer cancel()

	rows, err := db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	cols, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	out := make([]map[string]any, 0)
	for rows.Next() {
		if limit > 0 && len(out) >= limit {
			break
		}
		values := make([]any, len(cols))
		ptrs := make([]any, len(cols))
		for i := range values {
			ptrs[i] = &values[i]
		}
		if err := rows.Scan(ptrs...); err != nil {
			return nil, err
		}
		m := make(map[string]any, len(cols))
		for i, c := range cols {
			m[c] = normalizeSQLValue(values[i])
		}
		out = append(out, m)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return out, nil
}

func normalizeSQLValue(v any) any {
	switch x := v.(type) {
	case nil:
		return nil
	case []byte:
		return string(x)
	default:
		return x
	}
}

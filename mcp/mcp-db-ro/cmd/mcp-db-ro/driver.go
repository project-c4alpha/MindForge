package main

import (
	"context"
	"database/sql"
	"fmt"
	"strings"
	"sync"
	"time"
)

type DriverKind string

const (
	DriverPostgres DriverKind = "postgres"
	DriverMySQL    DriverKind = "mysql"
)

type TableScope struct {
	Database string
	Schema   string
}

type TableRef struct {
	Database string
	Schema   string
	Table    string
}

type DDLResult struct {
	TableDDL   string   `json:"tableDDL"`
	IndexDDLs  []string `json:"indexDDLs,omitempty"`
	Notes      []string `json:"notes,omitempty"`
	DriverKind string   `json:"driverKind,omitempty"`
}

type DBDriver interface {
	Kind() DriverKind
	ListDatabases(ctx context.Context, db *sql.DB) ([]map[string]any, error)
	ListSchemas(ctx context.Context, db *sql.DB) ([]map[string]any, error)
	ListTables(ctx context.Context, db *sql.DB, scope TableScope) ([]map[string]any, error)
	DescribeTable(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error)
	ListIndexes(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error)
	TablePartitions(ctx context.Context, db *sql.DB, ref TableRef) ([]map[string]any, error)
	Explain(ctx context.Context, db *sql.DB, query string, format string) ([]map[string]any, error)
	GetDDL(ctx context.Context, db *sql.DB, ref TableRef, includeIndexes bool) (DDLResult, error)
}

type dbClient struct {
	cfg           ConnectionConfig
	db            *sql.DB
	driver        DBDriver
	sqlDriverName string

	mu           sync.RWMutex
	selectedDB   string
	dbByDatabase map[string]*sql.DB // postgres only

	// bootstrapPing indicates base db was validated on startup.
	bootstrapPing bool
}

func normalizeDriver(d string) (DriverKind, string, error) {
	switch strings.ToLower(strings.TrimSpace(d)) {
	case "postgres", "postgresql", "pg":
		return DriverPostgres, "pgx", nil
	case "mysql":
		return DriverMySQL, "mysql", nil
	default:
		return "", "", fmt.Errorf("unsupported driver: %s (supported: postgres, mysql)", d)
	}
}

func newDriver(kind DriverKind) (DBDriver, error) {
	switch kind {
	case DriverPostgres:
		return postgresDriver{}, nil
	case DriverMySQL:
		return mysqlDriver{}, nil
	default:
		return nil, fmt.Errorf("unsupported driver kind: %s", kind)
	}
}

func (c *dbClient) normalizeScope(scope TableScope) (TableScope, error) {
	switch c.driver.Kind() {
	case DriverPostgres:
		if strings.TrimSpace(scope.Schema) == "" {
			scope.Schema = "public"
		}
		if strings.TrimSpace(scope.Database) == "" {
			scope.Database = c.getSelectedDatabase()
		}
		if strings.TrimSpace(scope.Database) == "" {
			scope.Database = strings.TrimSpace(c.cfg.Database)
		}
		return scope, nil
	case DriverMySQL:
		if strings.TrimSpace(scope.Database) == "" {
			scope.Database = c.getSelectedDatabase()
		}
		if strings.TrimSpace(scope.Database) == "" {
			scope.Database = c.cfg.DefaultDatabase
		}
		if strings.TrimSpace(scope.Database) == "" {
			scope.Database = c.cfg.Database
		}
		return scope, nil
	default:
		return TableScope{}, fmt.Errorf("unsupported driver: %s", c.cfg.Driver)
	}
}

func (c *dbClient) normalizeRef(ref TableRef) (TableRef, error) {
	ref.Table = strings.TrimSpace(ref.Table)
	if ref.Table == "" {
		return TableRef{}, fmt.Errorf("table is required")
	}
	scope, err := c.normalizeScope(TableScope{Database: ref.Database, Schema: ref.Schema})
	if err != nil {
		return TableRef{}, err
	}
	ref.Database = scope.Database
	ref.Schema = scope.Schema
	return ref, nil
}

func (c *dbClient) requireDatabase(database string) (string, error) {
	database = strings.TrimSpace(database)
	if database == "" {
		database = c.getSelectedDatabase()
	}
	if database == "" {
		database = strings.TrimSpace(c.cfg.DefaultDatabase)
	}
	if database == "" {
		database = strings.TrimSpace(c.cfg.Database)
	}
	if database == "" {
		return "", fmt.Errorf("database is required for this operation (provide argument database or set database/defaultDatabase in config)")
	}
	return database, nil
}

func (c *dbClient) setSelectedDatabase(database string) {
	c.mu.Lock()
	c.selectedDB = strings.TrimSpace(database)
	c.mu.Unlock()
}

func (c *dbClient) getSelectedDatabase() string {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.selectedDB
}

func (c *dbClient) dbForDatabase(ctx context.Context, database string) (*sql.DB, error) {
	database = strings.TrimSpace(database)
	if database == "" {
		return c.db, nil
	}
	if c.driver.Kind() != DriverPostgres {
		// MySQL doesn't require a separate pool per DB.
		return c.db, nil
	}

	c.mu.RLock()
	if db, ok := c.dbByDatabase[database]; ok {
		c.mu.RUnlock()
		return db, nil
	}
	c.mu.RUnlock()

	cfgCopy := c.cfg
	cfgCopy.Database = database
	dsn, err := buildDSN(DriverPostgres, cfgCopy)
	if err != nil {
		return nil, err
	}

	db, err := sql.Open(c.sqlDriverName, dsn)
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(4)
	db.SetMaxIdleConns(4)
	db.SetConnMaxLifetime(30 * time.Minute)

	pingCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	err = db.PingContext(pingCtx)
	cancel()
	if err != nil {
		_ = db.Close()
		return nil, err
	}

	c.mu.Lock()
	// Re-check after open to avoid duplicate pools.
	if existing, ok := c.dbByDatabase[database]; ok {
		c.mu.Unlock()
		_ = db.Close()
		return existing, nil
	}
	c.dbByDatabase[database] = db
	c.mu.Unlock()
	return db, nil
}

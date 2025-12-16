package main

import (
	"context"
	"fmt"
	"strings"
)

func (s *dbService) listDatabases(conn string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	return c.driver.ListDatabases(context.Background(), c.db)
}

func (s *dbService) listSchemas(conn, database string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	scope, err := c.normalizeScope(TableScope{Database: database})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), scope.Database)
	if err != nil {
		return nil, err
	}
	return c.driver.ListSchemas(context.Background(), db)
}

func (s *dbService) listTables(conn, database, schema string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	scope, err := c.normalizeScope(TableScope{Database: database, Schema: schema})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), scope.Database)
	if err != nil {
		return nil, err
	}
	return c.driver.ListTables(context.Background(), db, scope)
}

func (s *dbService) describeTable(conn, database, schema, table string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	if c.driver.Kind() == DriverMySQL {
		dbName, err := c.requireDatabase(database)
		if err != nil {
			return nil, err
		}
		database = dbName
	}
	ref, err := c.normalizeRef(TableRef{Database: database, Schema: schema, Table: table})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), ref.Database)
	if err != nil {
		return nil, err
	}
	return c.driver.DescribeTable(context.Background(), db, ref)
}

func (s *dbService) listIndexes(conn, database, schema, table string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	if c.driver.Kind() == DriverMySQL {
		dbName, err := c.requireDatabase(database)
		if err != nil {
			return nil, err
		}
		database = dbName
	}
	ref, err := c.normalizeRef(TableRef{Database: database, Schema: schema, Table: table})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), ref.Database)
	if err != nil {
		return nil, err
	}
	return c.driver.ListIndexes(context.Background(), db, ref)
}

func (s *dbService) tablePartitions(conn, database, schema, table string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	if c.driver.Kind() == DriverMySQL {
		dbName, err := c.requireDatabase(database)
		if err != nil {
			return nil, err
		}
		database = dbName
	}
	ref, err := c.normalizeRef(TableRef{Database: database, Schema: schema, Table: table})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), ref.Database)
	if err != nil {
		return nil, err
	}
	return c.driver.TablePartitions(context.Background(), db, ref)
}

func (s *dbService) explain(conn, database, query, format string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	query = strings.TrimSpace(query)
	if query == "" {
		return nil, fmt.Errorf("query is required")
	}
	if !isReadOnlySQL(query) {
		return nil, fmt.Errorf("query blocked (only SELECT/WITH/SHOW/EXPLAIN allowed)")
	}
	scope, err := c.normalizeScope(TableScope{Database: database})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), scope.Database)
	if err != nil {
		return nil, err
	}
	return c.driver.Explain(context.Background(), db, query, format)
}

func (s *dbService) query(conn, database, query string, limit int) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	query = strings.TrimSpace(query)
	if query == "" {
		return nil, fmt.Errorf("query is required")
	}
	if !isReadOnlySQL(query) {
		return nil, fmt.Errorf("query blocked (only SELECT/WITH/SHOW/EXPLAIN allowed)")
	}
	if limit <= 0 {
		limit = 200
	}
	scope, err := c.normalizeScope(TableScope{Database: database})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), scope.Database)
	if err != nil {
		return nil, err
	}
	return queryAllLimited(context.Background(), db, query, limit)
}

func (s *dbService) getDDL(conn, database, schema, table string, includeIndexes bool) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	if c.driver.Kind() == DriverMySQL {
		dbName, err := c.requireDatabase(database)
		if err != nil {
			return nil, err
		}
		database = dbName
	}
	ref, err := c.normalizeRef(TableRef{Database: database, Schema: schema, Table: table})
	if err != nil {
		return nil, err
	}
	db, err := c.dbForDatabase(context.Background(), ref.Database)
	if err != nil {
		return nil, err
	}
	return c.driver.GetDDL(context.Background(), db, ref, includeIndexes)
}

func (s *dbService) useDatabase(conn, database string) (any, error) {
	c, err := s.getClient(conn)
	if err != nil {
		return nil, err
	}
	database = strings.TrimSpace(database)
	if database == "" {
		return nil, fmt.Errorf("database is required")
	}

	switch c.driver.Kind() {
	case DriverPostgres:
		// Validate by opening/pinging (cached).
		if _, err := c.dbForDatabase(context.Background(), database); err != nil {
			return nil, err
		}
		c.setSelectedDatabase(database)
	case DriverMySQL:
		// Best-effort validation: check visibility in information_schema.
		_, err := queryAll(context.Background(), c.db, `SELECT schema_name FROM information_schema.schemata WHERE schema_name = ? LIMIT 1`, database)
		if err != nil {
			// If permissions prevent access to information_schema, still allow selecting.
			c.setSelectedDatabase(database)
			return map[string]any{
				"selectedDatabase": database,
				"note":             "database selected; validation skipped due to error: " + err.Error(),
			}, nil
		}
		c.setSelectedDatabase(database)
	default:
		return nil, fmt.Errorf("unsupported driver: %s", c.cfg.Driver)
	}

	return map[string]any{
		"selectedDatabase": database,
	}, nil
}

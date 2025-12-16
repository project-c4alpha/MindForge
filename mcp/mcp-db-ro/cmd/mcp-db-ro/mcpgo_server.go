package main

import (
	"context"
	"encoding/json"

	"github.com/mark3labs/mcp-go/mcp"
	mcpserver "github.com/mark3labs/mcp-go/server"
)

func runMCP(db *dbService) error {
	s := mcpserver.NewMCPServer("mcp-db-ro", "0.1.0",
		mcpserver.WithToolCapabilities(false),
		mcpserver.WithRecovery(),
	)

	// Helper to wrap handlers
	wrap := func(fn func(mcp.CallToolRequest) (any, error)) func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		return func(_ context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
			out, err := fn(req)
			if err != nil {
				return mcp.NewToolResultError(err.Error()), nil
			}
			return toolJSON(out)
		}
	}

	s.AddTool(toolListConnections(), wrap(func(_ mcp.CallToolRequest) (any, error) {
		return db.listConnections(), nil
	}))

	s.AddTool(toolListDatabases(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		return db.listDatabases(conn)
	}))

	s.AddTool(toolListSchemas(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		return db.listSchemas(conn, req.GetString("database", ""))
	}))

	s.AddTool(toolListTables(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		return db.listTables(conn, req.GetString("database", ""), req.GetString("schema", ""))
	}))

	s.AddTool(toolDescribeTable(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		table, err := req.RequireString("table")
		if err != nil {
			return nil, err
		}
		return db.describeTable(conn, req.GetString("database", ""), req.GetString("schema", ""), table)
	}))

	s.AddTool(toolListIndexes(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		table, err := req.RequireString("table")
		if err != nil {
			return nil, err
		}
		return db.listIndexes(conn, req.GetString("database", ""), req.GetString("schema", ""), table)
	}))

	s.AddTool(toolTablePartitions(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		table, err := req.RequireString("table")
		if err != nil {
			return nil, err
		}
		return db.tablePartitions(conn, req.GetString("database", ""), req.GetString("schema", ""), table)
	}))

	s.AddTool(toolExplain(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		query, err := req.RequireString("query")
		if err != nil {
			return nil, err
		}
		return db.explain(conn, req.GetString("database", ""), query, req.GetString("format", ""))
	}))

	s.AddTool(toolQuery(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		query, err := req.RequireString("query")
		if err != nil {
			return nil, err
		}
		return db.query(conn, req.GetString("database", ""), query, req.GetInt("limit", 200))
	}))

	s.AddTool(toolGetDDL(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		table, err := req.RequireString("table")
		if err != nil {
			return nil, err
		}
		return db.getDDL(conn, req.GetString("database", ""), req.GetString("schema", ""), table, req.GetBool("includeIndexes", false))
	}))

	s.AddTool(toolUseDatabase(), wrap(func(req mcp.CallToolRequest) (any, error) {
		conn, err := req.RequireString("connection")
		if err != nil {
			return nil, err
		}
		database, err := req.RequireString("database")
		if err != nil {
			return nil, err
		}
		return db.useDatabase(conn, database)
	}))

	return mcpserver.ServeStdio(s)
}

func toolJSON(v any) (*mcp.CallToolResult, error) {
	pretty, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return mcp.NewToolResultError(err.Error()), nil
	}
	// MCP protocol requires structured content to be an object, not an array
	// Wrap any slice/array types in an object
	structured := v
	switch v.(type) {
	case []string, []map[string]any, []any:
		structured = map[string]any{"data": v}
	}
	return mcp.NewToolResultStructured(structured, string(pretty)), nil
}

func toolListConnections() mcp.Tool {
	return mcp.NewTool("db.listConnections",
		mcp.WithDescription("List configured connection names."),
	)
}

func toolListDatabases() mcp.Tool {
	return mcp.NewTool("db.listDatabases",
		mcp.WithDescription("List databases."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
	)
}

func toolListSchemas() mcp.Tool {
	return mcp.NewTool("db.listSchemas",
		mcp.WithDescription("List schemas (Postgres returns schemas; MySQL returns empty)."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name (Postgres). If omitted uses selected/default database.")),
	)
}

func toolListTables() mcp.Tool {
	return mcp.NewTool("db.listTables",
		mcp.WithDescription("List tables."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name (MySQL/Postgres). If omitted uses selected/default; MySQL can also list across all DBs (limited) if none selected.")),
		mcp.WithString("schema", mcp.Description("Schema name (Postgres, default public)")),
	)
}

func toolDescribeTable() mcp.Tool {
	return mcp.NewTool("db.describeTable",
		mcp.WithDescription("Describe table columns."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name (MySQL required unless selected/default is set; Postgres uses selected/default if omitted).")),
		mcp.WithString("schema", mcp.Description("Schema name (Postgres, default public)")),
		mcp.WithString("table", mcp.Required(), mcp.Description("Table name")),
	)
}

func toolListIndexes() mcp.Tool {
	return mcp.NewTool("db.listIndexes",
		mcp.WithDescription("List indexes of a table."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name (MySQL required unless selected/default is set; Postgres uses selected/default if omitted).")),
		mcp.WithString("schema", mcp.Description("Schema name (Postgres, default public)")),
		mcp.WithString("table", mcp.Required(), mcp.Description("Table name")),
	)
}

func toolTablePartitions() mcp.Tool {
	return mcp.NewTool("db.tablePartitions",
		mcp.WithDescription("Inspect physical partitions (best effort)."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name (MySQL required unless selected/default is set; Postgres uses selected/default if omitted).")),
		mcp.WithString("schema", mcp.Description("Schema name (Postgres, default public)")),
		mcp.WithString("table", mcp.Required(), mcp.Description("Table name")),
	)
}

func toolExplain() mcp.Tool {
	return mcp.NewTool("db.explain",
		mcp.WithDescription("Explain a query (DB-native EXPLAIN)."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name. MySQL: can specify any accessible database; Postgres: uses selected/default if omitted.")),
		mcp.WithString("query", mcp.Required(), mcp.Description("Query to explain")),
		mcp.WithString("format", mcp.Description("Postgres: text|json; MySQL ignores")),
	)
}

func toolQuery() mcp.Tool {
	return mcp.NewTool("db.query",
		mcp.WithDescription("Run a read-only query (SELECT/WITH/SHOW/EXPLAIN)."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name. MySQL: can specify any accessible database; Postgres: uses selected/default if omitted. If not specified and no default configured, MySQL will fail.")),
		mcp.WithString("query", mcp.Required(), mcp.Description("Query to execute")),
		mcp.WithNumber("limit", mcp.Description("Row limit applied client-side (default 200)")),
	)
}

func toolGetDDL() mcp.Tool {
	return mcp.NewTool("db.getDDL",
		mcp.WithDescription("Get table DDL (best effort)."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Description("Database name (MySQL required unless selected/default is set; Postgres uses selected/default if omitted).")),
		mcp.WithString("schema", mcp.Description("Schema name (Postgres, default public)")),
		mcp.WithString("table", mcp.Required(), mcp.Description("Table name")),
		mcp.WithBoolean("includeIndexes", mcp.Description("Postgres only; include non-primary index DDLs"), mcp.DefaultBool(false)),
	)
}

func toolUseDatabase() mcp.Tool {
	return mcp.NewTool("db.useDatabase",
		mcp.WithDescription("Select a default database for subsequent operations on this connection (MySQL: like USE; Postgres: switches the underlying connection pool)."),
		mcp.WithString("connection", mcp.Required(), mcp.Description("Configured connection name")),
		mcp.WithString("database", mcp.Required(), mcp.Description("Database name to select")),
	)
}

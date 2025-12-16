package main

import (
	"context"
	"database/sql"
	"fmt"
	"regexp"
	"strings"
)

var mysqlIdentRe = regexp.MustCompile(`^[A-Za-z0-9_]+$`)

func (mysqlDriver) GetDDL(ctx context.Context, db *sql.DB, ref TableRef, _ bool) (DDLResult, error) {
	// MySQL returns indexes/constraints inside SHOW CREATE TABLE.
	// Identifiers cannot be parameters in prepared statements; validate strictly.
	if !mysqlIdentRe.MatchString(ref.Database) || !mysqlIdentRe.MatchString(ref.Table) {
		return DDLResult{}, fmt.Errorf("invalid mysql identifier (allowed: [A-Za-z0-9_])")
	}
	qualified := fmt.Sprintf("`%s`.`%s`", ref.Database, ref.Table)

	rows, err := db.QueryContext(ctx, "SHOW CREATE TABLE "+qualified)
	if err != nil {
		return DDLResult{}, err
	}
	defer rows.Close()

	cols, err := rows.Columns()
	if err != nil {
		return DDLResult{}, err
	}
	if len(cols) < 2 {
		return DDLResult{}, fmt.Errorf("unexpected SHOW CREATE TABLE result shape")
	}

	// The second column is the CREATE statement across MySQL variants.
	for rows.Next() {
		var tableName string
		var createSQL string
		if err := rows.Scan(&tableName, &createSQL); err != nil {
			return DDLResult{}, err
		}
		createSQL = strings.TrimSpace(createSQL)
		if !strings.HasSuffix(createSQL, ";") {
			createSQL += ";"
		}
		return DDLResult{
			TableDDL:   createSQL + "\n",
			DriverKind: string(DriverMySQL),
		}, nil
	}
	if err := rows.Err(); err != nil {
		return DDLResult{}, err
	}
	return DDLResult{}, fmt.Errorf("table not found: %s", qualified)
}

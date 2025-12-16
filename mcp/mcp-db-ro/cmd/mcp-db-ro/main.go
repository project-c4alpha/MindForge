package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	_ "github.com/go-sql-driver/mysql"
	_ "github.com/jackc/pgx/v5/stdlib"
)

func main() {
	var dbConfigPath string
	flag.StringVar(&dbConfigPath, "db", "", "Path to DB JSON config file")
	flag.Parse()

	if dbConfigPath == "" {
		fmt.Fprintln(os.Stderr, "config required: --db <path-to-json>")
		os.Exit(2)
	}

	cfg, err := readConfig(dbConfigPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "failed to read config:", err)
		os.Exit(2)
	}

	logger := log.New(os.Stderr, "mcp-db-ro: ", log.LstdFlags|log.Lmicroseconds)
	s, err := newDBService(logger, cfg)
	if err != nil {
		fmt.Fprintln(os.Stderr, "failed to init server:", err)
		os.Exit(2)
	}
	defer s.close()

	if err := runMCP(s); err != nil {
		fmt.Fprintln(os.Stderr, "server error:", err)
		os.Exit(1)
	}
}

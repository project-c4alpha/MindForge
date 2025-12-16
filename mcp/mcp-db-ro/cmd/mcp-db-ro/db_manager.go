package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"sort"
	"strings"
	"sync"
	"time"
)

type dbService struct {
	logger      *log.Logger
	connections map[string]*dbClient
}

func newDBService(logger *log.Logger, cfg Config) (*dbService, error) {
	connections := make(map[string]*dbClient, len(cfg.Connections))
	for _, c := range cfg.Connections {
		if strings.TrimSpace(c.Name) == "" {
			return nil, fmt.Errorf("connection name required")
		}
		if _, ok := connections[c.Name]; ok {
			return nil, fmt.Errorf("duplicate connection name: %s", c.Name)
		}
		kind, sqlDriverName, err := normalizeDriver(c.Driver)
		if err != nil {
			return nil, fmt.Errorf("connection %s: %w", c.Name, err)
		}
		driver, err := newDriver(kind)
		if err != nil {
			return nil, fmt.Errorf("connection %s: %w", c.Name, err)
		}
		c.Driver = string(kind)

		dsn, err := buildDSN(kind, c)
		if err != nil {
			return nil, fmt.Errorf("connection %s: %w", c.Name, err)
		}

		db, err := sql.Open(sqlDriverName, dsn)
		if err != nil {
			return nil, fmt.Errorf("connection %s: open: %w", c.Name, err)
		}
		db.SetMaxOpenConns(4)
		db.SetMaxIdleConns(4)
		db.SetConnMaxLifetime(30 * time.Minute)

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		err = db.PingContext(ctx)
		cancel()
		if err != nil {
			_ = db.Close()
			return nil, fmt.Errorf("connection %s: ping: %w", c.Name, err)
		}

		connections[c.Name] = &dbClient{
			cfg:           c,
			db:            db,
			driver:        driver,
			sqlDriverName: sqlDriverName,
			mu:            sync.RWMutex{},
			dbByDatabase:  map[string]*sql.DB{},
			selectedDB:    "",
			bootstrapPing: true,
		}
	}

	return &dbService{
		logger:      logger,
		connections: connections,
	}, nil
}

func (s *dbService) close() {
	for _, c := range s.connections {
		_ = c.db.Close()
		c.mu.Lock()
		for _, db := range c.dbByDatabase {
			_ = db.Close()
		}
		c.dbByDatabase = map[string]*sql.DB{}
		c.mu.Unlock()
	}
}

func (s *dbService) getClient(name string) (*dbClient, error) {
	name = strings.TrimSpace(name)
	if name == "" {
		return nil, fmt.Errorf("connection is required")
	}
	c, ok := s.connections[name]
	if !ok {
		return nil, fmt.Errorf("unknown connection: %s", name)
	}
	return c, nil
}

func (s *dbService) listConnections() []string {
	out := make([]string, 0, len(s.connections))
	for k := range s.connections {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

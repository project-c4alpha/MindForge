package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Config struct {
	Connections []ConnectionConfig `json:"connections"`
}

type ConnectionConfig struct {
	Name     string `json:"name"`
	Driver   string `json:"driver"` // postgres|mysql
	Host     string `json:"host"`
	Port     int    `json:"port,omitempty"`
	Username string `json:"username"`
	Password string `json:"password"`
	Database string `json:"database,omitempty"`

	// Used when a tool needs a database name (mainly MySQL metadata queries).
	DefaultDatabase string `json:"defaultDatabase,omitempty"`

	// Driver-specific options.
	SSLMode string            `json:"sslMode,omitempty"` // postgres
	TLS     string            `json:"tls,omitempty"`     // mysql (go-sql-driver/mysql TLSConfig name)
	Params  map[string]string `json:"params,omitempty"`  // query/conn params
}

func readConfig(path string) (Config, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return Config{}, err
	}
	return parseConfigJSON(b)
}

func parseConfigJSON(b []byte) (Config, error) {
	var cfg Config
	if err := json.Unmarshal(b, &cfg); err != nil {
		return Config{}, err
	}
	if len(cfg.Connections) == 0 {
		return Config{}, fmt.Errorf("no connections configured")
	}
	return cfg, nil
}

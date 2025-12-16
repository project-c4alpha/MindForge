package main

import (
	"fmt"
	"sort"
	"strconv"
	"strings"

	mysqlcfg "github.com/go-sql-driver/mysql"
)

func buildDSN(kind DriverKind, cfg ConnectionConfig) (string, error) {
	host := strings.TrimSpace(cfg.Host)
	if host == "" {
		return "", fmt.Errorf("host is required")
	}
	username := strings.TrimSpace(cfg.Username)
	if username == "" {
		return "", fmt.Errorf("username is required")
	}
	port := cfg.Port

	switch kind {
	case DriverPostgres:
		if port == 0 {
			port = 5432
		}
		parts := []string{
			"host=" + pgConnValue(host),
			"port=" + pgConnValue(strconv.Itoa(port)),
			"user=" + pgConnValue(username),
			"password=" + pgConnValue(cfg.Password),
		}
		if strings.TrimSpace(cfg.Database) != "" {
			parts = append(parts, "dbname="+pgConnValue(cfg.Database))
		}
		if strings.TrimSpace(cfg.SSLMode) != "" {
			parts = append(parts, "sslmode="+pgConnValue(cfg.SSLMode))
		}
		for _, kv := range sortedKV(cfg.Params) {
			parts = append(parts, kv[0]+"="+pgConnValue(kv[1]))
		}
		return strings.Join(parts, " "), nil

	case DriverMySQL:
		if port == 0 {
			port = 3306
		}
		c := mysqlcfg.NewConfig()
		c.User = username
		c.Passwd = cfg.Password
		c.Net = "tcp"
		c.Addr = fmt.Sprintf("%s:%d", host, port)
		// DBName is optional in MySQL DSN; omitting it allows connecting to the server
		// and inspecting multiple databases (subject to privileges).
		c.DBName = strings.TrimSpace(cfg.Database)
		c.ParseTime = true
		if strings.TrimSpace(cfg.TLS) != "" {
			c.TLSConfig = strings.TrimSpace(cfg.TLS)
		}
		if len(cfg.Params) > 0 {
			if c.Params == nil {
				c.Params = map[string]string{}
			}
			for k, v := range cfg.Params {
				c.Params[k] = v
			}
		}
		return c.FormatDSN(), nil

	default:
		return "", fmt.Errorf("unsupported driver kind: %s", kind)
	}
}

func pgConnValue(v string) string {
	// pgx keyword/connstring supports single-quoted values with backslash escaping.
	// Quote if it contains whitespace, backslash, or single-quote.
	if v == "" {
		return "''"
	}
	if strings.ContainsAny(v, " \t\r\n'\\") {
		v = strings.ReplaceAll(v, `\`, `\\`)
		v = strings.ReplaceAll(v, `'`, `\'`)
		return "'" + v + "'"
	}
	return v
}

func sortedKV(m map[string]string) [][2]string {
	if len(m) == 0 {
		return nil
	}
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	out := make([][2]string, 0, len(keys))
	for _, k := range keys {
		out = append(out, [2]string{k, m[k]})
	}
	return out
}

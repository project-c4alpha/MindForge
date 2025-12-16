.DEFAULT_GOAL := help
.PHONY: help build build-all test clean fmt lint

BIN_NAME := mcp-db-ro
DIST_DIR := dist
PKG := ./cmd/$(BIN_NAME)

export GOCACHE := $(CURDIR)/.cache/go-build

# Default cross-compilation targets for CI/release.
# Override via: make build-all CROSS_TARGETS="linux/amd64 windows/amd64"
CROSS_TARGETS ?= linux/amd64 linux/arm64 windows/amd64 windows/arm64

help:
	@echo "$(BIN_NAME)"
	@echo ""
	@echo "Targets:"
	@echo "  make build [GOOS=.. GOARCH=..]"
	@echo "  make build-all"
	@echo "  make test"
	@echo "  make clean"
	@echo "  make fmt"
	@echo "  make lint"

build:
	@mkdir -p "$(DIST_DIR)"
	@CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o "$(DIST_DIR)/$(BIN_NAME)" "$(PKG)"

build-all:
	@set -e; \
	for target in $(CROSS_TARGETS); do \
		GOOS=$${target%/*}; GOARCH=$${target#*/}; \
		out="$(DIST_DIR)/$${GOOS}_$${GOARCH}"; \
		mkdir -p "$$out"; \
		echo "==> build $$GOOS/$$GOARCH"; \
		ext=""; [ "$$GOOS" = "windows" ] && ext=".exe"; \
		CGO_ENABLED=0 GOOS=$$GOOS GOARCH=$$GOARCH go build -trimpath -ldflags="-s -w" -o "$$out/$(BIN_NAME)$$ext" "$(PKG)"; \
	done

test:
	@go test ./...

clean:
	@rm -rf "$(DIST_DIR)"
	@rm -rf .cache

fmt:
	@gofmt -w .

lint:
	@echo "No linter configured (optional)."

.PHONY: build test clean coverage help

help:
	@echo "Java Unit Test Agent - Make targets"
	@echo ""
	@echo "  make build      - Build example tests"
	@echo "  make test       - Run example tests"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make clean      - Clean build artifacts"

build:
	@echo "Building Java Unit Test Agent examples..."
	@if [ -f build.gradle ]; then \
		./gradlew build -x test || gradle build -x test; \
	else \
		echo "No build.gradle found, skipping build"; \
	fi

test:
	@echo "Running example tests..."
	@if [ -f build.gradle ]; then \
		./gradlew test || gradle test; \
	else \
		echo "No build.gradle found, skipping tests"; \
	fi

coverage:
	@echo "Running tests with coverage..."
	@if [ -f build.gradle ]; then \
		./gradlew testCoverage || gradle testCoverage; \
		echo "Coverage report: build/reports/jacoco/test/html/index.html"; \
	else \
		echo "No build.gradle found, skipping coverage"; \
	fi

clean:
	@echo "Cleaning build artifacts..."
	@if [ -f build.gradle ]; then \
		./gradlew clean || gradle clean; \
	fi
	@rm -rf build/
	@echo "Clean complete"

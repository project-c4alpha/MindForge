.DEFAULT_GOAL := help
.PHONY: help list-mcp list-agents list-skills init-mcp init-agent init-skill add-skill build test clean fmt lint build-all test-all clean-all

# Directory definitions
MCP_DIR := mcp
AGENTS_DIR := agents
SKILLS_DIR := skills

MCP_TEMPLATE_DIR := $(MCP_DIR)/_template
AGENT_TEMPLATE_DIR := $(AGENTS_DIR)/_template
SKILL_TEMPLATE_DIR := $(SKILLS_DIR)/_template

# Discover items (excluding _template directories)
MCP_SERVICES := $(filter-out _template,$(notdir $(patsubst %/,%,$(wildcard $(MCP_DIR)/*/))))
AGENTS := $(filter-out _template,$(notdir $(patsubst %/,%,$(wildcard $(AGENTS_DIR)/*/))))
SKILLS := $(filter-out _template,$(notdir $(patsubst %/,%,$(wildcard $(SKILLS_DIR)/*/))))

# Helper to require and validate MCP service
define require_mcp
	@if [ -z "$(SERVICE)" ]; then \
		echo "ERROR: SERVICE is required. Example: make $(1) SERVICE=mcp-foo"; \
		exit 2; \
	fi
	@if [ ! -d "$(MCP_DIR)/$(SERVICE)" ]; then \
		echo "ERROR: MCP service '$(SERVICE)' not found under $(MCP_DIR)/"; \
		echo "Run: make list-mcp"; \
		exit 2; \
	fi
	@if [ ! -f "$(MCP_DIR)/$(SERVICE)/Makefile" ]; then \
		echo "ERROR: $(MCP_DIR)/$(SERVICE)/Makefile not found."; \
		exit 2; \
	fi
endef

# Helper to require and validate agent
define require_agent
	@if [ -z "$(AGENT)" ]; then \
		echo "ERROR: AGENT is required. Example: make $(1) AGENT=my-agent"; \
		exit 2; \
	fi
	@if [ ! -d "$(AGENTS_DIR)/$(AGENT)" ]; then \
		echo "ERROR: Agent '$(AGENT)' not found under $(AGENTS_DIR)/"; \
		echo "Run: make list-agents"; \
		exit 2; \
	fi
	@if [ ! -f "$(AGENTS_DIR)/$(AGENT)/Makefile" ]; then \
		echo "ERROR: $(AGENTS_DIR)/$(AGENT)/Makefile not found."; \
		exit 2; \
	fi
endef

# Helper to require and validate skill
define require_skill
	@if [ -z "$(SKILL)" ]; then \
		echo "ERROR: SKILL is required. Example: make $(1) SKILL=my-skill"; \
		exit 2; \
	fi
	@if [ ! -d "$(SKILLS_DIR)/$(SKILL)" ]; then \
		echo "ERROR: Skill '$(SKILL)' not found under $(SKILLS_DIR)/"; \
		echo "Run: make list-skills"; \
		exit 2; \
	fi
	@if [ ! -f "$(SKILLS_DIR)/$(SKILL)/Makefile" ]; then \
		echo "ERROR: $(SKILLS_DIR)/$(SKILL)/Makefile not found."; \
		exit 2; \
	fi
endef

help:
	@echo "AITK - AI Toolkit for Claude Code"
	@echo "=================================="
	@echo ""
	@echo "List Resources:"
	@echo "  make list-mcp                   List available MCP services"
	@echo "  make list-agents                List available agents"
	@echo "  make list-skills                List available skills"
	@echo ""
	@echo "Initialize New Resources:"
	@echo "  make init-mcp SERVICE=<name>    Create a new MCP service"
	@echo "  make init-agent AGENT=<name>    Create a new agent"
	@echo "  make init-skill SKILL=<name>    Create a new skill"
	@echo ""
	@echo "Add Skill to Agent:"
	@echo "  make add-skill AGENT=<name> SKILL=<name>  Add a skill to an agent"
	@echo ""
	@echo "Build/Test/Clean (per resource):"
	@echo "  make build SERVICE=<name>       Build MCP service"
	@echo "  make build AGENT=<name>         Build agent"
	@echo "  make build SKILL=<name>         Build skill"
	@echo "  make test SERVICE/AGENT/SKILL=<name>"
	@echo "  make clean SERVICE/AGENT/SKILL=<name>"
	@echo "  make fmt SERVICE/AGENT/SKILL=<name>"
	@echo "  make lint SERVICE/AGENT/SKILL=<name>"
	@echo ""
	@echo "Build/Test/Clean All:"
	@echo "  make build-all"
	@echo "  make test-all"
	@echo "  make clean-all"

# List commands
list-mcp:
	@echo "MCP Services:"
	@echo "$(MCP_SERVICES)" | tr ' ' '\n' | sed '/^$$/d' | sed 's/^/  /'

list-agents:
	@echo "Agents:"
	@echo "$(AGENTS)" | tr ' ' '\n' | sed '/^$$/d' | sed 's/^/  /'

list-skills:
	@echo "Skills:"
	@echo "$(SKILLS)" | tr ' ' '\n' | sed '/^$$/d' | sed 's/^/  /'

# Init commands
init-mcp:
	@if [ -z "$(SERVICE)" ]; then \
		echo "ERROR: SERVICE is required. Example: make init-mcp SERVICE=mcp-foo"; \
		exit 2; \
	fi
	@if [ -d "$(MCP_DIR)/$(SERVICE)" ]; then \
		echo "ERROR: MCP service already exists: $(MCP_DIR)/$(SERVICE)"; \
		exit 2; \
	fi
	@if [ ! -d "$(MCP_TEMPLATE_DIR)" ]; then \
		echo "ERROR: Template directory not found: $(MCP_TEMPLATE_DIR)"; \
		exit 2; \
	fi
	@mkdir -p "$(MCP_DIR)"
	@cp -R "$(MCP_TEMPLATE_DIR)" "$(MCP_DIR)/$(SERVICE)"
	@echo "✓ Created MCP service: $(MCP_DIR)/$(SERVICE)"
	@echo "Next: edit $(MCP_DIR)/$(SERVICE)/README.md and $(MCP_DIR)/$(SERVICE)/Makefile"

init-agent:
	@if [ -z "$(AGENT)" ]; then \
		echo "ERROR: AGENT is required. Example: make init-agent AGENT=my-agent"; \
		exit 2; \
	fi
	@if [ -d "$(AGENTS_DIR)/$(AGENT)" ]; then \
		echo "ERROR: Agent already exists: $(AGENTS_DIR)/$(AGENT)"; \
		exit 2; \
	fi
	@if [ ! -d "$(AGENT_TEMPLATE_DIR)" ]; then \
		echo "ERROR: Template directory not found: $(AGENT_TEMPLATE_DIR)"; \
		exit 2; \
	fi
	@mkdir -p "$(AGENTS_DIR)"
	@cp -R "$(AGENT_TEMPLATE_DIR)" "$(AGENTS_DIR)/$(AGENT)"
	@mkdir -p "$(AGENTS_DIR)/$(AGENT)/skills"
	@echo "✓ Created agent: $(AGENTS_DIR)/$(AGENT)"
	@echo "Next: edit $(AGENTS_DIR)/$(AGENT)/README.md"

init-skill:
	@if [ -z "$(SKILL)" ]; then \
		echo "ERROR: SKILL is required. Example: make init-skill SKILL=my-skill"; \
		exit 2; \
	fi
	@if [ -d "$(SKILLS_DIR)/$(SKILL)" ]; then \
		echo "ERROR: Skill already exists: $(SKILLS_DIR)/$(SKILL)"; \
		exit 2; \
	fi
	@if [ ! -d "$(SKILL_TEMPLATE_DIR)" ]; then \
		echo "ERROR: Template directory not found: $(SKILL_TEMPLATE_DIR)"; \
		exit 2; \
	fi
	@mkdir -p "$(SKILLS_DIR)"
	@cp -R "$(SKILL_TEMPLATE_DIR)" "$(SKILLS_DIR)/$(SKILL)"
	@echo "✓ Created skill: $(SKILLS_DIR)/$(SKILL)"
	@echo "Next: edit $(SKILLS_DIR)/$(SKILL)/README.md"

# Add skill to agent
add-skill:
	@if [ -z "$(AGENT)" ]; then \
		echo "ERROR: AGENT is required. Example: make add-skill AGENT=my-agent SKILL=my-skill"; \
		exit 2; \
	fi
	@if [ -z "$(SKILL)" ]; then \
		echo "ERROR: SKILL is required. Example: make add-skill AGENT=my-agent SKILL=my-skill"; \
		exit 2; \
	fi
	@if [ ! -d "$(AGENTS_DIR)/$(AGENT)" ]; then \
		echo "ERROR: Agent '$(AGENT)' not found. Run: make list-agents"; \
		exit 2; \
	fi
	@if [ ! -d "$(SKILLS_DIR)/$(SKILL)" ]; then \
		echo "ERROR: Skill '$(SKILL)' not found. Run: make list-skills"; \
		exit 2; \
	fi
	@mkdir -p "$(AGENTS_DIR)/$(AGENT)/skills"
	@if [ -L "$(AGENTS_DIR)/$(AGENT)/skills/$(SKILL)" ] || [ -d "$(AGENTS_DIR)/$(AGENT)/skills/$(SKILL)" ]; then \
		echo "✓ Skill '$(SKILL)' already added to agent '$(AGENT)'"; \
	else \
		ln -s "../../../$(SKILLS_DIR)/$(SKILL)" "$(AGENTS_DIR)/$(AGENT)/skills/$(SKILL)"; \
		echo "✓ Added skill '$(SKILL)' to agent '$(AGENT)'"; \
	fi

# Build/test/clean commands - auto-detect type
build:
	@if [ -n "$(SERVICE)" ]; then \
		$(call require_mcp,build); \
		$(MAKE) -C "$(MCP_DIR)/$(SERVICE)" build; \
	elif [ -n "$(AGENT)" ]; then \
		$(call require_agent,build); \
		$(MAKE) -C "$(AGENTS_DIR)/$(AGENT)" build; \
	elif [ -n "$(SKILL)" ]; then \
		$(call require_skill,build); \
		$(MAKE) -C "$(SKILLS_DIR)/$(SKILL)" build; \
	else \
		echo "ERROR: Specify SERVICE, AGENT, or SKILL"; \
		exit 2; \
	fi

test:
	@if [ -n "$(SERVICE)" ]; then \
		$(call require_mcp,test); \
		$(MAKE) -C "$(MCP_DIR)/$(SERVICE)" test; \
	elif [ -n "$(AGENT)" ]; then \
		$(call require_agent,test); \
		$(MAKE) -C "$(AGENTS_DIR)/$(AGENT)" test; \
	elif [ -n "$(SKILL)" ]; then \
		$(call require_skill,test); \
		$(MAKE) -C "$(SKILLS_DIR)/$(SKILL)" test; \
	else \
		echo "ERROR: Specify SERVICE, AGENT, or SKILL"; \
		exit 2; \
	fi

clean:
	@if [ -n "$(SERVICE)" ]; then \
		$(call require_mcp,clean); \
		$(MAKE) -C "$(MCP_DIR)/$(SERVICE)" clean; \
	elif [ -n "$(AGENT)" ]; then \
		$(call require_agent,clean); \
		$(MAKE) -C "$(AGENTS_DIR)/$(AGENT)" clean; \
	elif [ -n "$(SKILL)" ]; then \
		$(call require_skill,clean); \
		$(MAKE) -C "$(SKILLS_DIR)/$(SKILL)" clean; \
	else \
		echo "ERROR: Specify SERVICE, AGENT, or SKILL"; \
		exit 2; \
	fi

fmt:
	@if [ -n "$(SERVICE)" ]; then \
		$(call require_mcp,fmt); \
		$(MAKE) -C "$(MCP_DIR)/$(SERVICE)" fmt; \
	elif [ -n "$(AGENT)" ]; then \
		$(call require_agent,fmt); \
		$(MAKE) -C "$(AGENTS_DIR)/$(AGENT)" fmt; \
	elif [ -n "$(SKILL)" ]; then \
		$(call require_skill,fmt); \
		$(MAKE) -C "$(SKILLS_DIR)/$(SKILL)" fmt; \
	else \
		echo "ERROR: Specify SERVICE, AGENT, or SKILL"; \
		exit 2; \
	fi

lint:
	@if [ -n "$(SERVICE)" ]; then \
		$(call require_mcp,lint); \
		$(MAKE) -C "$(MCP_DIR)/$(SERVICE)" lint; \
	elif [ -n "$(AGENT)" ]; then \
		$(call require_agent,lint); \
		$(MAKE) -C "$(AGENTS_DIR)/$(AGENT)" lint; \
	elif [ -n "$(SKILL)" ]; then \
		$(call require_skill,lint); \
		$(MAKE) -C "$(SKILLS_DIR)/$(SKILL)" lint; \
	else \
		echo "ERROR: Specify SERVICE, AGENT, or SKILL"; \
		exit 2; \
	fi

# Build/test/clean all
build-all:
	@echo "==> Building all MCP services..."
	@set -e; \
	for s in $(MCP_SERVICES); do \
		echo "  → $$s"; \
		$(MAKE) -C "$(MCP_DIR)/$$s" build; \
	done
	@echo "==> Building all agents..."
	@set -e; \
	for a in $(AGENTS); do \
		echo "  → $$a"; \
		$(MAKE) -C "$(AGENTS_DIR)/$$a" build; \
	done
	@echo "==> Building all skills..."
	@set -e; \
	for sk in $(SKILLS); do \
		echo "  → $$sk"; \
		$(MAKE) -C "$(SKILLS_DIR)/$$sk" build; \
	done

test-all:
	@echo "==> Testing all MCP services..."
	@set -e; \
	for s in $(MCP_SERVICES); do \
		echo "  → $$s"; \
		$(MAKE) -C "$(MCP_DIR)/$$s" test; \
	done
	@echo "==> Testing all agents..."
	@set -e; \
	for a in $(AGENTS); do \
		echo "  → $$a"; \
		$(MAKE) -C "$(AGENTS_DIR)/$$a" test; \
	done
	@echo "==> Testing all skills..."
	@set -e; \
	for sk in $(SKILLS); do \
		echo "  → $$sk"; \
		$(MAKE) -C "$(SKILLS_DIR)/$$sk" test; \
	done

clean-all:
	@echo "==> Cleaning all MCP services..."
	@set -e; \
	for s in $(MCP_SERVICES); do \
		echo "  → $$s"; \
		$(MAKE) -C "$(MCP_DIR)/$$s" clean; \
	done
	@echo "==> Cleaning all agents..."
	@set -e; \
	for a in $(AGENTS); do \
		echo "  → $$a"; \
		$(MAKE) -C "$(AGENTS_DIR)/$$a" clean; \
	done
	@echo "==> Cleaning all skills..."
	@set -e; \
	for sk in $(SKILLS); do \
		echo "  → $$sk"; \
		$(MAKE) -C "$(SKILLS_DIR)/$$sk" clean; \
	done

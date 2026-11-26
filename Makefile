.DEFAULT_GOAL := help
PYTHON ?= python
RUFF ?= ruff
PYTEST ?= pytest

.PHONY: help install lint test docs docs-strict check run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

install: ## Install the package and the dev tools
	$(PYTHON) -m pip install -e ".[dev]"

lint: ## Lint the Python code
	$(RUFF) check .

test: ## Run the offline test suite
	$(PYTEST) -q

docs: ## Check page structure, links and code fences
	$(PYTHON) scripts/check_docs.py

docs-strict: ## Require every linked file to exist (run before a release)
	$(PYTHON) scripts/check_docs.py --strict

check: lint docs test ## Run everything CI runs

run: ## Start the hello-world example (needs BOT_TOKEN)
	$(PYTHON) examples/01_hello_polling.py

clean: ## Remove caches and coverage output
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

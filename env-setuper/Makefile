.ONESHELL:
SHELL := /bin/bash

.SILENT:

DEFAULT_GOAL := help
.PHONY: help
help:
	awk 'BEGIN {FS = ":.*?## "} /^[%a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Create poetry environment and install all dependencies.
	poetry config virtualenvs.in-project true --local
	poetry env use 3.12
	poetry install

.PHONY: checks
checks: style-check static-check ## Run all checks.

.PHONY: style-check
style-check: ## Run style checks.
	printf "Style Checking with Ruff\n"
	poetry run ruff check

.PHONY: static-check
static-check: ## Run strict typing checks.
	printf "Static Checking with Mypy\n"
	poetry run mypy .

.PHONY: restyle
restyle: ## Reformat code with ruff.
	poetry run ruff format .
	poetry run ruff check --fix .

.PHONY: requirements
requirements: ## Generate requirements.txt based on poetry env.
	poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev

.PHONY: tests
tests: ## Run tests.
	PYTHONPATH=. poetry run pytest -s

.PHONY: build
build: ## Build the current project to the installable whl
	poetry build --format wheel --clean --output dist

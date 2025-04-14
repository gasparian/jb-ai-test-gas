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

.PHONY: tests
tests: ## Run tests.
	PYTHONPATH=. poetry run pytest -s

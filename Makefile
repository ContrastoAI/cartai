.DEFAULT_GOAL := all

.PHONY: all
all: format lint

.PHONY: .uv
.uv: ## Check that uv is installed
	@uv --version || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: .pre-commit
.pre-commit: ## Check that pre-commit is installed
	@pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

.PHONY: format
format:
	uv sync --group lint
	uv run ruff format
	uv run ruff check --fix

.PHONY: lint
lint:
	uv sync --group lint
	uv run ruff format --check
#uv run ruff check
	uv run --all-groups mypy .

.PHONY: test
test:
	uv sync --group test
	uv run pytest

.PHONY: pre-commit
pre-commit:
	uv sync --group lint
	uv run pre-commit run --all-files

.PHONY: install-all
install-all:
	uv sync --all-groups

.PHONY: run_readme
run_readme:
#	uv pip install -e .
	uv run cartai readme --description "Crafting intelligent E2E documentation for trustworthy AI." --code "." --output "README_new.md"

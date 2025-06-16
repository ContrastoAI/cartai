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
#   uv run ruff format --check
#   uv run ruff check
	uv run mypy . --exclude examples/ --exclude tests/

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

# MLflow and MCP Server commands
.PHONY: mlflow-build
mlflow-build:
	cd example_integrations/mlflow && docker-compose build

.PHONY: mlflow-clean
mlflow-clean:
	cd example_integrations/mlflow && docker-compose down -v

.PHONY: mlflow-start
mlflow-start:
	cd example_integrations/mlflow && docker-compose up -d

.PHONY: mcp-server
mcp-server:
	uv run python ./cartai/mcps/servers/mcp_main_server.py

.PHONY: start-all
start-all: mlflow-clean mlflow-build mlflow-start mcp-server

.PHONY: agent
agent:
	uv run python .\examples\ml_pipeline_orchestration.py

# deprecated

.PHONY: agent-deprecated
agent-deprecated:
	uv run python ./cartai/deprecated/oversight/agent.py 'List experiments please'

.PHONY: run-readme
run-readme:
#	uv pip install -e .
	uv run cartai readme --description "Crafting intelligent E2E documentation for trustworthy AI." --code "." --output "README_new.md"

.PHONY: install quality test train build deploy dbt-gcs clean help

help:
	@echo "Available targets:"
	@echo "  install    - Set up development environment with uv"
	@echo "  quality    - Run code quality checks (Ruff, Mypy)"
	@echo "  test       - Run pytest test suite"
	@echo "  train      - Run default training pipeline"
	@echo "  build      - Build production Docker image"
	@echo "  deploy     - Deploy to cloud environment"
	@echo "  dbt-gcs    - Run dbt GCS model (requires GCS_KEY_ID and GCS_SECRET env vars)"
	@echo "  clean      - Remove temporary files and caches"

install:
	@echo "Installing dependencies with uv..."
	uv venv
	uv pip install -e ".[dev]"
	@echo "Setting up pre-commit hooks..."
	uv run pre-commit install
	@echo "✓ Development environment ready"

quality:
	@echo "Running code quality checks..."
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/
	uv run mypy src/ tests/
	@echo "✓ Code quality checks passed"

test:
	@echo "Running test suite..."
	uv run pytest tests/ -v
	@echo "✓ Tests passed"

train:
	@echo "Running training pipeline..."
	@set -a && . ./.env && set +a && uv run python -m src.tasks.train
	@echo "✓ Training complete"

build:
	@echo "Building Docker image..."
	docker build -t tabular-pipeline:latest -f infra/Dockerfile .
	@echo "✓ Docker image built"

deploy:
	@echo "Deploying to cloud environment..."
	@bash infra/deploy.sh
	@echo "✓ Deployment complete"

dbt-gcs:
	@echo "Running dbt GCS model..."
	@if [ ! -f .env ]; then echo "Error: .env file not found. Copy .env.example and add your credentials."; exit 1; fi
	@set -a && . ./.env && set +a && cd dbt/telco_pipeline && uv run dbt run --profiles-dir .. --select stg_churn_gcs
	@echo "✓ GCS model complete"

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

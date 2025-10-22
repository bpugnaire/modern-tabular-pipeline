.PHONY: install quality test train build deploy clean gcs-setup help

help:
	@echo "Available targets:"
	@echo "  install    - Set up development environment with uv"
	@echo "  quality    - Run code quality checks (Ruff, Mypy)"
	@echo "  test       - Run pytest test suite"
	@echo "  train      - Run default training pipeline"
	@echo "  build      - Build production Docker image"
	@echo "  deploy     - Deploy to cloud environment"
	@echo "  gcs-setup  - Set up and test Google Cloud Storage access"
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
	@echo "Running default training pipeline..."
	uv run python src/tabular_pipeline/pipelines/train.py
	@echo "✓ Training complete"

build:
	@echo "Building Docker image..."
	docker build -t tabular-pipeline:latest -f infra/Dockerfile .
	@echo "✓ Docker image built"

deploy:
	@echo "Deploying to cloud environment..."
	@bash infra/deploy.sh
	@echo "✓ Deployment complete"

gcs-setup:
	@echo "Setting up Google Cloud Storage access..."
	@bash dbt/setup_gcs.sh
	@echo "✓ GCS setup complete"

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

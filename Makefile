.PHONY: install quality test train build deploy dbt-gcs clean help api-dev api-test docker-up docker-down deploy-training deploy-api

help:
	@echo "Available targets:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Set up development environment with uv"
	@echo "  quality      - Run code quality checks (Ruff, Mypy)"
	@echo "  test         - Run pytest test suite"
	@echo "  clean        - Remove temporary files and caches"
	@echo ""
	@echo "Training:"
	@echo "  train        - Run default training pipeline"
	@echo "  dbt-gcs      - Run dbt GCS model (requires GCS_KEY_ID and GCS_SECRET)"
	@echo ""
	@echo "API Development:"
	@echo "  api-dev      - Run FastAPI server locally (hot-reload)"
	@echo "  api-test     - Test API with example requests"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up    - Start all services with Docker Compose"
	@echo "  docker-down  - Stop all services"
	@echo "  build-train  - Build training Docker image"
	@echo "  build-api    - Build API Docker image"
	@echo ""
	@echo "Cloud Deployment:"
	@echo "  deploy-training - Deploy training job to Vertex AI"
	@echo "  deploy-api      - Deploy API to Cloud Run"

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
	@echo "Building Docker images..."
	@$(MAKE) build-train
	@$(MAKE) build-api
	@echo "✓ All Docker images built"

deploy:
	@echo "Deploying to cloud environment..."
	@echo "Choose deployment target:"
	@echo "  make deploy-training  - Deploy training to Vertex AI"
	@echo "  make deploy-api       - Deploy API to Cloud Run"

dbt-gcs:
	@echo "Running dbt GCS model..."
	@if [ ! -f .env ]; then echo "Error: .env file not found. Copy .env.example and add your credentials."; exit 1; fi
	@set -a && . ./.env && set +a && cd dbt/telco_pipeline && uv run dbt run --profiles-dir .. --select stg_churn_gcs
	@echo "✓ GCS model complete"

# API Development
api-dev:
	@echo "Starting FastAPI development server..."
	@set -a && . ./.env && set +a && uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

api-test:
	@echo "Testing API..."
	@uv run python examples/api_client.py

# Docker commands
docker-up:
	@echo "Starting services with Docker Compose..."
	cd infra/docker && docker-compose up -d
	@echo "✓ Services started"
	@echo "  - MLflow UI: http://localhost:5000"
	@echo "  - API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"

docker-down:
	@echo "Stopping services..."
	cd infra/docker && docker-compose down
	@echo "✓ Services stopped"

build-train:
	@echo "Building training Docker image..."
	docker build -f infra/docker/Dockerfile.train -t churn-training:latest .
	@echo "✓ Training image built"

build-api:
	@echo "Building API Docker image..."
	docker build -f infra/docker/Dockerfile.api -t churn-api:latest .
	@echo "✓ API image built"

# Cloud deployment
deploy-training:
	@echo "Deploying training to Vertex AI..."
	@bash infra/gcp/deploy_training.sh

deploy-api:
	@echo "Deploying API to Cloud Run..."
	@bash infra/gcp/deploy_api.sh

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

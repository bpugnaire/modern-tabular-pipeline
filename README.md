# Modern Tabular Pipeline

A production-grade, end-to-end ML system for tabular data that serves as a reusable template for future projects.

## 🎯 Project Overview

This project implements a complete machine learning pipeline for **Telco Customer Churn Prediction** (Binary Classification) using the IBM Telco Customer Churn dataset from Kaggle. The architecture is designed to be data-agnostic and easily adaptable to new tabular datasets.

## 🏗️ Architecture

The system is composed of four distinct layers:

1. **Data Layer** (`dbt` + `DuckDB` + `Polars`)
   - Ingests versioned raw data from cloud storage
   - Cleans, transforms, and creates features
   - Outputs versioned, tested feature tables

2. **Experimentation Layer** (`Hydra` + `MLflow` + `Ray` + `PyTorch`)
   - Loads feature tables
   - Preprocesses data for ML
   - Trains and evaluates multiple model architectures
   - Tracks experiments and manages model lifecycle

3. **Serving Layer** (`FastAPI` + `Docker`)
   - Wraps models in a high-performance REST API
   - Defines clear data contracts for inference
   - Containerized for portability

4. **Deployment Layer** (`GCP Cloud Run` + `GitHub Actions`)
   - Deploys containers as serverless services
   - Automates testing and deployment via CI/CD

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (for containerization)
- GCP account (for deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/modern-tabular-pipeline.git
cd modern-tabular-pipeline

# Set up development environment
make install
```

### Key Commands

```bash
make help      # Show all available commands
make quality   # Run code quality checks
make test      # Run test suite
make train     # Run default training pipeline
make build     # Build Docker image
make deploy    # Deploy to cloud
make clean     # Clean temporary files
```

## 📁 Project Structure

```
modern-tabular-pipeline/
├── dbt/                    # dbt project for feature engineering
├── notebooks/              # Marimo notebooks for EDA and visualization
├── src/tabular_pipeline/   # Core Python package
│   ├── data/              # Data processing modules
│   ├── models/            # Model definitions
│   ├── pipelines/         # Training and inference pipelines
│   └── api/               # FastAPI application
├── configs/               # Hydra configuration files
├── infra/                 # Infrastructure and deployment assets
├── tests/                 # pytest test suite
├── .github/workflows/     # CI/CD workflows
├── pyproject.toml         # Project dependencies
├── Makefile               # Developer shortcuts
└── CONTEXT.md             # Detailed project blueprint
```

## 🛠️ Technology Stack

- **Package Management**: uv
- **Notebooks**: marimo
- **Data Warehouse**: DuckDB
- **Data Transformation**: dbt, Polars
- **Configuration**: Hydra
- **Experiment Tracking**: MLflow
- **Distributed Compute**: Ray
- **Modeling**: CatBoost, PyTorch
- **API Framework**: FastAPI
- **Containerization**: Docker
- **Deployment**: GCP Cloud Run
- **Code Quality**: Ruff, Mypy, pre-commit
- **CI/CD**: GitHub Actions

## 🔄 Workflows

### Local Development
```bash
# Run EDA with marimo
marimo run notebooks/explore.py

# Run dbt transformations
dbt build

# Train a model
python src/tabular_pipeline/pipelines/train.py

# Validate before commit
make quality test
```

### Experimentation
```bash
# Run hyperparameter optimization
python src/tabular_pipeline/pipelines/hpo.py

# View experiments
mlflow ui

# Promote best model to production
mlflow models ...
```

### CI/CD
- Pull requests automatically run quality checks and tests
- Merges to main can trigger automated deployments

## 📊 Core Principles

- **Designed for Templating**: Data-agnostic architecture
- **Modularity**: Decoupled components
- **Robust Automation**: Pre-commit hooks and CI/CD
- **Production-Ready**: Packaged application with tests
- **Cloud-Agnostic**: Swappable cloud services
- **Tasteful Tooling**: Modern best practices

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please ensure all code passes quality checks:
```bash
make quality test
```

## 📚 Documentation

See [CONTEXT.md](CONTEXT.md) for the complete project blueprint and detailed rationale.

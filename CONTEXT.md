
# Project Blueprint: Modern Tabular Pipeline

## 1. Project Identity

- **Project Name:** `modern-tabular-pipeline`

- **Mission:** To build a production-grade, end-to-end ML system for tabular data that serves as a reusable template for future projects.

- **Problem Domain:** Telco Customer Churn Prediction (Binary Classification). This serves as the initial reference implementation.

- **Source Dataset:** IBM Telco Customer Churn from Kaggle.

- **Key Deliverables:**

    1. A public GitHub repository with fully reproducible code.

    2. A containerized, live REST API for online churn predictions.

    3. A reusable project template that can be adapted to new tabular datasets with minimal changes.

    4. A series of technical articles based on the project's components and findings.


## 2. Core Principles

This project is guided by the following principles:

- **Designed for Templating:** The architecture is intentionally data-agnostic. Logic is separated from configuration to allow easy adaptation to new datasets and models.

- **Modularity:** Each component (data, training, inference) is decoupled and can be worked on independently.

- **Robust Automation:** The project enforces high code quality and reproducibility through automated checks, including `pre-commit` hooks for linting (`Ruff`), type checking (`Mypy`), and formatting.

- **Production-Readiness:** This is a packaged Python application with tests, CI/CD, and a deployment target, mirroring a real-world production system.

- **Cloud-Agnosticism:** The core application logic is independent of any specific cloud provider. Cloud services are used for commodity tasks via simple, swappable scripts.

- **Tasteful Tooling:** Every tool is chosen for a specific, justified reason, emphasizing modern best practices.


## 3. System Architecture

The system is composed of four distinct, data-agnostic layers.

```
[ Raw Data (Cloud Storage: GCS/S3 w/ Delta Lake or Iceberg) ]
             |
             v
[ 1. Data Layer (dbt + DuckDB + Polars) ]
    - Ingests versioned raw data.
    - Cleans, transforms, and creates features.
    - Outputs a versioned, tested feature table (Parquet).
             |
             v
[ 2. Experimentation Layer (Hydra + MLflow + Ray + PyTorch) ]
    - Loads the feature table.
    - Preprocesses data for ML (scaling, encoding).
    - Trains and evaluates multiple model architectures.
    - Tracks all experiments, parameters, metrics, and artifacts.
    - Manages model lifecycle via a Model Registry.
             |
             v
[ 3. Serving Layer (FastAPI + Docker) ]
    - Fetches the "Production" model from the Model Registry.
    - Wraps the model in a high-performance REST API.
    - Defines a clear data contract for inference requests.
    - Is containerized for portability.
             |
             v
[ 4. Deployment Layer (GCP Cloud Run + GitHub Actions) ]
    - Deploys the Docker container as a serverless, scalable web service.
    - Automates testing and deployment via CI/CD pipelines.
```

## 4. Technology Stack & Rationale

|   |   |   |
|---|---|---|
|**Component**|**Tool**|**Role & Rationale**|
|**Dependency Mgmt**|`uv`|An extremely fast Python package installer and resolver. Chosen for its performance and modern approach to managing `pyproject.toml`.|
|**Notebooks**|`marimo`|Reactive, interactive notebooks for EDA, visualization, and building simple data apps. Chosen for its reproducible and clean state management compared to traditional notebooks.|
|**Data Warehouse**|`DuckDB`|A file-based analytical engine. Can read versioned formats (Delta/Iceberg) from cloud storage, enabling a powerful local development workflow.|
|**Data Transformation**|`dbt` (`dbt-duckdb`, `dbt-python`)|The definitive tool for building versioned and tested data pipelines. Integrates `Polars` logic directly into the dbt DAG.|
|**Data Processing (Py)**|`Polars`|A high-performance DataFrame library. The modern, faster alternative to `pandas`.|
|**Configuration**|`Hydra`|Manages complex YAML configurations. Enables clean, composable experiments, crucial for a reusable template.|
|**Experiment Tracking**|`MLflow`|The open-source MLOps standard. Chosen for its integrated solution, especially the **Model Registry**, which is critical for the production workflow.|
|**Distributed Compute**|`Ray` (`Ray Tune`)|The modern standard for distributed Python. Used for efficient Hyperparameter Optimization (HPO).|
|**Modeling**|`CatBoost` / `PyTorch`|Pluggable model architectures. The system is designed to easily add or swap models via configuration.|
|**API Framework**|`FastAPI`|High-performance Python web framework for building REST APIs.|
|**Containerization**|`Docker`|The universal standard for packaging applications, ensuring consistency across environments.|
|**Deployment Platform**|`GCP Cloud Run`|A serverless container platform chosen for its simplicity and scalability. The architecture remains cloud-agnostic.|
|**Code Quality**|`pre-commit`, `Ruff`, `Mypy`|A suite of tools for automated code quality. `pre-commit` runs hooks, `Ruff` handles fast linting/formatting, and `Mypy` performs static type checking.|
|**CI/CD**|`GitHub Actions`|The native automation engine for GitHub. Used to run the code quality suite and trigger authenticated cloud deployments.|

## 5. Component Logic & File Structure

This section outlines the repository's structure, focusing on the purpose of each component.

- **`modern-tabular-pipeline/`**: The project root.

    - `pyproject.toml`: Project metadata and dependencies, managed by `uv`.

    - `.pre-commit-config.yaml`: Configuration for pre-commit hooks.

    - `Makefile`: A set of shortcuts for common developer tasks.

    - `CONTEXT.md`: This file.

    - `README.md`: Human-friendly project overview.

- **`dbt/`**: The dbt project for all pre-model feature engineering.

- **`notebooks/`**: Marimo notebooks for exploratory data analysis (EDA), visualization, and presenting results.

- **`src/tabular_pipeline/`**: The installable Python package containing all core ML logic (data processing, model definitions, training pipelines, and inference API).

- **`configs/`**: The Hydra configuration directory, enabling full control without code changes.

- **`infra/`**: Infrastructure-as-Code and deployment assets (Dockerfiles, cloud scripts).

- **`tests/`**: The `pytest` suite for the Python package.

- **`.github/workflows/`**: GitHub Actions workflows for CI/CD.


## 6. Key Workflows

This project supports several distinct workflows for different stages of development and deployment.

#### 1. The Local Development Loop (DS/ML Engineer)

This is the "inner loop" for rapid, local iteration and debugging.

- **Setup:** A developer clones the repo and runs `make install` to create a local `uv` environment.

- **Exploration:** Use `marimo` notebooks in the `notebooks/` directory for EDA. These notebooks can directly query versioned data (e.g., Delta Lake tables) from cloud storage using DuckDB. This provides **local compute on fresh cloud data**.

- **Iteration:** Run individual training pipelines (`python src/tabular_pipeline/pipelines/train.py ...`) to test model changes. Debug feature logic by running `dbt build` locally.

- **Validation:** Before committing, run `make quality` and `make test` to ensure code meets project standards.


#### 2. The Experimentation Loop (MLOps)

This is the loop for systematically finding the best model.

- **Scaling:** Run large-scale hyperparameter optimization sweeps using `Ray Tune` (`python src/tabular_pipeline/pipelines/hpo.py ...`).

- **Analysis:** Use the MLflow UI to compare hundreds of experiment runs, visualize metrics, and identify the top-performing models.

- **Promotion:** The best model version is promoted from "Staging" to "Production" within the MLflow Model Registry. This is a deliberate, human-in-the-loop step that signals a model is ready for deployment.


#### 3. The CI/CD Loop (Automation)

This is the automated "outer loop" triggered by Git events.

- **Pull Request:** When a PR is opened, a GitHub Action workflow automatically runs the full quality and test suite (`make quality test`). This acts as a gatekeeper, preventing low-quality code from being merged.

- **Merge to Main:** When a PR is merged into the `main` branch, a GitHub Action can be configured to automatically trigger the `make deploy` workflow, deploying the latest version of the API to a staging or production environment.


#### 4. The Makefile as an Accelerator

The `Makefile` provides a simple, consistent interface for all key operations, abstracting away the underlying commands.

- `make install`: Sets up the development environment.

- `make quality`: Runs all code quality checks (Ruff, Mypy).

- `make test`: Executes the `pytest` suite.

- `make train`: Runs a default training pipeline for a quick sanity check.

- `make build`: Builds the production Docker image.

- `make deploy`: Deploys the latest image to the configured cloud environment.

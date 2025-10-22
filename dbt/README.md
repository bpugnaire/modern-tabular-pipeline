# Telco Pipeline - dbt Project

This directory contains the dbt (data build tool) project for feature engineering and data transformation.

## Project Structure

```
dbt/
├── profiles.yml              # DuckDB connection configuration
└── telco_pipeline/
    ├── dbt_project.yml       # dbt project configuration
    ├── models/
    │   └── staging/
    │       ├── stg_churn.sql # Staging model for Telco Churn data
    │       └── schema.yml    # Model documentation and tests
    ├── macros/               # Custom SQL macros
    ├── seeds/                # Static CSV data
    ├── snapshots/            # Type-2 SCD snapshots
    └── tests/                # Custom data tests
```

## Quick Start

### Run the pipeline

```bash
cd dbt/telco_pipeline
uv run dbt run --profiles-dir ..
```

### Run tests

```bash
cd dbt/telco_pipeline
uv run dbt test --profiles-dir ..
```

### Build everything (run + test)

```bash
cd dbt/telco_pipeline
uv run dbt build --profiles-dir ..
```

## Models

### Staging Layer (`models/staging/`)

#### `stg_churn.sql`
Reads the IBM Telco Customer Churn dataset directly from GitHub and performs:
- Type casting (integers, decimals, booleans)
- Column renaming to snake_case
- Yes/No to boolean conversion
- Handling of missing/empty values in `total_charges`

**Source**: https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv

**Output**: 7,043 rows × 21 columns

**Tests**: 17 data quality tests including:
- Uniqueness of `customer_id`
- Non-null constraints on key fields
- Accepted values validation for categorical fields

#### `stg_churn_gcs.sql`
Same as `stg_churn.sql` but reads from Google Cloud Storage bucket.

**Source**: `gs://modern-tabular-dev/data/raw/Telco-Customer-Churn.csv`

**Requirements**:
- GCP authentication configured (see [GCS_SETUP.md](GCS_SETUP.md))
- Storage Object Viewer permissions on the bucket

**Setup**:
```bash
# Run the automated setup script
./setup_gcs.sh

# Or manually authenticate
gcloud auth application-default login
gcloud config set project modern-tabular-pipeline-dev
```

**Output**: 7,043 rows × 21 columns

**Tests**: 17 data quality tests

### Features Layer (`models/features/`)

#### `fct_churn_features.py` (Python/Polars)
Advanced feature engineering using Polars for high-performance transformations:

**Tenure Features:**
- `tenure_years` - Tenure converted to years
- `tenure_group` - Segmentation: new (<12mo), medium (12-36mo), long_term (>36mo)

**Financial Features:**
- `avg_monthly_charges` - Historical average monthly charges
- `charge_velocity` - Rate of change in charges (current vs average)
- `lifetime_value_proxy` - Customer lifetime value estimate
- `revenue_per_service` - Revenue efficiency metric
- `is_high_value` - Above-median monthly charges flag

**Service Features:**
- `total_services_count` - Count of premium services (0-6)
- `has_premium_services` - Any premium service flag
- `has_internet_service` - Internet service indicator
- `has_fiber_optic` - Fiber optic (premium) flag

**Contract & Risk Features:**
- `is_month_to_month` - Month-to-month contract flag
- `is_electronic_payment` - Electronic payment flag
- `churn_risk_score` - Composite risk score (0-10, higher = more risk)
- `engagement_score` - Customer engagement score (higher = more engaged)

**Output**: 7,043 rows × 36 columns

**Tests**: 10 data quality tests

**Key Insights:**
- Overall churn rate: 26.54%
- New customers (<12mo): 47.44% churn rate
- High risk score (10): 70.64% churn rate
- Month-to-month contracts: 55% of customers

## Configuration

### DuckDB Setup
- **Profile**: `telco_pipeline`
- **Target**: `dev` (default)
- **Database**: `target/dev.duckdb`
- **Extensions**: `httpfs`, `parquet`
- **Region**: `eu-west-3` (Paris)

### Materialization Strategy
- **Staging models**: Materialized as `table`
- **Feature models**: Materialized as `table`

## Data Quality

All models include comprehensive data tests defined in `schema.yml`:
- Primary key uniqueness
- Not-null constraints
- Accepted values for categorical columns
- Custom business logic tests

Run tests with:
```bash
uv run dbt test --profiles-dir ..
```

## Development

### View compiled SQL
```bash
cat target/compiled/telco_pipeline/models/staging/stg_churn.sql
```

### Generate documentation
```bash
uv run dbt docs generate --profiles-dir ..
uv run dbt docs serve --profiles-dir ..
```

### Clean build artifacts
```bash
uv run dbt clean
```

## Next Steps

Future models to add:
- `models/features/` - Feature engineering layer
- `models/marts/` - Business-specific data marts
- Custom macros for reusable logic
- dbt snapshots for tracking changes over time

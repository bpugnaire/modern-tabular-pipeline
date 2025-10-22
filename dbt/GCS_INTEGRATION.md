# GCS Integration Summary

## Files Created

### 1. Model Files
- `dbt/telco_pipeline/models/staging/stg_churn_gcs.sql`
  - Reads from `gs://modern-tabular-dev/data/raw/Telco-Customer-Churn.csv`
  - Identical transformation logic to `stg_churn.sql`
  - Tagged with `['staging', 'gcs']`

### 2. Documentation
- `dbt/GCS_SETUP.md` - Complete GCS setup guide
- `dbt/README.md` - Updated with GCS model information
- `dbt/telco_pipeline/models/staging/schema.yml` - Added GCS model schema and tests

### 3. Setup Scripts
- `dbt/setup_gcs.sh` - Automated GCS setup and testing script
- `Makefile` - Added `gcs-setup` target

## Usage

### Quick Start
```bash
# Authenticate with GCP
gcloud auth application-default login
gcloud config set project modern-tabular-pipeline-dev

# Run the GCS model
cd dbt/telco_pipeline
uv run dbt run --profiles-dir .. --select stg_churn_gcs
```

### Using the Setup Script
```bash
# Automated setup and test
make gcs-setup

# Or directly
./dbt/setup_gcs.sh
```

## Model Selection

You now have two staging models:

1. **`stg_churn`** - Reads from public GitHub URL
   - No authentication required
   - Good for demos and CI/CD
   - Always available

2. **`stg_churn_gcs`** - Reads from GCS bucket
   - Requires GCP authentication
   - Production data source
   - Better for data versioning and control

## Configuration

The dbt profile (`dbt/profiles.yml`) is configured for GCS:
```yaml
extensions:
  - httpfs
  - parquet
settings:
  s3_region: eu-west-3
  gcs_region: eu-west-3
```

DuckDB's `httpfs` extension handles GCS access automatically when `GOOGLE_APPLICATION_CREDENTIALS` is set.

## Authentication Methods

### Development (Local)
```bash
gcloud auth application-default login
```

### Production (Service Account)
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### CI/CD (GitHub Actions)
```yaml
- uses: google-github-actions/auth@v1
  with:
    credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
```

## Testing

Both models have identical tests (17 data quality tests each):
```bash
# Test GitHub model
uv run dbt test --profiles-dir .. --select stg_churn

# Test GCS model
uv run dbt test --profiles-dir .. --select stg_churn_gcs
```

## Data Upload

If you need to upload data to GCS:
```bash
# Download the CSV
curl -o Telco-Customer-Churn.csv \
  https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv

# Upload to GCS
gsutil cp Telco-Customer-Churn.csv gs://modern-tabular-dev/data/raw/
```

## Dependencies Installed

- `gcsfs==2025.9.0` - Google Cloud Storage filesystem interface
- `google-cloud-storage==3.4.1` - Official GCS client library
- `google-auth` and related packages - Authentication

## Next Steps

1. **Authenticate with GCP**: Run `gcloud auth application-default login`
2. **Upload data**: Ensure the CSV is in `gs://modern-tabular-dev/data/raw/`
3. **Test the model**: Run `make gcs-setup` or `dbt run --select stg_churn_gcs`
4. **Use in features**: Update `fct_churn_features.py` to use GCS source if desired

## Troubleshooting

See `dbt/GCS_SETUP.md` for detailed troubleshooting steps.

Common issues:
- **Access Denied**: Check authentication and bucket permissions
- **File Not Found**: Verify the file exists with `gsutil ls`
- **Extension Error**: Ensure `httpfs` is in the extensions list

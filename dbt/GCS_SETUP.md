# Google Cloud Storage (GCS) Setup Guide

This guide explains how to configure DuckDB to read data from Google Cloud Storage buckets.

## Project Configuration

- **GCP Project**: `modern-tabular-pipeline-dev`
- **GCS Bucket**: `gs://modern-tabular-dev/`
- **Data Location**: `gs://modern-tabular-dev/data/raw/Telco-Customer-Churn.csv`
- **Region**: `eu-west-3` (Paris)

## Prerequisites

1. **Google Cloud SDK** installed
2. **gcloud** CLI authenticated
3. **Service Account** with Storage Object Viewer permissions (or use Application Default Credentials)

## Setup Methods

### Method 1: Application Default Credentials (Recommended for Development)

This is the easiest method for local development:

```bash
# Authenticate with your Google account
gcloud auth application-default login

# Set your project
gcloud config set project modern-tabular-pipeline-dev
```

DuckDB will automatically use these credentials via the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

### Method 2: Service Account Key (Recommended for Production)

1. **Create a Service Account:**
```bash
gcloud iam service-accounts create dbt-duckdb-reader \
    --display-name="dbt DuckDB GCS Reader" \
    --project=modern-tabular-pipeline-dev
```

2. **Grant Storage Permissions:**
```bash
gcloud projects add-iam-policy-binding modern-tabular-pipeline-dev \
    --member="serviceAccount:dbt-duckdb-reader@modern-tabular-pipeline-dev.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

3. **Create and Download Key:**
```bash
gcloud iam service-accounts keys create ~/.gcp/dbt-duckdb-key.json \
    --iam-account=dbt-duckdb-reader@modern-tabular-pipeline-dev.iam.gserviceaccount.com
```

4. **Set Environment Variable:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcp/dbt-duckdb-key.json"
```

Add this to your shell profile (`.bashrc`, `.zshrc`, etc.):
```bash
echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcp/dbt-duckdb-key.json"' >> ~/.zshrc
```

### Method 3: Environment Variable in .env File

Create a `.env` file in the project root (already in `.gitignore`):

```bash
# .env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GCP_PROJECT=modern-tabular-pipeline-dev
```

Then load it in your shell:
```bash
source .env
```

## Verify Setup

Test that DuckDB can access GCS:

```bash
cd dbt/telco_pipeline

# Test reading from GCS
uv run dbt run --profiles-dir .. --select stg_churn_gcs

# Run tests
uv run dbt test --profiles-dir .. --select stg_churn_gcs
```

## Upload Data to GCS

If you need to upload the data file:

```bash
# Download the file first
curl -o Telco-Customer-Churn.csv \
  https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv

# Upload to GCS
gsutil cp Telco-Customer-Churn.csv gs://modern-tabular-dev/data/raw/

# Verify upload
gsutil ls gs://modern-tabular-dev/data/raw/
```

## Models Available

### `stg_churn.sql`
- Reads from public GitHub URL
- No authentication required
- Good for demos and testing

### `stg_churn_gcs.sql`
- Reads from GCS bucket
- Requires GCP authentication
- Production-ready data source

## Troubleshooting

### Error: "No such file or directory"
- Check that the GCS path is correct
- Verify the file exists: `gsutil ls gs://modern-tabular-dev/data/raw/`

### Error: "Access Denied"
- Verify authentication: `gcloud auth application-default print-access-token`
- Check service account permissions
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set correctly

### Error: "httpfs extension not loaded"
- The DuckDB httpfs extension should be loaded automatically
- Check `dbt/profiles.yml` includes `httpfs` in extensions list

### Error: "Invalid GCS credentials"
- Regenerate application default credentials: `gcloud auth application-default login`
- Check that your service account key file exists and is valid

## Security Best Practices

1. **Never commit service account keys** to version control
2. **Use least privilege** - only grant Storage Object Viewer role
3. **Rotate keys regularly** (every 90 days)
4. **Use Workload Identity** in production Kubernetes environments
5. **Keep `.env` files** in `.gitignore`

## CI/CD Setup

For GitHub Actions or other CI/CD:

```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v1
  with:
    credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

- name: Run dbt
  run: |
    cd dbt/telco_pipeline
    uv run dbt run --profiles-dir .. --select stg_churn_gcs
```

## Bucket Organization

Recommended structure:

```
gs://modern-tabular-dev/
├── data/
│   ├── raw/              # Original source data
│   │   └── Telco-Customer-Churn.csv
│   ├── processed/        # dbt-processed data
│   └── features/         # Feature tables
├── models/               # Saved ML models
│   └── production/
└── artifacts/            # MLflow artifacts
```

## Additional Resources

- [DuckDB httpfs Extension](https://duckdb.org/docs/extensions/httpfs.html)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [dbt-duckdb Adapter](https://github.com/duckdb/dbt-duckdb)

# GCS Authentication

## Quick Setup

### 1. One-Time: Create Service Account & HMAC Keys
```bash
# Create service account
gcloud iam service-accounts create tabular-pipeline-sa \
    --display-name="Tabular Pipeline" \
    --project=modern-tabular-pipeline-dev

# Grant storage permissions
gcloud projects add-iam-policy-binding modern-tabular-pipeline-dev \
    --member="serviceAccount:tabular-pipeline-sa@modern-tabular-pipeline-dev.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Create HMAC keys (DuckDB requires these, not OAuth)
gsutil hmac create tabular-pipeline-sa@modern-tabular-pipeline-dev.iam.gserviceaccount.com
```

### 2. Create `.env` File
```bash
# Copy the example
cp .env.example .env

# Edit with your HMAC credentials from step 1
# .env
GCS_KEY_ID=GOOG1E...
GCS_SECRET=your-secret-here
```

The `.env` file is already in `.gitignore` - your credentials won't be committed.

## Usage

```bash
# Just run the make target - it loads .env automatically
make dbt-gcs
```

That's it! No need to export variables or edit shell configs.

## How It Works

- Makefile loads `.env` before running dbt
- dbt model uses `env_var()` to inject credentials into DuckDB secret
- DuckDB uses HMAC keys to authenticate to GCS

## Why HMAC Keys?

DuckDB's `httpfs` extension requires HMAC keys (like AWS access keys) for GCS, not OAuth tokens or service account JSON files.

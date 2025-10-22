#!/bin/bash
# Script to set up and test GCS access for dbt-duckdb

set -e

echo "==================================="
echo "GCS Setup and Test Script"
echo "==================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo "✓ gcloud CLI found"

# Check if authenticated
if gcloud auth application-default print-access-token &> /dev/null; then
    echo "✓ Already authenticated with GCP"
else
    echo "⚠️  Not authenticated. Running authentication..."
    gcloud auth application-default login
fi

# Set project
echo ""
echo "Setting GCP project..."
gcloud config set project modern-tabular-pipeline-dev

# Check if gsutil is available
if ! command -v gsutil &> /dev/null; then
    echo "❌ gsutil not found"
    exit 1
fi
echo "✓ gsutil found"

# Check if bucket exists
echo ""
echo "Checking GCS bucket..."
if gsutil ls gs://modern-tabular-dev/ &> /dev/null; then
    echo "✓ Bucket gs://modern-tabular-dev/ exists"
else
    echo "❌ Bucket gs://modern-tabular-dev/ not found or no access"
    exit 1
fi

# Check if data file exists
echo ""
echo "Checking for data file..."
if gsutil ls gs://modern-tabular-dev/data/raw/Telco-Customer-Churn.csv &> /dev/null; then
    echo "✓ Data file exists"
    FILE_SIZE=$(gsutil du -sh gs://modern-tabular-dev/data/raw/Telco-Customer-Churn.csv | awk '{print $1}')
    echo "  Size: $FILE_SIZE"
else
    echo "⚠️  Data file not found. Uploading..."

    # Download from GitHub
    echo "  Downloading from GitHub..."
    curl -sS -o /tmp/Telco-Customer-Churn.csv \
      https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv

    # Upload to GCS
    echo "  Uploading to GCS..."
    gsutil cp /tmp/Telco-Customer-Churn.csv gs://modern-tabular-dev/data/raw/

    echo "✓ Data file uploaded"
    rm /tmp/Telco-Customer-Churn.csv
fi

# Test dbt connection
echo ""
echo "==================================="
echo "Testing dbt with GCS..."
echo "==================================="
cd "$(dirname "$0")/telco_pipeline"

echo ""
echo "Running dbt debug..."
uv run dbt debug --profiles-dir ..

echo ""
echo "Running stg_churn_gcs model..."
uv run dbt run --profiles-dir .. --select stg_churn_gcs

echo ""
echo "Running tests..."
uv run dbt test --profiles-dir .. --select stg_churn_gcs

echo ""
echo "==================================="
echo "✓ GCS setup complete!"
echo "==================================="
echo ""
echo "You can now use the stg_churn_gcs model in dbt."
echo "Models available:"
echo "  - stg_churn      (reads from GitHub)"
echo "  - stg_churn_gcs  (reads from GCS)"

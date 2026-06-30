# Deployment Guide

This guide covers deploying the churn prediction model training and API to the cloud.

## Table of Contents

1. [Local Development](#local-development)
2. [Cloud Training (Vertex AI)](#cloud-training)
3. [API Deployment (Cloud Run)](#api-deployment)
4. [CI/CD Setup](#cicd-setup)
5. [Testing](#testing)

---

## Local Development

### Running Locally with Docker Compose

```bash
# Start MLflow, training, and API services
cd infra/docker
docker-compose up

# Run only API (after training)
docker-compose up api

# Run training job
docker-compose run --rm training
```

### Running API Locally (Without Docker)

```bash
# Set environment variables
export MODEL_URI="runs:/RUN_ID/model"  # or
export MODEL_PATH="/path/to/model.cbm"

# Run API
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Access API
open http://localhost:8000/docs
```

### Local Training

```bash
# Set credentials
export GCS_KEY_ID="your-key"
export GCS_SECRET="your-secret"

# Run training
python -m src.tasks.train

# View MLflow UI
mlflow ui --port 5000
open http://localhost:5000
```

---

## Cloud Training

### Prerequisites

1. **GCP Project Setup**
   ```bash
   # Set project ID
   export GCP_PROJECT_ID="your-project-id"
   export GCP_REGION="us-central1"

   # Enable required APIs
   gcloud services enable \
     aiplatform.googleapis.com \
     compute.googleapis.com \
     containerregistry.googleapis.com
   ```

2. **Service Account**
   ```bash
   # Create service account
   gcloud iam service-accounts create vertex-ai-trainer \
     --display-name="Vertex AI Training Service Account"

   # Grant permissions
   gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
     --member="serviceAccount:vertex-ai-trainer@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"

   gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
     --member="serviceAccount:vertex-ai-trainer@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"
   ```

### Deploy Training to Vertex AI

```bash
# Using deployment script
cd infra/gcp
./deploy_training.sh

# Or manually
docker build -f infra/docker/Dockerfile.train -t gcr.io/$GCP_PROJECT_ID/churn-training:latest .
docker push gcr.io/$GCP_PROJECT_ID/churn-training:latest

gcloud ai custom-jobs create \
  --region=$GCP_REGION \
  --display-name=churn-training-$(date +%Y%m%d-%H%M%S) \
  --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=gcr.io/$GCP_PROJECT_ID/churn-training:latest
```

### Monitor Training

```bash
# List jobs
gcloud ai custom-jobs list --region=$GCP_REGION

# View job details
gcloud ai custom-jobs describe JOB_ID --region=$GCP_REGION

# Stream logs
gcloud ai custom-jobs stream-logs JOB_ID --region=$GCP_REGION
```

---

## API Deployment

### Deploy to Cloud Run

```bash
# Set model URI
export MODEL_URI="runs:/YOUR_RUN_ID/model"

# Deploy using script
cd infra/gcp
./deploy_api.sh

# Or manually
docker build -f infra/docker/Dockerfile.api -t gcr.io/$GCP_PROJECT_ID/churn-api:latest .
docker push gcr.io/$GCP_PROJECT_ID/churn-api:latest

gcloud run deploy churn-prediction-api \
  --image=gcr.io/$GCP_PROJECT_ID/churn-api:latest \
  --platform=managed \
  --region=$GCP_REGION \
  --allow-unauthenticated \
  --port=8080 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --set-env-vars="MODEL_URI=$MODEL_URI"
```

### Configure Custom Domain (Optional)

```bash
# Map domain to service
gcloud run domain-mappings create \
  --service=churn-prediction-api \
  --domain=api.yourdomain.com \
  --region=$GCP_REGION
```

---

## CI/CD Setup

### GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
GCP_PROJECT_ID       # Your GCP project ID
GCP_SA_KEY          # Service account JSON key
MODEL_URI           # Default MLflow model URI (optional)
```

### Workflows

1. **Automatic API Deployment** (`.github/workflows/deploy-api.yml`)
   - Triggers on push to `main` when API code changes
   - Builds Docker image
   - Deploys to Cloud Run
   - Runs health checks

2. **Scheduled Training** (`.github/workflows/train-model.yml`)
   - Runs weekly on Mondays at 2am UTC
   - Submits training job to Vertex AI
   - Can be triggered manually with custom config

### Manual Workflow Triggers

```bash
# Trigger API deployment
gh workflow run deploy-api.yml

# Trigger training with custom config
gh workflow run train-model.yml -f config_name=production
```

---

## Testing

### Test API Locally

```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict/single \
  -H "Content-Type: application/json" \
  -d @examples/sample_customer.json

# Batch prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @examples/sample_batch.json
```

### Test Deployed API

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe churn-prediction-api \
  --platform=managed \
  --region=$GCP_REGION \
  --format='value(status.url)')

# Test endpoints
curl $SERVICE_URL/health
curl $SERVICE_URL/docs
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 -T 'application/json' \
  -p examples/sample_customer.json \
  $SERVICE_URL/predict/single
```

---

## Monitoring & Observability

### Cloud Run Metrics

```bash
# View metrics in console
open "https://console.cloud.google.com/run/detail/$GCP_REGION/churn-prediction-api/metrics?project=$GCP_PROJECT_ID"
```

### Logs

```bash
# Stream logs
gcloud run services logs tail churn-prediction-api \
  --region=$GCP_REGION

# View logs in console
gcloud run services logs read churn-prediction-api \
  --region=$GCP_REGION \
  --limit=50
```

### Alerts

Set up alerts in Cloud Monitoring for:
- High error rates (>5%)
- High latency (p99 >2s)
- Low CPU utilization (<10%)
- Container instance count

---

## Cost Optimization

### Cloud Run
- Set `--max-instances` to limit scaling
- Use `--min-instances=0` for infrequent traffic
- Set appropriate `--cpu` and `--memory` limits

### Vertex AI Training
- Use preemptible instances for cost savings
- Schedule training during off-peak hours
- Use smaller machine types when possible

### Storage
- Set lifecycle policies on GCS buckets
- Clean up old model versions regularly

---

## Troubleshooting

### API Won't Start
```bash
# Check logs
gcloud run services logs read churn-prediction-api --limit=100

# Common issues:
# - MODEL_URI not set or invalid
# - Insufficient memory (increase --memory)
# - Missing dependencies (rebuild image)
```

### Training Job Fails
```bash
# View job logs
gcloud ai custom-jobs stream-logs JOB_ID --region=$GCP_REGION

# Common issues:
# - GCS credentials not set
# - Insufficient disk space
# - Out of memory (use larger machine type)
```

### Prediction Errors
```bash
# Check model input schema
curl $SERVICE_URL/docs

# Validate input data matches CustomerFeatures schema
# Check model version compatibility
```

---

## Security Best Practices

1. **API Authentication**
   ```bash
   # Require authentication
   gcloud run services update churn-prediction-api \
     --no-allow-unauthenticated
   ```

2. **Network Security**
   - Use VPC connector for private resources
   - Set up Cloud Armor for DDoS protection
   - Enable Cloud CDN for caching

3. **Secrets Management**
   - Use Secret Manager for sensitive data
   - Rotate credentials regularly
   - Audit access logs

---

## Next Steps

1. Set up monitoring and alerting
2. Implement A/B testing for model versions
3. Add model versioning and rollback capabilities
4. Set up automated retraining pipeline
5. Implement feature drift detection
6. Add more comprehensive logging

---

For more information, see:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

# Quick Start: Deploy Churn Prediction API

This guide will help you deploy the churn prediction model and API in under 10 minutes.

## Prerequisites

- Docker installed
- GCP account (for cloud deployment)
- Python 3.11+ (for local development)

---

## Option 1: Local Development (Fastest)

### 1. Install Dependencies

```bash
make install
```

### 2. Set Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your GCS credentials
# GCS_KEY_ID=your-key
# GCS_SECRET=your-secret
```

### 3. Train Model Locally

```bash
make train
```

This will:
- Load features from GCS
- Train CatBoost model with balanced class weights
- Save model to MLflow (in `mlruns/` directory)
- Display training metrics

### 4. Start API Server

```bash
# Set model location (use run ID from training output)
export MODEL_URI="runs:/YOUR_RUN_ID/model"

# Start API
make api-dev
```

The API will be available at:
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### 5. Test API

```bash
# In another terminal
make api-test

# Or manually
curl http://localhost:8000/health

curl -X POST http://localhost:8000/predict/single \
  -H "Content-Type: application/json" \
  -d @examples/sample_customer.json
```

---

## Option 2: Docker Compose (Recommended for Teams)

### 1. Start All Services

```bash
make docker-up
```

This starts:
- **MLflow UI** at http://localhost:5000
- **API** at http://localhost:8000

### 2. Train Model

```bash
# Run training in Docker
docker-compose -f infra/docker/docker-compose.yml run --rm training
```

### 3. Update API with Trained Model

```bash
# Get the run ID from MLflow UI
export MODEL_URI="runs://YOUR_RUN_ID/model"

# Restart API with model
docker-compose -f infra/docker/docker-compose.yml up -d api
```

### 4. Test

```bash
curl http://localhost:8000/docs
```

### 5. Stop Services

```bash
make docker-down
```

---

## Option 3: Cloud Deployment (Production)

### Prerequisites

```bash
# Set GCP project
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# Authenticate
gcloud auth login
gcloud config set project $GCP_PROJECT_ID

# Enable APIs
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com
```

### 1. Deploy Training to Vertex AI

```bash
make deploy-training
```

This will:
- Build training Docker image
- Push to Google Container Registry
- Submit job to Vertex AI
- Return job name for monitoring

Monitor training:
```bash
# View in console
open "https://console.cloud.google.com/vertex-ai/training/custom-jobs?project=$GCP_PROJECT_ID"

# Or via CLI
gcloud ai custom-jobs list --region=$GCP_REGION
```

### 2. Get Model URI

After training completes:
1. Check MLflow artifacts in GCS
2. Or use local MLflow if artifacts are synced
3. Get the model URI: `runs:/RUN_ID/model`

### 3. Deploy API to Cloud Run

```bash
# Set model URI
export MODEL_URI="runs://YOUR_RUN_ID/model"

# Deploy
make deploy-api
```

This will:
- Build API Docker image
- Push to Google Container Registry
- Deploy to Cloud Run
- Return service URL

### 4. Test Deployed API

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe churn-prediction-api \
  --platform=managed \
  --region=$GCP_REGION \
  --format='value(status.url)')

# Test
curl $SERVICE_URL/health
open "$SERVICE_URL/docs"
```

---

## Quick API Usage Examples

### Python

```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8000/predict/single",
    json={
        "gender": "Female",
        "is_senior_citizen": False,
        "has_partner": True,
        "has_dependents": False,
        "tenure_months": 12,
        "tenure_years": 1.0,
        "tenure_group": "new",
        "monthly_charges": 65.0,
        "total_charges": 780.0,
        "avg_monthly_charges": 65.0,
        "charge_velocity": 0.0,
        "contract_type": "Month-to-month",
        "is_paperless_billing": True,
        "payment_method": "Electronic check",
        "is_month_to_month": True,
        "is_electronic_payment": True,
        "has_phone_service": True,
        "internet_service": "Fiber optic",
        "has_internet_service": True,
        "has_fiber_optic": True,
        "online_security": "No",
        "online_backup": "No",
        "device_protection": "No",
        "tech_support": "No",
        "streaming_tv": "Yes",
        "streaming_movies": "Yes",
        "multiple_lines": "No",
        "total_services_count": 2,
        "has_premium_services": True,
        "lifetime_value_proxy": 780.0,
        "revenue_per_service": 21.67,
        "is_high_value": True,
        "churn_risk_score": 8,
        "engagement_score": 4
    }
)

result = response.json()
print(f"Churn Probability: {result['churn_probability']:.2%}")
print(f"Risk Level: {result['risk_level']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function predictChurn(customer) {
  const response = await axios.post(
    'http://localhost:8000/predict/single',
    customer
  );

  const { churn_probability, will_churn, risk_level } = response.data;
  console.log(`Churn Probability: ${(churn_probability * 100).toFixed(2)}%`);
  console.log(`Risk Level: ${risk_level}`);
}
```

### cURL

```bash
curl -X POST http://localhost:8000/predict/single \
  -H "Content-Type: application/json" \
  -d @examples/sample_customer.json
```

---

## CI/CD Automation (GitHub Actions)

### Setup

1. Add GitHub secrets:
   ```
   GCP_PROJECT_ID   # Your GCP project ID
   GCP_SA_KEY       # Service account JSON key
   MODEL_URI        # Default model URI (optional)
   ```

2. Workflows will automatically:
   - Deploy API on push to `main`
   - Train model weekly on Mondays
   - Run on manual trigger

### Manual Triggers

```bash
# Deploy API
gh workflow run deploy-api.yml

# Train model
gh workflow run train-model.yml
```

---

## Monitoring

### Local

```bash
# View MLflow experiments
mlflow ui --port 5000
open http://localhost:5000

# View API logs
docker-compose -f infra/docker/docker-compose.yml logs -f api
```

### Cloud

```bash
# Cloud Run logs
gcloud run services logs tail churn-prediction-api --region=$GCP_REGION

# Vertex AI training logs
gcloud ai custom-jobs stream-logs JOB_ID --region=$GCP_REGION

# Open Cloud Console
open "https://console.cloud.google.com/run?project=$GCP_PROJECT_ID"
```

---

## Troubleshooting

### API won't start
```bash
# Check if model is set
echo $MODEL_URI

# Check logs
docker-compose -f infra/docker/docker-compose.yml logs api

# Verify model exists in MLflow
mlflow ui
```

### Training fails
```bash
# Check GCS credentials
echo $GCS_KEY_ID
echo $GCS_SECRET

# Verify data exists
gsutil ls gs://modern-tabular-dev/data/features/

# Check training logs
docker-compose -f infra/docker/docker-compose.yml logs training
```

### Prediction errors
```bash
# Verify input schema
curl http://localhost:8000/docs

# Check model compatibility
# Ensure feature names match training data
```

---

## Next Steps

1. **Customize the model**: Edit `configs/training/default.yaml`
2. **Add monitoring**: Set up Cloud Monitoring alerts
3. **Scale the API**: Adjust Cloud Run settings
4. **Automate retraining**: Schedule training jobs
5. **A/B test models**: Deploy multiple versions

For detailed documentation, see [DEPLOYMENT.md](DEPLOYMENT.md)

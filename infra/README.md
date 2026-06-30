# API & Deployment Guide

## Overview

This directory contains everything needed to deploy the churn prediction model:

### 📁 Directory Structure

```
infra/
├── docker/              # Docker containers
│   ├── Dockerfile.train       # Training image
│   ├── Dockerfile.api         # API serving image
│   └── docker-compose.yml     # Local dev setup
│
├── gcp/                 # Cloud deployment
│   ├── deploy_training.sh     # Deploy to Vertex AI
│   └── deploy_api.sh          # Deploy to Cloud Run
│
├── DEPLOYMENT.md        # Full deployment guide
└── README.md           # This file
```

## 🚀 Quick Start

### Local Development

```bash
# 1. Start all services
make docker-up

# 2. Access services
# - API: http://localhost:8000/docs
# - MLflow: http://localhost:5000

# 3. Test API
make api-test

# 4. Stop services
make docker-down
```

### Cloud Deployment

```bash
# 1. Set GCP project
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# 2. Deploy training
make deploy-training

# 3. Deploy API (after getting model URI)
export MODEL_URI="runs://YOUR_RUN_ID/model"
make deploy-api
```

## 📚 Documentation

- **[QUICKSTART.md](../QUICKSTART.md)** - Get started in 10 minutes
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide
- **[API Examples](../examples/)** - Sample requests and client code

## 🛠️ Available Make Commands

### Development
```bash
make install      # Setup environment
make train        # Train model locally
make api-dev      # Run API with hot-reload
make api-test     # Test API endpoints
```

### Docker
```bash
make docker-up      # Start all services
make docker-down    # Stop all services
make build-train    # Build training image
make build-api      # Build API image
```

### Cloud Deployment
```bash
make deploy-training  # Deploy to Vertex AI
make deploy-api       # Deploy to Cloud Run
```

## 🌐 API Endpoints

Once running, access these endpoints:

- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Single Prediction**: POST http://localhost:8000/predict/single
- **Batch Prediction**: POST http://localhost:8000/predict

### Example Request

```bash
curl -X POST http://localhost:8000/predict/single \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female",
    "is_senior_citizen": false,
    "has_partner": true,
    "tenure_months": 12,
    "monthly_charges": 65.0,
    ...
  }'
```

See [examples/](../examples/) for complete request examples.

## 🔧 Configuration

### Environment Variables

```bash
# Required for training
GCS_KEY_ID=your-gcs-key
GCS_SECRET=your-gcs-secret

# Required for API
MODEL_URI=runs://run-id/model  # OR
MODEL_PATH=/path/to/model.cbm

# Optional
MLFLOW_TRACKING_URI=http://mlflow:5000
PORT=8080
```

### Training Config

Edit `configs/training/default.yaml`:

```yaml
model:
  type: catboost
  iterations: 100
  learning_rate: 0.1
  depth: 6
  auto_class_weights: Balanced  # Important for class imbalance!
```

## 🐳 Docker Services

### MLflow Tracking Server
- **Port**: 5000
- **Purpose**: Track experiments and store models
- **Access**: http://localhost:5000

### API Server
- **Port**: 8000
- **Purpose**: Serve predictions
- **Access**: http://localhost:8000/docs

### Training Job
- **Mode**: Run once
- **Purpose**: Train model and log to MLflow
- **Command**: `docker-compose run --rm training`

## ☁️ Cloud Architecture

```
Training Flow:
┌─────────┐    ┌──────────────┐    ┌─────────┐
│ GCS     │───▶│ Vertex AI    │───▶│ MLflow  │
│ Data    │    │ Training     │    │ Registry│
└─────────┘    └──────────────┘    └─────────┘

Serving Flow:
┌─────────┐    ┌──────────────┐    ┌──────────┐
│ Client  │───▶│ Cloud Run    │───▶│ Model    │
│ Request │    │ API          │    │ Service  │
└─────────┘    └──────────────┘    └──────────┘
                      │
                      ▼
              ┌──────────────┐
              │ Auto-scaling │
              │ Load Balancer│
              └──────────────┘
```

## 🔍 Monitoring

### Local
```bash
# View MLflow experiments
mlflow ui

# View API logs
docker-compose logs -f api

# View training logs
docker-compose logs training
```

### Cloud
```bash
# API logs
gcloud run services logs tail churn-prediction-api

# Training logs
gcloud ai custom-jobs stream-logs JOB_ID

# Metrics dashboard
open "https://console.cloud.google.com/run?project=$GCP_PROJECT_ID"
```

## 🧪 Testing

### Unit Tests
```bash
# Run API tests
pytest tests/api/

# With coverage
pytest tests/api/ --cov=src/api
```

### Integration Tests
```bash
# Test live API
python examples/api_client.py

# Or with curl
curl http://localhost:8000/health
```

## 📊 CI/CD

GitHub Actions workflows automatically:

1. **Deploy API** on push to `main` when API code changes
2. **Train Model** weekly on Mondays at 2am UTC
3. **Manual triggers** for both via GitHub UI

See [.github/workflows/](.github/workflows/) for details.

## 🔐 Security

### Production Checklist

- [ ] Enable authentication on Cloud Run
- [ ] Use Secret Manager for credentials
- [ ] Set up VPC connector for private resources
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Configure IAM roles properly
- [ ] Set up audit logging
- [ ] Rotate credentials regularly

### API Authentication

```bash
# Require authentication
gcloud run services update churn-prediction-api \
  --no-allow-unauthenticated
```

## 💡 Tips & Best Practices

1. **Always use balanced class weights** for churn prediction
2. **Version your models** with meaningful tags in MLflow
3. **Monitor prediction latency** and set alerts
4. **Test with production-like data** before deploying
5. **Set resource limits** to control costs
6. **Use staging environments** for testing changes
7. **Log all predictions** for audit and debugging

## 🐛 Troubleshooting

### API won't start
```bash
# Check logs
docker-compose logs api

# Verify model URI
echo $MODEL_URI

# Test model loading
python -c "import mlflow; mlflow.catboost.load_model('$MODEL_URI')"
```

### Training fails
```bash
# Check credentials
echo $GCS_KEY_ID

# Verify data exists
gsutil ls gs://modern-tabular-dev/data/features/

# Check logs
docker-compose logs training
```

### Prediction errors
```bash
# Verify input schema
curl http://localhost:8000/docs

# Check model version
curl http://localhost:8000/health

# Test with known-good example
curl -X POST http://localhost:8000/predict/single \
  -H "Content-Type: application/json" \
  -d @examples/sample_customer.json
```

## 📈 Performance Optimization

### API Performance
- Use connection pooling for database/cache
- Implement request batching for high throughput
- Cache model predictions for common inputs
- Use async endpoints for I/O-bound operations

### Training Performance
- Use GPU instances for large datasets
- Implement early stopping
- Optimize hyperparameter search space
- Use distributed training for very large datasets

## 🔄 Model Updates

### Retraining Workflow
1. Schedule training with GitHub Actions or Cloud Scheduler
2. Train new model on Vertex AI
3. Log model to MLflow with version tag
4. Validate model performance
5. Update MODEL_URI and redeploy API
6. Monitor for regressions

### A/B Testing
```python
# Load two models
model_a = mlflow.catboost.load_model("runs://version-a/model")
model_b = mlflow.catboost.load_model("runs://version-b/model")

# Route traffic (e.g., 50/50 split)
if random.random() < 0.5:
    prediction = model_a.predict(features)
else:
    prediction = model_b.predict(features)
```

## 📝 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [CatBoost Documentation](https://catboost.ai/docs/)

## 🤝 Contributing

When adding new features:
1. Update API schemas in `src/api/schemas.py`
2. Add tests in `tests/api/`
3. Update documentation
4. Test locally with Docker Compose
5. Deploy to staging before production

## 📞 Support

For issues or questions:
1. Check [troubleshooting section](#troubleshooting)
2. Review [deployment guide](DEPLOYMENT.md)
3. Check API docs at `/docs` endpoint
4. Review logs and metrics

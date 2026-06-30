#!/bin/bash
# Deploy API to Cloud Run

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="churn-prediction-api"
IMAGE_NAME="churn-api"
IMAGE_TAG=${IMAGE_TAG:-"latest"}
IMAGE_URI="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"
MODEL_URI=${MODEL_URI:-""}

echo "======================================"
echo "Deploying API to Cloud Run"
echo "======================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_URI}"
echo "Model URI: ${MODEL_URI}"
echo "======================================"

# Build and push Docker image
echo "Building Docker image..."
docker build -f infra/docker/Dockerfile.api -t ${IMAGE_URI} .

echo "Pushing image to GCR..."
docker push ${IMAGE_URI}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URI} \
  --platform=managed \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --allow-unauthenticated \
  --port=8080 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --set-env-vars="MODEL_URI=${MODEL_URI}" \
  --timeout=300

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform=managed \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --format='value(status.url)')

echo ""
echo "✓ API deployed successfully!"
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Test the API:"
echo "  curl ${SERVICE_URL}/health"
echo "  curl ${SERVICE_URL}/docs"

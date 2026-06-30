#!/bin/bash
# Deploy training job to Vertex AI

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
IMAGE_NAME="churn-training"
IMAGE_TAG=${IMAGE_TAG:-"latest"}
IMAGE_URI="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"
JOB_NAME="churn-training-$(date +%Y%m%d-%H%M%S)"

echo "======================================"
echo "Deploying Training Job to Vertex AI"
echo "======================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Image: ${IMAGE_URI}"
echo "Job Name: ${JOB_NAME}"
echo "======================================"

# Build and push Docker image
echo "Building Docker image..."
docker build -f infra/docker/Dockerfile.train -t ${IMAGE_URI} .

echo "Pushing image to GCR..."
docker push ${IMAGE_URI}

# Submit training job to Vertex AI
echo "Submitting training job to Vertex AI..."
gcloud ai custom-jobs create \
  --region=${REGION} \
  --display-name=${JOB_NAME} \
  --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=${IMAGE_URI} \
  --project=${PROJECT_ID} \
  --args="--config-name=default"

echo "✓ Training job submitted successfully!"
echo "Monitor at: https://console.cloud.google.com/vertex-ai/training/custom-jobs?project=${PROJECT_ID}"

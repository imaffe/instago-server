#!/bin/bash

# Deployment script for Instago Server to Google Cloud Run

# Set variables
PROJECT_ID=${1:-$(gcloud config get-value project)}
SERVICE_NAME="instago-server"
REGION="us-central1"
IMAGE_TAG=${2:-latest}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set. Usage: ./deploy.sh [PROJECT_ID] [IMAGE_TAG]"
    exit 1
fi

echo "Deploying to project: $PROJECT_ID"
echo "Service name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Image tag: $IMAGE_TAG"

# Build the Docker image for linux/amd64 platform
echo "Building Docker image for linux/amd64..."
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG .

# Push to Google Container Registry
echo "Pushing image to GCR..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG

# Deploy to Cloud Run using service.yaml
echo "Deploying to Cloud Run using service.yaml..."

# First update the image tag in service.yaml
sed -i.bak "s|gcr.io/careful-pillar-464706-d1/instago-server:.*|gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG|g" service.yaml

# Deploy using the service configuration
gcloud run services replace service.yaml \
    --region $REGION \
    --project $PROJECT_ID

# Make the service publicly accessible
echo "Making service publicly accessible..."
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --region=$REGION \
    --project=$PROJECT_ID

echo "Deployment complete!"
echo "Service URL:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)' --project $PROJECT_ID
#!/bin/bash

# Script to create and store a service account key for GCS access

PROJECT_ID=${1:-$(gcloud config get-value project)}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set. Usage: ./setup-gcs-key.sh [PROJECT_ID]"
    exit 1
fi

SERVICE_ACCOUNT_NAME="instago-gcs"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="instago-gcs-key.json"
SECRET_NAME="gcs-service-account-key"

echo "Setting up GCS service account for project: $PROJECT_ID"

# Create the service account if it doesn't exist
if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Creating service account..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Instago GCS Service Account" \
        --description="Service account for GCS access with signed URL capability" \
        --project=$PROJECT_ID
else
    echo "Service account already exists"
fi

# Grant necessary roles
echo "Granting Storage Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.admin" \
    --quiet

# Create a new key
echo "Creating service account key..."
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL \
    --project=$PROJECT_ID

# Store the key in Secret Manager
echo "Storing key in Secret Manager..."
if gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Updating existing secret..."
    gcloud secrets versions add $SECRET_NAME --data-file=$KEY_FILE --project=$PROJECT_ID
else
    echo "Creating new secret..."
    gcloud secrets create $SECRET_NAME --data-file=$KEY_FILE --project=$PROJECT_ID
fi

# Grant the Cloud Run service account access to this secret
CLOUD_RUN_SA="instago-server@$PROJECT_ID.iam.gserviceaccount.com"
echo "Granting access to Cloud Run service account..."
gcloud secrets add-iam-policy-binding $SECRET_NAME \
    --member="serviceAccount:$CLOUD_RUN_SA" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

# Clean up local key file
rm -f $KEY_FILE

echo ""
echo "Setup complete!"
echo "The GCS service account key has been stored in Secret Manager as: $SECRET_NAME"
echo ""
echo "Next steps:"
echo "1. Update your service.yaml to mount this secret"
echo "2. Set GOOGLE_APPLICATION_CREDENTIALS to point to the mounted file"
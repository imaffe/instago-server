#!/bin/bash

# Script to set up the service account for Instago Server on Cloud Run

PROJECT_ID=${1:-$(gcloud config get-value project)}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set. Usage: ./setup-service-account.sh [PROJECT_ID]"
    exit 1
fi

SERVICE_ACCOUNT_NAME="instago-server"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Setting up service account for project: $PROJECT_ID"
echo "Service account: $SERVICE_ACCOUNT_EMAIL"

# Create the service account if it doesn't exist
if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Creating service account..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Instago Server Cloud Run Service Account" \
        --description="Service account for Instago Server running on Cloud Run" \
        --project=$PROJECT_ID
else
    echo "Service account already exists"
fi

echo "Granting necessary roles to the service account..."

# Grant necessary roles
ROLES=(
    "roles/secretmanager.secretAccessor"    # Access secrets from Secret Manager
    "roles/storage.objectAdmin"             # Read/write to GCS buckets
    "roles/cloudtrace.agent"                # Send traces
    "roles/logging.logWriter"               # Write logs
    "roles/monitoring.metricWriter"         # Write metrics
)

for ROLE in "${ROLES[@]}"; do
    echo "Granting $ROLE..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$ROLE" \
        --quiet
done

# If using Vertex AI for Gemini
echo "Granting Vertex AI access..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/aiplatform.user" \
    --quiet

# Create and download a key for local testing (optional)
read -p "Do you want to create a service account key for local testing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    KEY_FILE="instago-server-sa-key.json"
    echo "Creating service account key..."
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=$SERVICE_ACCOUNT_EMAIL \
        --project=$PROJECT_ID
    
    echo "Service account key saved to: $KEY_FILE"
    echo "IMPORTANT: Keep this key secure and never commit it to version control!"
    echo "Add to .gitignore: echo '$KEY_FILE' >> .gitignore"
fi

echo ""
echo "Service account setup complete!"
echo ""
echo "To deploy Cloud Run with this service account, use:"
echo "gcloud run deploy instago-server \\"
echo "    --service-account=$SERVICE_ACCOUNT_EMAIL \\"
echo "    --region=us-central1 \\"
echo "    --image=gcr.io/$PROJECT_ID/instago-server:latest"
echo ""
echo "Or update your deploy.sh and cloudbuild.yaml to include:"
echo "    --service-account=$SERVICE_ACCOUNT_EMAIL"
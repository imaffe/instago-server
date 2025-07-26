#!/bin/bash

# Script to set up Google Cloud Secret Manager secrets for Instago Server

PROJECT_ID=${1:-$(gcloud config get-value project)}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set. Usage: ./setup-secrets.sh [PROJECT_ID]"
    exit 1
fi

echo "Setting up secrets for project: $PROJECT_ID"

# Function to create or update a secret
create_or_update_secret() {
    SECRET_NAME=$1
    SECRET_VALUE=$2
    
    # Check if secret exists
    if gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID >/dev/null 2>&1; then
        echo "Updating secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID
    else
        echo "Creating secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets create $SECRET_NAME --data-file=- --project=$PROJECT_ID
    fi
}

# Read .env file if it exists
if [ -f .env ]; then
    echo "Reading secrets from .env file..."
    
    # Parse .env file and create secrets
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        
        # Remove quotes from value
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"
        
        # Convert to lowercase and replace underscores with hyphens for secret names
        secret_name=$(echo "$key" | tr '[:upper:]' '[:lower:]' | tr '_' '-')
        
        # Create or update the secret
        case $key in
            SUPABASE_URL|SUPABASE_ANON_KEY|SUPABASE_SERVICE_KEY|SUPABASE_JWT_SECRET|\
            OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CUSTOM_SEARCH_API_KEY|\
            GOOGLE_CUSTOM_SEARCH_ENGINE_ID|GCS_BUCKET_NAME|MILVUS_HOST|DATABASE_URL|\
            MILVUS_TOKEN|OPENROUTER_API_KEY|VERTEX_AI_PROJECT)
                create_or_update_secret "$secret_name" "$value"
                ;;
        esac
    done < .env
else
    echo "No .env file found. Please create secrets manually or provide a .env file."
    echo "Required secrets:"
    echo "  - database-url"
    echo "  - supabase-url"
    echo "  - supabase-anon-key"
    echo "  - supabase-service-key"
    echo "  - supabase-jwt-secret"
    echo "  - openai-api-key"
    echo "  - anthropic-api-key"
    echo "  - google-custom-search-api-key"
    echo "  - google-custom-search-engine-id"
    echo "  - gcs-bucket-name"
    echo "  - milvus-host"
    echo "  - milvus-token"
    echo "  - openrouter-api-key (optional)"
    echo "  - vertex-ai-project (optional)"
fi

# Grant Cloud Run service account access to secrets
SERVICE_ACCOUNT="instago-server@$PROJECT_ID.iam.gserviceaccount.com"

echo "Granting secret access to service account: $SERVICE_ACCOUNT"

# Create service account if it doesn't exist
gcloud iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID >/dev/null 2>&1 || \
    gcloud iam service-accounts create instago-server --display-name="Instago Server Service Account" --project=$PROJECT_ID

# Grant secret accessor role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

# Grant storage access for GCS
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectAdmin"

echo "Setup complete!"
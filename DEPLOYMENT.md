# Instago Server - Google Cloud Run Deployment Guide

## Prerequisites

1. Google Cloud SDK installed and configured
2. Docker installed
3. A Google Cloud project with billing enabled
4. Required APIs enabled:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Secret Manager API

## Quick Deployment

### 1. Configure Google Cloud

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Set up Secrets

Create a `.env` file with your secrets, then run:

```bash
./setup-secrets.sh $PROJECT_ID
```

### 3. Deploy

#### Option A: Manual Deployment
```bash
./deploy.sh $PROJECT_ID
```

#### Option B: Cloud Build (CI/CD)
```bash
gcloud builds submit --config cloudbuild.yaml
```

#### Option C: Using Service Configuration
```bash
# Replace PROJECT_ID in service.yaml
sed -i "s/PROJECT_ID/$PROJECT_ID/g" service.yaml

# Deploy using the service configuration
gcloud run services replace service.yaml --region us-central1
```

## Environment Variables

The following secrets need to be configured in Google Secret Manager:

- `supabase-url`: Your Supabase project URL
- `supabase-anon-key`: Supabase anonymous key
- `supabase-service-key`: Supabase service role key
- `supabase-jwt-secret`: JWT secret for token validation
- `openai-api-key`: OpenAI API key
- `anthropic-api-key`: Anthropic API key
- `google-custom-search-api-key`: Google Custom Search API key
- `google-custom-search-engine-id`: Google Custom Search Engine ID
- `gcs-bucket-name`: Google Cloud Storage bucket name
- `milvus-host`: Milvus vector database host

## Service Configuration

The service is configured with:
- **Memory**: 2GB
- **CPU**: 2 vCPUs
- **Timeout**: 300 seconds
- **Max Instances**: 10
- **Concurrency**: 100 requests per instance

## Monitoring

View logs:
```bash
gcloud run services logs read instago-server --region us-central1
```

View service details:
```bash
gcloud run services describe instago-server --region us-central1
```

## Updating the Service

To update the service with a new image:

```bash
# Build and push new image
docker build -t gcr.io/$PROJECT_ID/instago-server:v2 .
docker push gcr.io/$PROJECT_ID/instago-server:v2

# Update the service
gcloud run deploy instago-server \
    --image gcr.io/$PROJECT_ID/instago-server:v2 \
    --region us-central1
```

## Rollback

To rollback to a previous revision:

```bash
# List revisions
gcloud run revisions list --service instago-server --region us-central1

# Rollback to a specific revision
gcloud run services update-traffic instago-server \
    --to-revisions=instago-server-00001-abc=100 \
    --region us-central1
```

## Troubleshooting

1. **Service fails to start**: Check logs with `gcloud run services logs read`
2. **Authentication errors**: Ensure all secrets are properly configured
3. **Timeout errors**: Increase timeout in service configuration
4. **Memory errors**: Increase memory allocation in service.yaml

## Security Notes

- The service runs as a non-root user for security
- All sensitive data is stored in Google Secret Manager
- The service account has minimal required permissions
- CORS is configured for production use
# Instago Server Development

## Overview
Instago is a Mac screenshot management tool that uses LLMs to understand and enrich screenshots. This document tracks the development progress and setup instructions.

## Tech Stack
- **API Framework**: FastAPI with Python 3.12
- **Authentication**: Supabase (JWT validation)
- **Database**: PostgreSQL (via Supabase)
- **Vector Store**: Milvus (for semantic search)
- **Storage**: Google Cloud Storage (for images)
- **AI Workflow**: OpenAI Agent SDK
- **Deployment**: Google Cloud Run

## Progress Tracking

### Completed
- [x] Created CLAUDE.md documentation
- [x] Set up project structure and dependencies
- [x] Configure Supabase authentication integration
- [x] Implement core FastAPI application with health check
- [x] Create database models for users, screenshots, and friends
- [x] Implement POST /screenshot endpoint with GCS upload
- [x] Set up OpenAI Agent SDK for AI workflow
- [x] Configure Milvus vector store integration
- [x] Implement semantic search with POST /query endpoint
- [x] Implement friend management endpoints
- [x] Implement screenshot management endpoints (GET, PUT, DELETE)
- [x] Create Docker configuration for Cloud Run deployment

All tasks completed!

## Setup Instructions

### Prerequisites
- Python 3.12
- Docker (for deployment)
- Google Cloud account with GCS access
- Supabase project
- Milvus instance
- OpenAI API key

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the server
uvicorn app.main:app --reload
```

### Environment Variables
```
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Google Cloud Storage
GCS_BUCKET_NAME=your_gcs_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Milvus
MILVUS_HOST=your_milvus_host
MILVUS_PORT=19530

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## API Endpoints

### Screenshot Operations
- `POST /screenshot` - Upload new screenshot and trigger AI processing
- `GET /screenshot-note` - Get all screenshot metadata for logged-in user
- `PUT /screenshot-note/{id}` - Update screenshot note/tag
- `DELETE /screenshot/{id}` - Delete screenshot

### Search
- `POST /query` - Semantic search using natural language

### Social Features
- `POST /friend-request` - Send friend request
- `PUT /friend-grant` - Accept friend request
- `GET /friends` - Get friend list
- `DELETE /friend/{id}` - Remove friend

## Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run linting
ruff check .
mypy app
```

## Deployment
```bash
# Build Docker image
docker build -t instago-server .

# Deploy to Cloud Run
gcloud run deploy instago-server \
  --image gcr.io/PROJECT_ID/instago-server \
  --platform managed \
  --region us-central1
```
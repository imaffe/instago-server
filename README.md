# Instago Server

Backend API server for Instago - a Mac screenshot management tool with AI-powered enrichment.

## Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Key Endpoints

- `POST /api/v1/screenshot` - Upload screenshot (used by Mac app)
- `POST /api/v1/query` - Semantic search screenshots
- `GET /api/v1/screenshot-note` - Get user's screenshots
- `PUT /api/v1/screenshot-note/{id}` - Update screenshot metadata
- `DELETE /api/v1/screenshot/{id}` - Delete screenshot
- `POST /api/v1/friend-request` - Send friend request
- `PUT /api/v1/friend-grant` - Accept friend request
- `GET /api/v1/friends` - Get friend list
- `DELETE /api/v1/friend/{id}` - Remove friend

## Required Services

- **Supabase**: Authentication and PostgreSQL database
- **Google Cloud Storage**: Image storage
- **Milvus**: Vector database for semantic search
- **OpenAI API**: AI processing for screenshots

## Deployment

Deploy to Google Cloud Run:
```bash
gcloud builds submit --config cloudbuild.yaml
```
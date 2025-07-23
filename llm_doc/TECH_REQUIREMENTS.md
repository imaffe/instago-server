Instago: Backend Implementation Plan
1. Project Overview
This document outlines the backend architecture, technology stack, and API design for the Instago application. The service is designed to be a scalable, modern backend that handles screenshot uploads, AI-based analysis and tagging, user management, and social features.

2. Technology Stack
The backend will be built using a modern, cloud-native technology stack designed for performance, scalability, and rapid development.

- Supabase: PG + UserAuth
- VectorStore: Zilliz Milvus
- Python Runtime: Google Cloud Run (Container Level)
- API Framework: FastAPI + python 3.12 + ThreadPoolExecutor for agent workflows.
- AI Agent workflow: OpenAI Agent SDK
- Blog Storage: GCS (Google Cloud Storage)

3. Backend Architecture
The system is architected around a core API service that interfaces with specialized cloud services for distinct functions.

API Service (FastAPI on Cloud Run): The central component that handles all client requests. It contains the business logic for all features. Long-running tasks like AI processing will be handled in a non-blocking fashion using ThreadPoolExecutor.

Authentication (Supabase): The FastAPI service will not handle passwords directly. Instead, it will validate JWTs issued by Supabase to secure its endpoints.

Data Storage:

Postgres (Supabase): Stores structured data like user info, screenshot notes/tags, and friend lists.

Google Cloud Storage: Stores the actual screenshot image files.

Milvus: Stores vector embeddings of screenshots for semantic search.

4. Core AI Workflow
The primary AI workflow for processing a new screenshot is as follows:

Upload: A client (e.g., the desktop app) sends a new screenshot to the POST /screenshot endpoint.

Storage: The backend immediately uploads the image to a private bucket in Google Cloud Storage.

AI Analysis: The image is passed to a workflow managed by the OpenAI Agent SDK. This agent will likely perform multi-modal analysis (e.g., OCR to extract text and vision models to understand context) to generate a highly accurate tag and description.

Database Entry: The resulting metadata (AI tag, image URL from GCS) is saved in the Postgres database, linked to the user's ID.

Vectorization: The screenshot is converted into a vector embedding and stored in Milvus to make it discoverable via semantic search.

5. API Endpoint Design
The API is designed to be RESTful and is categorized by function.

Create / Update Operations
POST /screenshot

Description: Uploads a new screenshot and triggers the AI processing workflow.

POST /query

Description: Initiates a semantic search against the Milvus vector store using a natural language query.

POST /friend-request

Description: Sends a friend request to another user.

PUT /friend-grant

Description: Accepts a pending friend request.

PUT /screenshot-note/{id}

Description: Updates the note or tag for a specific screenshot. Sending an empty value in the request body will "delete" the note while keeping the image.

Read Operations
GET /screenshot-note

Description: Retrieves a list of all screenshot metadata (tags, notes, URLs) for the logged-in user. Supports filtering.

GET /friends

Description: Retrieves the friend list for the logged-in user.

Delete Operations
DELETE /friend/{id}

Description: Removes a friend from the user's friend list.

DELETE /screenshot/{id}

Description: Permanently deletes a screenshot record from the database and its corresponding image file from Google Cloud Storage.

Auth Operations (Handled by Supabase)
/login

/logout

/delete-account
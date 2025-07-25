from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import api_router
from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import Base, engine
from app.models import Screenshot, Friendship, Query  # Import all models to register them

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Instago Server...")

    # Create all tables
    logger.info("Setting up database...")

    try:
        # Enable UUID extension if not already enabled
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()

        # Create tables if they don't exist
        # This will not recreate existing tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.warning(f"Database setup warning: {e}")
        logger.info("Continuing with existing database schema")

    yield
    logger.info("Shutting down Instago Server...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request details
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    logger.debug(f"Headers: {dict(request.headers)}")

    # Get authorization header
    auth_header = request.headers.get("authorization", "No auth header")
    logger.info(f"Auth header: {auth_header[:50]}..." if len(auth_header) > 50 else f"Auth header: {auth_header}")

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")

    return response


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

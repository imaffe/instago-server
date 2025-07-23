from fastapi import APIRouter

from app.api import screenshots, search, friends

api_router = APIRouter()

api_router.include_router(screenshots.router, tags=["screenshots"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(friends.router, tags=["friends"])
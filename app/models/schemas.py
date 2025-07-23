from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ScreenshotBase(BaseModel):
    user_note: Optional[str] = None


class ScreenshotCreate(BaseModel):
    pass


class ScreenshotUpdate(BaseModel):
    user_note: Optional[str] = None
    ai_tags: Optional[List[str]] = None


class ScreenshotResponse(ScreenshotBase):
    id: UUID
    user_id: UUID
    image_url: str
    thumbnail_url: Optional[str] = None
    ai_title: Optional[str] = None
    ai_description: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    markdown_content: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    width: Optional[float] = None
    height: Optional[float] = None
    file_size: Optional[float] = None

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    include_friends: bool = False
    limit: int = Field(default=20, ge=1, le=100)


class QueryResult(BaseModel):
    screenshot: ScreenshotResponse
    score: float
    friend_name: Optional[str] = None


class FriendRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)


class FriendshipResponse(BaseModel):
    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: str
    created_at: datetime
    requester_email: Optional[str] = None
    addressee_email: Optional[str] = None

    class Config:
        from_attributes = True


class FriendGrantRequest(BaseModel):
    friendship_id: UUID


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
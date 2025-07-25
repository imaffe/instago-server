from datetime import datetime
from typing import List, Optional, Dict, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ScreenshotBase(BaseModel):
    user_note: Optional[str] = None


class ScreenshotCreate(BaseModel):
    screenshotTimestamp: int  # Unix timestamp
    screenshotAppName: str  # Application name
    screenshotTags: str = Field(..., max_length=16)  # User tag, max 16 chars
    screenshotFileBlob: str  # Base64 encoded image


class ScreenshotUpdate(BaseModel):
    user_note: Optional[str] = None
    ai_tags: Optional[List[str]] = None


class ScreenshotResponse(ScreenshotBase):
    id: UUID
    user_id: UUID
    image_url: str
    process_status: str = "pending"
    thumbnail_url: Optional[str] = None
    ai_title: Optional[str] = None
    ai_description: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    markdown_content: Optional[str] = None
    quick_link: Optional[Dict[str, str]] = None  # {"type": "direct"|"search_str", "content": "..."}
    created_at: datetime
    updated_at: datetime
    width: Optional[float] = None
    height: Optional[float] = None
    file_size: Optional[float] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_db(cls, db_screenshot) -> "ScreenshotResponse":
        """Convert database model to Pydantic response model"""
        # Parse JSON ai_tags if present
        ai_tags = None
        if db_screenshot.ai_tags:
            import json
            try:
                ai_tags = json.loads(db_screenshot.ai_tags)
            except json.JSONDecodeError:
                ai_tags = []

        return cls(
            id=db_screenshot.id,
            user_id=db_screenshot.user_id,
            image_url=db_screenshot.image_url,
            process_status=db_screenshot.process_status,
            thumbnail_url=db_screenshot.thumbnail_url,
            ai_title=db_screenshot.ai_title,
            ai_description=db_screenshot.ai_description,
            ai_tags=ai_tags,
            markdown_content=db_screenshot.markdown_content,
            quick_link=db_screenshot.quick_link,  # JSON field is automatically handled
            user_note=db_screenshot.user_note,
            created_at=db_screenshot.created_at,
            updated_at=db_screenshot.updated_at,
            width=db_screenshot.width,
            height=db_screenshot.height,
            file_size=db_screenshot.file_size
        )


class ScreenshotDTO(BaseModel):
    """Data Transfer Object for screenshot data used in search/reranking operations"""
    id: str
    user_id: str
    ai_title: str = ""
    ai_description: str = ""
    markdown_content: str = ""
    ai_tags: List[str] = Field(default_factory=list)
    vector_score: float



class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=100)


class QueryResult(BaseModel):
    screenshot: ScreenshotResponse
    score: float


class RAGQueryResponse(BaseModel):
    """Response for RAG-enhanced query"""
    answer: str = Field(..., description="AI-generated answer based on retrieved screenshots")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the answer")
    sources_used: int = Field(..., ge=0, description="Number of screenshots used to generate answer")
    model_used: Optional[str] = Field(None, description="Model used for generation")
    results: List[QueryResult] = Field(..., description="Reranked screenshot results")
    total_results: int = Field(..., description="Total number of results found")


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


class QueryHistoryItem(BaseModel):
    id: UUID
    query_text: str
    results_count: int
    created_at: datetime

    class Config:
        from_attributes = True

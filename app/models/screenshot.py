from datetime import datetime, timezone
from typing import Optional, TypedDict, Literal
import uuid

from sqlalchemy import Text, Float, text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class QuickLinkDict(TypedDict):
    type: Literal["direct", "search_str"]
    content: str


class Screenshot(Base):
    __tablename__ = "screenshots"
    
    # Primary key with auto-generated UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    # Required fields
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    image_url: Mapped[str] = mapped_column(Text)
    
    # Optional fields
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array stored as text
    user_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    markdown_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vector_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Milvus vector ID
    quick_link: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # QuickLinkDict as JSON
    
    # Timestamps with timezone-aware defaults
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Numeric optional fields
    width: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    height: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    file_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # in bytes
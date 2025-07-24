from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import String, Text, Integer, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Query(Base):
    __tablename__ = "queries"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    # Required fields
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    query_text: Mapped[str] = mapped_column(Text)
    
    # Fields with defaults
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    include_friends: Mapped[int] = mapped_column(Integer, default=0)  # Boolean stored as int
    
    # Optional fields
    vector_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Milvus vector ID
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
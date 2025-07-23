from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Screenshot(Base):
    __tablename__ = "screenshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    
    ai_title = Column(String(200), nullable=True)
    ai_description = Column(Text, nullable=True)
    ai_tags = Column(Text, nullable=True)  # JSON array stored as text
    user_note = Column(Text, nullable=True)
    
    markdown_content = Column(Text, nullable=True)
    
    vector_id = Column(String(100), nullable=True)  # Milvus vector ID
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    file_size = Column(Float, nullable=True)  # in bytes
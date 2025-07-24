from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Query(Base):
    __tablename__ = "queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    query_text = Column(Text, nullable=False)
    results_count = Column(Integer, default=0)
    include_friends = Column(Integer, default=0)  # Boolean stored as int
    
    vector_id = Column(String(100), nullable=True)  # Milvus vector ID
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
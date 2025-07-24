from datetime import datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class FriendshipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Friendship(Base):
    __tablename__ = "friendships"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    # Foreign keys
    requester_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    addressee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    
    # Status with default
    status: Mapped[str] = mapped_column(
        String(20), 
        default=FriendshipStatus.PENDING
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        UniqueConstraint('requester_id', 'addressee_id', name='unique_friendship'),
    )
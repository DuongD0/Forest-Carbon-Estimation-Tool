import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.session import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = {"schema": "analytics"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(255), index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.users.id"), nullable=True) # Can be null for anonymous events
    details = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
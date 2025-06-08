from sqlalchemy import Column, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base

# Intermediate table for project bookmarks
project_bookmarks = Table(
    "project_bookmarks",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("user_mgmt.users.id"), primary_key=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("project_mgmt.projects.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    schema="user_mgmt"
) 
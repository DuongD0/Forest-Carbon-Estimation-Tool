import uuid
import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.session import Base
from app.models.shared import project_bookmarks

class ProjectType(str, enum.Enum):
    FORESTRY = "Forestry"

class ProjectStatus(str, enum.Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    REJECTED = "Rejected"

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "project_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.users.id"), nullable=False)
    ecosystem_id = Column(UUID(as_uuid=True), ForeignKey("carbon_mgmt.ecosystems.id"), nullable=True)
    location_geometry = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="projects")
    ecosystem = relationship("Ecosystem")
    carbon_credits = relationship("CarbonCredit", back_populates="project")
    bookmarked_by = relationship("User", secondary=project_bookmarks, back_populates="bookmarked_projects")
    imagery = relationship("Imagery", back_populates="project")

# project bookmarks table is in shared.py now 
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.session import Base
import enum

# Enum for Project Status
class ProjectStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "project_mgmt"}

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    owner_id = Column(Integer, ForeignKey("user_mgmt.users.user_id"), nullable=False)
    # Define location using PostGIS geometry (e.g., a bounding box or centroid)
    location_geometry = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User") # Relationship to the User model
    # Add relationships to other related entities like Forests, Imagery, Calculations later
    # forests = relationship("Forest", back_populates="project")
    # imagery = relationship("Imagery", back_populates="project")
    # calculations = relationship("Calculation", back_populates="project")

print("Project model defined.")


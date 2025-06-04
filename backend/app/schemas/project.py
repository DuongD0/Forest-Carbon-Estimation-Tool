from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from .user import User # Import User schema for owner details
from app.models.project import ProjectStatus # Import Enum

# Shared properties
class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = ProjectStatus.DRAFT
    # Represent geometry as GeoJSON structure for API
    location_geometry: Optional[Any] = None # e.g., { "type": "Polygon", "coordinates": [...] }

# Properties to receive via API on creation
class ProjectCreate(ProjectBase):
    owner_id: int # Must be provided on creation

# Properties to receive via API on update
class ProjectUpdate(ProjectBase):
    project_name: Optional[str] = Field(None, min_length=3, max_length=255)
    owner_id: Optional[int] = None # Allow changing owner?
    status: Optional[ProjectStatus] = None

# Properties shared by models stored in DB
class ProjectInDBBase(ProjectBase):
    project_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Project(ProjectInDBBase):
    owner: Optional[User] = None # Include owner details
    # Add lists of related entities later
    # forest_count: Optional[int] = None
    # imagery_count: Optional[int] = None
    # calculation_count: Optional[int] = None

# Properties stored in DB
class ProjectInDB(ProjectInDBBase):
    pass

print("Pydantic schemas for Project defined.")


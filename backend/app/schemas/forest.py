from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from .project import Project # Import Project schema for context
from app.models.forest import ForestTypeEnum # Import Enum

# Shared properties
class ForestBase(BaseModel):
    forest_name: str = Field(..., min_length=3, max_length=255)
    forest_type: ForestTypeEnum
    description: Optional[str] = None
    # Represent geometry as GeoJSON structure for API
    geometry: Any # e.g., { "type": "MultiPolygon", "coordinates": [...] }
    area_ha: Optional[float] = None # Area might be calculated or provided

# Properties to receive via API on creation
class ForestCreate(ForestBase):
    project_id: int # Must be provided on creation

# Properties to receive via API on update
class ForestUpdate(ForestBase):
    forest_name: Optional[str] = Field(None, min_length=3, max_length=255)
    forest_type: Optional[ForestTypeEnum] = None
    geometry: Optional[Any] = None
    area_ha: Optional[float] = None

# Properties shared by models stored in DB
class ForestInDBBase(ForestBase):
    forest_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Forest(ForestInDBBase):
    # project: Optional[Project] = None # Optionally include project details
    pass

# Properties stored in DB
class ForestInDB(ForestInDBBase):
    pass

print("Pydantic schemas for Forest defined.")


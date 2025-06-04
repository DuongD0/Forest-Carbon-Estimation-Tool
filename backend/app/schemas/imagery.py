from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .project import Project # Import Project schema for context
from .user import User # Import User schema for uploader
from app.models.imagery import ImagerySourceEnum, ImageryStatusEnum # Import Enums

# Shared properties
class ImageryBase(BaseModel):
    source: ImagerySourceEnum
    source_identifier: Optional[str] = Field(None, max_length=255)
    acquisition_date: datetime
    sensor_type: Optional[str] = Field(None, max_length=100)
    resolution_m: Optional[float] = None
    cloud_cover_percent: Optional[float] = Field(None, ge=0, le=100)
    file_path: str = Field(..., max_length=1024) # Path is essential
    file_format: Optional[str] = Field(None, max_length=50)
    crs: Optional[str] = Field(None, max_length=100)
    status: Optional[ImageryStatusEnum] = ImageryStatusEnum.RECEIVED
    processing_log: Optional[str] = None

# Properties to receive via API on creation
# Usually created via an upload endpoint which sets file_path, format, etc.
class ImageryCreate(ImageryBase):
    project_id: int
    uploaded_by_id: Optional[int] = None # Set based on authenticated user

# Properties to receive via API on update
# Typically status and processing_log are updated internally
class ImageryUpdate(BaseModel):
    source_identifier: Optional[str] = Field(None, max_length=255)
    acquisition_date: Optional[datetime] = None
    sensor_type: Optional[str] = Field(None, max_length=100)
    resolution_m: Optional[float] = None
    cloud_cover_percent: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[ImageryStatusEnum] = None
    processing_log: Optional[str] = None
    # Maybe allow updating CRS if georeferencing is done post-upload
    crs: Optional[str] = Field(None, max_length=100)

# Properties shared by models stored in DB
class ImageryInDBBase(ImageryBase):
    imagery_id: int
    project_id: int
    uploaded_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Imagery(ImageryInDBBase):
    # project: Optional[Project] = None # Optionally include project details
    uploaded_by: Optional[User] = None # Optionally include uploader details
    pass

# Properties stored in DB
class ImageryInDB(ImageryInDBBase):
    pass

print("Pydantic schemas for Imagery defined.")


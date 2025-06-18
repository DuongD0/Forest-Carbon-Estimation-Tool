import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.imagery import ImageryStatus, SatelliteType

# Base schemas
class ImageryMetadata(BaseModel):
    """Schema for imagery metadata"""
    satellite_type: Optional[SatelliteType] = None
    capture_date: Optional[datetime] = None
    resolution: Optional[float] = Field(None, description="Resolution in meters per pixel")
    cloud_cover: Optional[float] = Field(None, ge=0, le=100, description="Cloud cover percentage")
    coordinates_lat: Optional[float] = Field(None, ge=-90, le=90)
    coordinates_lng: Optional[float] = Field(None, ge=-180, le=180)
    bounding_box: Optional[Dict[str, float]] = Field(None, description="Bounding box coordinates")
    projection: Optional[str] = Field(None, description="Coordinate system/projection")
    spectral_bands: Optional[List[str]] = Field(None, description="Available spectral bands")
    notes: Optional[str] = None

class ImageryBase(BaseModel):
    """Base imagery schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[ImageryMetadata] = None

class ImageryCreate(ImageryBase):
    """Schema for creating imagery"""
    project_id: uuid.UUID
    file_name: str
    file_size: int = Field(..., gt=0)
    file_format: str

class ImageryUpdate(BaseModel):
    """Schema for updating imagery"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[ImageryMetadata] = None
    status: Optional[ImageryStatus] = None
    processing_log: Optional[str] = None
    notes: Optional[str] = None

class ImageryInDBBase(ImageryBase):
    """Base schema for imagery in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    project_id: uuid.UUID
    file_path: str
    file_name: str
    file_size: int
    file_format: str
    status: ImageryStatus
    
    # Metadata fields (flattened for database storage)
    satellite_type: Optional[SatelliteType] = None
    capture_date: Optional[datetime] = None
    resolution: Optional[float] = None
    cloud_cover: Optional[float] = None
    coordinates_lat: Optional[float] = None
    coordinates_lng: Optional[float] = None
    bounding_box: Optional[Dict[str, float]] = None
    projection: Optional[str] = None
    spectral_bands: Optional[List[str]] = None
    notes: Optional[str] = None
    
    processing_log: Optional[str] = None
    processing_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class Imagery(ImageryInDBBase):
    """Schema for returning imagery to client"""
    pass

class ImageryInDB(ImageryInDBBase):
    """Schema for imagery stored in database"""
    pass

class ImageryWithProcessingResults(Imagery):
    """Schema for imagery with processing results"""
    processing_results: List["ImageryProcessingResult"] = []

# Processing result schemas
class ProcessingResultBase(BaseModel):
    """Base processing result schema"""
    result_type: str
    result_data: Dict[str, Any]
    output_file_path: Optional[str] = None
    output_file_format: Optional[str] = None
    processing_algorithm: Optional[str] = None
    processing_parameters: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)

class ProcessingResultCreate(ProcessingResultBase):
    """Schema for creating processing result"""
    imagery_id: uuid.UUID

class ProcessingResultUpdate(BaseModel):
    """Schema for updating processing result"""
    result_data: Optional[Dict[str, Any]] = None
    output_file_path: Optional[str] = None
    output_file_format: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)

class ProcessingResultInDBBase(ProcessingResultBase):
    """Base schema for processing result in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    imagery_id: uuid.UUID
    created_at: datetime

class ImageryProcessingResult(ProcessingResultInDBBase):
    """Schema for returning processing result to client"""
    pass

class ProcessingResultInDB(ProcessingResultInDBBase):
    """Schema for processing result stored in database"""
    pass

# Upload schemas
class ImageryUploadResponse(BaseModel):
    """Response schema for imagery upload"""
    imagery_id: uuid.UUID
    message: str
    file_path: str
    status: ImageryStatus

class BatchImageryUploadResponse(BaseModel):
    """Response schema for batch imagery upload"""
    uploaded_count: int
    failed_count: int
    imagery_ids: List[uuid.UUID]
    failed_files: List[Dict[str, str]]  # filename and error message
    message: str

# Analysis schemas
class ImageryAnalysisRequest(BaseModel):
    """Schema for requesting imagery analysis"""
    analysis_type: str = Field(..., description="Type of analysis to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Analysis parameters")

class ImageryAnalysisResponse(BaseModel):
    """Schema for imagery analysis response"""
    imagery_id: uuid.UUID
    analysis_type: str
    result_id: uuid.UUID
    status: str
    message: str
    estimated_completion: Optional[datetime] = None
import uuid
import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class ImageryStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class SatelliteType(str, enum.Enum):
    LANDSAT_8 = "landsat-8"
    LANDSAT_9 = "landsat-9"
    SENTINEL_2 = "sentinel-2"
    MODIS = "modis"
    WORLDVIEW_2 = "worldview-2"
    WORLDVIEW_3 = "worldview-3"
    QUICKBIRD = "quickbird"
    IKONOS = "ikonos"
    SPOT_6 = "spot-6"
    SPOT_7 = "spot-7"
    PLANETSCOPE = "planetscope"
    RAPIDEYE = "rapideye"
    DRONE = "drone"
    AERIAL = "aerial"
    OTHER = "other"

class Imagery(Base):
    __tablename__ = "imagery"
    __table_args__ = {"schema": "project_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_mgmt.projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_format = Column(String(50), nullable=False)  # e.g., 'GeoTIFF', 'JPEG', 'PNG'
    
    # Imagery metadata
    satellite_type = Column(SQLEnum(SatelliteType), nullable=True)
    capture_date = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(Float, nullable=True)  # meters per pixel
    cloud_cover = Column(Float, nullable=True)  # percentage
    
    # Geographic information
    coordinates_lat = Column(Float, nullable=True)
    coordinates_lng = Column(Float, nullable=True)
    bounding_box = Column(JSON, nullable=True)  # {"north": float, "south": float, "east": float, "west": float}
    projection = Column(String(100), nullable=True)  # e.g., "WGS84 (EPSG:4326)"
    
    # Spectral bands information
    spectral_bands = Column(JSON, nullable=True)  # ["Red", "Green", "Blue", "NIR", ...]
    
    # Processing information
    status = Column(SQLEnum(ImageryStatus), default=ImageryStatus.UPLOADED, nullable=False)
    processing_log = Column(Text, nullable=True)
    processing_metadata = Column(JSON, nullable=True)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="imagery")
    processing_results = relationship("ImageryProcessingResult", back_populates="imagery")

class ImageryProcessingResult(Base):
    __tablename__ = "imagery_processing_results"
    __table_args__ = {"schema": "project_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imagery_id = Column(UUID(as_uuid=True), ForeignKey("project_mgmt.imagery.id"), nullable=False)
    
    # Processing result information
    result_type = Column(String(100), nullable=False)  # e.g., "forest_detection", "carbon_calculation", "ndvi"
    result_data = Column(JSON, nullable=False)  # Flexible JSON field for different result types
    
    # File outputs (if any)
    output_file_path = Column(String(500), nullable=True)
    output_file_format = Column(String(50), nullable=True)
    
    # Processing metadata
    processing_algorithm = Column(String(100), nullable=True)
    processing_parameters = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    imagery = relationship("Imagery", back_populates="processing_results")
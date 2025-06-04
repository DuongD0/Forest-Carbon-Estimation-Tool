from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

# Enum for Imagery Source
class ImagerySourceEnum(str, enum.Enum):
    SATELLITE = "Satellite"
    DRONE = "Drone"
    UPLOADED = "Uploaded"

# Enum for Imagery Status (e.g., for processing pipeline)
class ImageryStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    RECEIVED = "Received"
    VALIDATING = "Validating"
    PREPROCESSING = "Preprocessing"
    READY = "Ready"
    ERROR = "Error"

class Imagery(Base):
    __tablename__ = "imagery"
    __table_args__ = {"schema": "imagery_data"} # Assuming a dedicated schema

    imagery_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project_mgmt.projects.project_id"), nullable=False, index=True)
    
    source = Column(SQLEnum(ImagerySourceEnum), nullable=False)
    source_identifier = Column(String(255), nullable=True, index=True) # e.g., Sentinel Scene ID, Drone Flight ID, Filename
    acquisition_date = Column(DateTime(timezone=True), nullable=False, index=True)
    sensor_type = Column(String(100))
    resolution_m = Column(Float) # Spatial resolution in meters
    cloud_cover_percent = Column(Float)
    
    # Store path to the raw/processed file (e.g., S3 URI, local path)
    file_path = Column(String(1024), nullable=False)
    file_format = Column(String(50)) # e.g., GeoTIFF, JPEG2000
    crs = Column(String(100)) # Coordinate Reference System (e.g., EPSG:4326)
    
    status = Column(SQLEnum(ImageryStatusEnum), default=ImageryStatusEnum.RECEIVED, nullable=False)
    processing_log = Column(Text) # Log messages during validation/processing
    
    uploaded_by_id = Column(Integer, ForeignKey("user_mgmt.users.user_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project") # Relationship back to the Project model
    uploaded_by = relationship("User") # Relationship to the User who uploaded (if applicable)

print("Imagery model defined.")


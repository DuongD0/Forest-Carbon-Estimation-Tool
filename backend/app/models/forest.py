from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.session import Base
import enum

# Enum for Forest Type (as defined in requirements)
class ForestTypeEnum(str, enum.Enum):
    TROPICAL_EVERGREEN = "Tropical evergreen"
    DECIDUOUS = "Deciduous"
    MANGROVE = "Mangrove"
    BAMBOO = "Bamboo"
    OTHER = "Other" # Add an other category if needed

class Forest(Base):
    __tablename__ = "forests"
    __table_args__ = {"schema": "forest_data"} # Assuming a dedicated schema

    forest_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project_mgmt.projects.project_id"), nullable=False, index=True)
    forest_name = Column(String(255), nullable=False, index=True)
    forest_type = Column(SQLEnum(ForestTypeEnum), nullable=False)
    description = Column(Text)
    
    # Store the authoritative geometry in a suitable projected CRS or geographic CRS (e.g., 4326)
    # SRID 4326 corresponds to WGS 84
    geometry = Column(Geometry(geometry_type=\"MULTIPOLYGON\", srid=4326), nullable=False)
    
    # Area in hectares, potentially calculated on save or via trigger/job
    area_ha = Column(Float, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project") # Relationship back to the Project model
    # Add relationships to calculations, etc. later

print("Forest model defined.")


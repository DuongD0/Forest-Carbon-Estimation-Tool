# Models for Forest Boundaries (formerly Forest)

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum as SQLEnum, Numeric
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
    OTHER = "Other"

class Forest(Base):
    __tablename__ = "forest_boundaries"
    # Aligning schema with the enhanced design
    __table_args__ = {"schema": "spatial"}

    forest_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project_mgmt.projects.project_id"), nullable=False, index=True)
    forest_name = Column(String(100), nullable=True) # Adjusted length based on schema
    forest_type = Column(String(50)) # Using String based on schema, consider Enum if preferred
    # forest_type = Column(SQLEnum(ForestTypeEnum), nullable=False) # Keep Enum if strongly preferred
    description = Column(Text) # Added description field if needed

    # Store the authoritative geometry in a suitable projected CRS or geographic CRS (e.g., 4326)
    # SRID 4326 corresponds to WGS 84
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)

    # Area in hectares, potentially calculated on save or via trigger/job
    area_ha = Column(Numeric(12, 2), nullable=True) # Changed to Numeric based on schema

    valid_from = Column(DateTime(timezone=True), server_default=func.now()) # Added from schema
    valid_to = Column(DateTime(timezone=True), nullable=True) # Added from schema
    created_by = Column(Integer, ForeignKey("user_mgmt.users.user_id")) # Added from schema
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) # Added for consistency
    source = Column(String(100)) # Added from schema
    source_date = Column(DateTime(timezone=True)) # Changed to DateTime based on schema

    # Relationships
    project = relationship("Project") # Relationship back to the Project model
    creator = relationship("User") # Relationship to the User model

    # Add relationship to ForestPlot (one-to-many)
    plots = relationship("ForestPlot", back_populates="forest", cascade="all, delete-orphan")

    # Add relationships to calculation results (one-to-many)
    biomass_calculations = relationship("Biomass", back_populates="forest")
    carbon_stock_calculations = relationship("CarbonStock", back_populates="forest")
    baseline_calculations = relationship("Baseline", back_populates="forest")
    carbon_credit_calculations = relationship("CarbonCredit", back_populates="forest")

print("Forest model defined.")


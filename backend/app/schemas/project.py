from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
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

# Schemas for Calculation Results
class BiomassSummary(BaseModel):
    agb_tonnes: float
    bgb_tonnes: float
    total_biomass_tonnes: float

class CarbonStockResult(BaseModel):
    forest_id: int
    agb_carbon_tonnes: float
    bgb_carbon_tonnes: float
    total_carbon_tonnes: float
    total_co2e_tonnes: float

class CarbonCreditResult(BaseModel):
    # forest_id: int # This is now part of the parent ForestCalculationResult
    gross_credits_co2e: float
    net_credits_co2e: float
    issuable_credits_co2e: float
    leakage_deduction_co2e: float
    permanence_buffer_co2e: float

class CalculationResultData(BaseModel):
    # project_id: int # This is now part of the parent ProjectCalculationResult
    current_biomass: BiomassSummary
    current_carbon_stock: CarbonStockResult
    carbon_credits: CarbonCreditResult
    # The baseline might be simple for now
    baseline_stock: Dict[str, Any]

class ForestCalculationResult(BaseModel):
    forest_id: int
    current_stock: CarbonStockResult
    baseline_stock: Dict[str, Any]
    carbon_credits: CarbonCreditResult
    error: Optional[str] = None

class ProjectCalculationResult(BaseModel):
    project_id: int
    # calculation_results: CalculationResultData # Old schema
    forest_calculations: List[ForestCalculationResult]

# New schemas for asynchronous calculation tasks
class CalculationStatus(BaseModel):
    forest_id: int
    status: str
    credit_id: Optional[int] = None
    error: Optional[str] = None

class ProjectCalculationResponse(BaseModel):
    project_id: int
    status: str
    message: str
    results: Optional[List[CalculationStatus]] = None

print("Pydantic schemas for Project defined.")


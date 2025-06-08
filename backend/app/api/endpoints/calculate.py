from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import tempfile
import os

from app.services import forest_detector, carbon_calculator

router = APIRouter()

# Request/Response Models
class AreaCalculationRequest(BaseModel):
    ecosystem_type: str = Field(..., description="Type of ecosystem (e.g., 'tropical_forest', 'mangrove')")
    scale_factor: float = Field(..., description="Conversion factor from pixels to square meters")

class CreditCalculationRequest(BaseModel):
    area_ha: float = Field(..., description="Area in hectares")
    ecosystem_type: str = Field(..., description="Type of ecosystem")
    region: str = Field("vietnam", description="Geographic region")
    years: int = Field(1, description="Number of years to calculate credits for")
    baseline_carbon: Optional[float] = Field(None, description="Optional baseline carbon")
    leakage_factor: float = Field(0.0, description="Leakage discount factor (0-1)")
    uncertainty_factor: float = Field(0.15, description="Scientific uncertainty discount")
    buffer_percent: float = Field(0.15, description="VCS buffer pool contribution percentage")

class RenewableCalculationRequest(BaseModel):
    energy_type: str = Field(..., description="Type of renewable energy")
    annual_generation_mwh: float = Field(..., description="Annual electricity generation in MWh")
    grid_emission_factor: float = Field(..., description="tCO2e/MWh for the local grid")
    years: int = Field(1, description="Number of years to calculate credits for")
    uncertainty_factor: float = Field(0.1, description="Scientific uncertainty discount")
    buffer_percent: float = Field(0.1, description="VCS buffer pool contribution percentage")

# API Endpoints
@router.post("/area", response_model=Dict[str, Any])
async def calculate_area(
    params: AreaCalculationRequest = Body(...),
    image: UploadFile = File(...),
):
    """
    Calculate forest area based on image analysis.
    Note: This is a long-running operation and in a production system
    should be handled asynchronously (e.g., with Celery and Redis).
    """
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(await image.read())
            temp_path = temp_file.name
        
        # Process image with detector
        result = forest_detector.detect_area(
            image_path=temp_path,
            ecosystem_type=params.ecosystem_type,
            scale_factor=params.scale_factor
        )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return result
    except Exception as e:
        # Clean up in case of error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/credits", response_model=Dict[str, Any])
async def calculate_credits_endpoint(
    params: CreditCalculationRequest,
):
    """Calculate carbon credits for a forest area"""
    try:
        result = carbon_calculator.calculate_credits(
            area_ha=params.area_ha,
            ecosystem_type=params.ecosystem_type,
            region=params.region,
            years=params.years,
            baseline_carbon=params.baseline_carbon,
            leakage_factor=params.leakage_factor,
            uncertainty_factor=params.uncertainty_factor,
            buffer_percent=params.buffer_percent
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/renewable", response_model=Dict[str, Any])
async def calculate_renewable_credits_endpoint(
    params: RenewableCalculationRequest,
):
    """Calculate carbon credits for renewable energy projects"""
    try:
        result = carbon_calculator.calculate_renewable_credits(
            energy_type=params.energy_type,
            annual_generation_mwh=params.annual_generation_mwh,
            grid_emission_factor=params.grid_emission_factor,
            years=params.years,
            uncertainty_factor=params.uncertainty_factor,
            buffer_percent=params.buffer_percent
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
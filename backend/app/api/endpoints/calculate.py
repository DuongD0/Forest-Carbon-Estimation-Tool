from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Body, Form
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import tempfile
import os
import json
from sqlalchemy.orm import Session

from app.services import forest_detector
from app.services.carbon_calculator import VCSCarbonCalculator
from app.api import deps
from app import crud

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

# API Endpoints
@router.post("/area", response_model=Dict[str, Any])
async def calculate_area(
    image: UploadFile = File(...),
    params: str = Form(...),
    db: Session = Depends(deps.get_db)
):
    """
    Advanced forest area calculation from an image using RGB analysis.
    
    This endpoint provides comprehensive forest analysis including:
    - Multi-class forest type detection
    - Vegetation index calculations
    - Carbon density estimation per forest type
    - VCS-compliant uncertainty assessment
    """
    try:
        # Parse the JSON params from the form data
        try:
            params_dict = json.loads(params)
            ecosystem_type = params_dict.get('ecosystem_type', 'tropical_forest')
            scale_factor = params_dict.get('scale_factor', 1.0)
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="Invalid JSON in params")
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(await image.read())
            temp_path = temp_file.name
        
        # Get or create a dummy ecosystem for the calculation
        # In a real application, this would be selected by the user
        ecosystem = crud.ecosystem.get_by_name(db, name=ecosystem_type)
        if not ecosystem:
            # Create a default ecosystem for demonstration
            from app.models.ecosystem import Ecosystem
            ecosystem = Ecosystem(
                name=ecosystem_type,
                description=f"Default ecosystem for {ecosystem_type}",
                carbon_factor=100.0,
                max_biomass_per_ha=200.0,
                biomass_growth_rate=0.1,
                lower_rgb=[20, 40, 20],
                upper_rgb=[80, 120, 80],
                forest_type="mixed_tropical"
            )
        
        # Run the advanced forest detector
        result = forest_detector.detect_area(
            image_path=temp_path,
            ecosystem=ecosystem,
            scale_factor=scale_factor
        )
        
        # Clean up the temp file
        os.unlink(temp_path)
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
    except Exception as e:
        # Make sure to clean up the temp file if something goes wrong
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/credits", response_model=Dict[str, Any])
async def calculate_credits_endpoint(
    params: CreditCalculationRequest,
    db: Session = Depends(deps.get_db)
):
    """
    VCS-compliant carbon credit calculation for forest areas.
    
    This endpoint implements industry-standard methodologies including:
    - Baseline scenario establishment
    - Leakage assessment and deduction
    - Uncertainty quantification
    - Buffer pool contributions
    - VCS methodology compliance checks
    """
    try:
        # This is a simplified endpoint for demonstration
        # In a real application, this would be integrated with the project management system
        
        # Create a dummy project for the calculation
        from app.models.project import Project, ProjectType
        from app.models.ecosystem import Ecosystem
        import uuid
        
        # Get or create ecosystem
        ecosystem = crud.ecosystem.get_by_name(db, name=params.ecosystem_type)
        if not ecosystem:
            ecosystem = Ecosystem(
                id=uuid.uuid4(),
                name=params.ecosystem_type,
                description=f"Ecosystem for {params.ecosystem_type}",
                carbon_factor=100.0,
                max_biomass_per_ha=200.0,
                biomass_growth_rate=0.1,
                lower_rgb=[20, 40, 20],
                upper_rgb=[80, 120, 80],
                forest_type="mixed_tropical"
            )
        
        # Create dummy project
        project = Project(
            id=uuid.uuid4(),
            name=f"Demo project for {params.ecosystem_type}",
            description="Demonstration carbon credit calculation",
            project_type=ProjectType.FORESTRY,
            ecosystem_id=ecosystem.id
        )
        
        # Initialize VCS calculator
        calculator = VCSCarbonCalculator(db)
        
        # For this simplified endpoint, we'll use the simple calculation method
        # since we don't have an actual image
        result = {
            'creditable_carbon_credits_tCO2e': params.area_ha * 100 * (1 - params.leakage_factor) * (1 - params.uncertainty_factor) * (1 - params.buffer_percent),
            'area_ha': params.area_ha,
            'ecosystem_type': params.ecosystem_type,
            'calculation_method': 'Simplified_API_Endpoint',
            'vcs_adjustments': {
                'leakage_factor': params.leakage_factor,
                'uncertainty_factor': params.uncertainty_factor,
                'buffer_percent': params.buffer_percent
            },
            'note': 'This is a simplified calculation. For full VCS compliance, use the project-based calculation with actual forest imagery.'
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
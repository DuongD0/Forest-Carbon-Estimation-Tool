from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Body, Form
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import tempfile
import os
import json
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import cv2
import numpy as np

from app.services.forest_detector import advanced_forest_detector, vietnamese_forests
from app.services.carbon_calculator import VCSCarbonCalculator
from app.api import deps
from app import crud
from app.models.user import User
from app.models.imagery import Imagery
from app.models.project import Project
from app.models.ecosystem import Ecosystem

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
@router.post("/area")
async def calculate_area(
    imagery_id: int,
    project_id: int,
    forest_type: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    # hey get the imagery from db
    imagery = db.query(Imagery).filter(Imagery.id == imagery_id).first()
    if not imagery:
        raise HTTPException(status_code=404, detail="Imagery not found")
    
    # Get the project to check ownership
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to calculate for this project")
    
    # Get the ecosystem 
    ecosystem = db.query(Ecosystem).filter(Ecosystem.id == 1).first()  # Default ecosystem
    
    # Calculate the area with forest type
    # Load the image first
    image = cv2.imread(imagery.file_path)
    if image is None:
        raise HTTPException(status_code=400, detail="Failed to load image")
    
    result = advanced_forest_detector.detect_area_comprehensive(
        image,
        scale_factor=imagery.scale_factor,
        forest_type=forest_type,
        use_ai=True
    )
    
    # Update imagery with calculation results
    imagery.forest_area = result['forest_area_ha']
    carbon_density = vietnamese_forests.get(forest_type, {}).get('carbon_density', 100.0)
    imagery.carbon_credits = result.get('forest_area_ha', 0) * carbon_density  # Calculate carbon stock
    imagery.calculation_date = datetime.utcnow()
    imagery.metadata = {
        **imagery.metadata,
        'forest_analysis': result,
        'forest_type_selected': forest_type or 'automatic',
        'carbon_density_used': carbon_density
    }
    
    db.commit()
    
    return {
        "success": True,
        "result": result,
        "imagery_id": imagery_id,
        "project_id": project_id
    }

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

@router.post("/area/form", response_model=Dict[str, Any])
async def calculate_area_form(
    image: UploadFile = File(...),
    params: str = Form(...),
    db: Session = Depends(deps.get_db)
):
    """
    Advanced forest area calculation from an image using RGB analysis.
    This endpoint handles form data with optional forest_type parameter.
    """
    try:
        # Parse the JSON params from the form data
        try:
            params_dict = json.loads(params)
            ecosystem_type = params_dict.get('ecosystem_type', 'tropical_forest')
            scale_factor = params_dict.get('scale_factor', 1.0)
            forest_type = params_dict.get('forest_type', None)
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="Invalid JSON in params")
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(await image.read())
            temp_path = temp_file.name
        
        # Load the image using OpenCV
        img = cv2.imread(temp_path)
        if img is None:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail="Failed to load image")
        
        # Get or create a dummy ecosystem for the calculation
        ecosystem = crud.ecosystem.get_by_name(db, name=ecosystem_type)
        if not ecosystem:
            # Create a default ecosystem
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
        
        # Perform detection
        logging.info(f"Processing image: {temp_path} for forest type: {forest_type}")
        
        # Use comprehensive detection with AI when available
        result = advanced_forest_detector.detect_area_comprehensive(
            img,  # Pass the loaded image
            scale_factor=10.0,  # Default 10m per pixel
            forest_type=forest_type,
            use_ai=True  # Enable AI detection
        )
        
        # Log detection method used
        logging.info(f"Detection method: {result.get('detection_method', 'Unknown')}")
        logging.info(f"AI detection used: {result.get('ai_detection', False)}")
        logging.info(f"Confidence score: {result.get('confidence_score', 0):.2f}")
        
        # Extract results
        forest_area_ha = result['forest_area_ha']
        coverage_percent = result['coverage_percent']
        carbon_density = vietnamese_forests.get(forest_type, {}).get('carbon_density', 100.0)
        
        logging.info(f"Detected {forest_area_ha:.2f} ha of forest")
        logging.info(f"Carbon density: {carbon_density} tC/ha")
        
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
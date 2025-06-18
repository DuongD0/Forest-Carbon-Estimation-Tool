from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile, Query
from sqlalchemy.orm import Session
from shapely.geometry import shape
import numpy as np
import cv2
import zipfile
import io
import geopandas as gpd
import tempfile
import os

from app import crud, models, schemas
from app.api import deps
from app.services.carbon_calculator import VCSCarbonCalculator
from app.services.serial_generator import serial_generator

router = APIRouter()

@router.get("/", response_model=List[schemas.Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    project_type: Optional[str] = Query(None),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    get my projects
    """
    projects = crud.project.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit, project_type=project_type
    )
    return projects

@router.post("/", response_model=schemas.Project)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: schemas.ProjectCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    create a new project
    """
    project = crud.project.create_with_owner(db=db, obj_in=project_in, owner_id=current_user.id)
    return project

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    get a project by its id
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    project_in: schemas.ProjectUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    update a project
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    project = crud.project.update(db=db, db_obj=project, obj_in=project_in)
    return project

@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    delete a project
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    project = crud.project.remove(db=db, id=project_id)
    return project

@router.put("/{project_id}/geometry", response_model=schemas.Project)
def set_project_geometry(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    geometry: schemas.GeoJSON,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    set or update the project's geometry
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Convert GeoJSON to WKT for GeoAlchemy2
    geom = shape(geometry.dict())
    project.location_geometry = geom.wkt
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.post("/{project_id}/calculate_carbon", response_model=float)
async def calculate_carbon(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_user),
    image: UploadFile = File(...),
) -> Any:
    """
    calculates the carbon stock for a project from an image i upload.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Read the uploaded image file into a NumPy array
    contents = await image.read()
    nparr = np.fromstring(contents, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    calculator = VCSCarbonCalculator(db=db)
    try:
        # Save image to temporary file for processing
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            cv2.imwrite(temp_file.name, img_np)
            
            # Calculate carbon credits using the VCS methodology
            result = calculator.calculate_credits(
                project=project,
                image_path=temp_file.name,
                image_scale_factor=1.0,  # Assume 1 meter per pixel for now
                project_age_years=1,     # Assume 1 year old project
                use_vcs_methodology=True
            )
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            carbon_stock = result.get('creditable_carbon_credits_tCO2e', 0.0)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return carbon_stock

@router.put("/{project_id}/shapefile", response_model=schemas.Project)
async def upload_shapefile(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    """
    upload a shapefile zip to define project geometry.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    try:
        with zipfile.ZipFile(io.BytesIO(await file.read()), 'r') as zip_ref:
            # Find the .shp file in the zip
            shp_name = next((name for name in zip_ref.namelist() if name.endswith('.shp')), None)
            if not shp_name:
                raise HTTPException(status_code=400, detail="No .shp file found in the zip archive")
            
            gdf = gpd.read_file(f"/vsizip/{file.filename}/{shp_name}", vfs=f"zip://{file.filename}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading shapefile: {e}")

    if gdf.empty:
        raise HTTPException(status_code=400, detail="Shapefile contains no geometries")
    
    # We'll take the first geometry from the shapefile
    geom = gdf.geometry.iloc[0]

    # Update project geometry
    project.location_geometry = geom.wkt
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project

@router.post("/{project_id}/issue-credits", response_model=schemas.CarbonCredit)
def issue_carbon_credits(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    issuance_request: schemas.CreditIssuanceRequest,
    current_user: models.User = Security(deps.get_current_user, scopes=["manage:credits"]),
) -> Any:
    """
    issue new carbon credits for a project (admins only)
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure the project_id in the path matches the one in the body
    if str(issuance_request.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    # Generate the serial number
    serial_number = serial_generator.generate_serial(
        project_id=project.id,
        vintage_year=issuance_request.vintage_year,
        batch_size=float(issuance_request.quantity_co2e),
        sequential_number=1  # This should be retrieved from database
    )

    # Create the credit object
    credit_in = schemas.CarbonCreditCreate(
        **issuance_request.dict(),
        vcs_serial_number=serial_number
    )

    credit = crud.carbon_credit.create(db=db, obj_in=credit_in)
    return credit 
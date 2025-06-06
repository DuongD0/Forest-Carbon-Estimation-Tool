from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Any, Optional
import shutil
import os
from datetime import datetime
import logging

from app import schemas, crud, models
from app.api import deps
from app.processing.image_processor import ImageProcessor

UPLOAD_DIR = "backend/uploads/imagery"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()
logger = logging.getLogger(__name__)

# Note: Imagery endpoints are typically nested under projects, e.g., /projects/{project_id}/imagery/
# For simplicity here, we use a top-level /imagery/ endpoint, but nesting is recommended.

# Endpoint to upload imagery file and create metadata record
@router.post("/upload/", response_model=schemas.Imagery, status_code=status.HTTP_201_CREATED)
def upload_imagery(
    *, 
    db: Session = Depends(deps.get_db),
    project_id: int = Form(...),
    source: models.imagery.ImagerySourceEnum = Form(models.imagery.ImagerySourceEnum.UPLOADED),
    acquisition_date: datetime = Form(...),
    sensor_type: Optional[str] = Form(None),
    resolution_m: Optional[float] = Form(None),
    cloud_cover_percent: Optional[float] = Form(None),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload an imagery file and create its metadata record.
    """
    project = crud.project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to upload imagery to this project")

    file_location = os.path.join(UPLOAD_DIR, f"project_{project_id}_{file.filename}")

    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    finally:
        file.file.close()

    # TODO: Add logic here to extract metadata (CRS, format) from the file itself (e.g., using rasterio/gdal)
    # For now, we rely on user input or defaults
    file_format = file.content_type # Or extract from file extension/content
    crs = "EPSG:4326" # Placeholder - should be extracted

    # Create the metadata record in the database
    imagery_in = schemas.ImageryCreate(
        project_id=project_id,
        source=source,
        source_identifier=file.filename,
        acquisition_date=acquisition_date,
        sensor_type=sensor_type,
        resolution_m=resolution_m,
        cloud_cover_percent=cloud_cover_percent,
        file_path=file_location,
        file_format=file_format,
        crs=crs,
        status=models.imagery.ImageryStatusEnum.RECEIVED, # Initial status
        uploaded_by_id=current_user.user_id
    )

    try:
        db_imagery = crud.imagery.create_imagery(db=db, imagery=imagery_in)
    except Exception as e:
        # Clean up saved file if DB insertion fails
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Could not create imagery record: {e}")

    return db_imagery

@router.get("/", response_model=List[schemas.Imagery])
def read_imagery_list(
    db: Session = Depends(deps.get_db),
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve imagery records for a specific project.
    """
    if not project_id:
        raise HTTPException(status_code=400, detail="Project ID must be provided to list imagery")
        
    project = crud.project.get_project(db, project_id=project_id)
    if not project:
         raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to view imagery for this project")

    imagery_list = crud.imagery.get_imagery_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return imagery_list

@router.get("/{imagery_id}", response_model=schemas.Imagery)
def read_imagery_by_id(
    imagery_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific imagery record by id.
    """
    imagery = crud.imagery.get_imagery(db, imagery_id=imagery_id)
    if not imagery:
        raise HTTPException(status_code=404, detail="Imagery not found")
    
    project = crud.project.get_project(db, project_id=imagery.project_id)
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to view this imagery")

    return imagery

@router.put("/{imagery_id}", response_model=schemas.Imagery)
def update_imagery_metadata(
    *,
    db: Session = Depends(deps.get_db),
    imagery_id: int,
    imagery_in: schemas.ImageryUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update imagery metadata.
    """
    db_imagery = crud.imagery.get_imagery(db, imagery_id=imagery_id)
    if not db_imagery:
        raise HTTPException(
            status_code=404,
            detail="The imagery with this id does not exist in the system",
        )
    
    project = crud.project.get_project(db, project_id=db_imagery.project_id)
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to update this imagery")
    
    updated_imagery = crud.imagery.update_imagery(db=db, db_imagery=db_imagery, imagery_in=imagery_in)
    return updated_imagery

@router.delete("/{imagery_id}", response_model=schemas.Imagery)
def delete_imagery_record(
    *,
    db: Session = Depends(deps.get_db),
    imagery_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an imagery record.
    """
    imagery = crud.imagery.get_imagery(db=db, imagery_id=imagery_id)
    if not imagery:
        raise HTTPException(status_code=404, detail="Imagery not found")
        
    project = crud.project.get_project(db, project_id=imagery.project_id)
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this imagery")
    
    deleted_imagery = crud.imagery.delete_imagery(db=db, imagery_id=imagery_id)
    return deleted_imagery

@router.post("/{imagery_id}/process", status_code=status.HTTP_202_ACCEPTED)
def process_imagery(
    *,
    db: Session = Depends(deps.get_db),
    imagery_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Triggers the full processing pipeline for a specific imagery record.
    """
    db_imagery = crud.imagery.get_imagery(db, imagery_id=imagery_id)
    if not db_imagery:
        raise HTTPException(
            status_code=404,
            detail="The imagery with this id does not exist in the system",
        )
        
    project = crud.project.get_project(db, project_id=db_imagery.project_id)
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to process this imagery")

    try:
        processor = ImageProcessor(imagery_record=db_imagery, db_session=db)
        success = processor.process()
        if success:
            return {"message": "Image processing started successfully."}
        else:
            raise HTTPException(
                status_code=500,
                detail="Image processing failed. Check server logs for details."
            )
    except Exception as e:
        logger.error(f"Error starting image processing for {imagery_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred while starting the processing job: {e}"
        )

print("API endpoints for Imagery defined.")


from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Any, Optional
import shutil
import os

from app import schemas, crud, models
from app.db.session import get_db
# Import dependency for authentication/authorization later
# from app.api import deps

# Define a directory for uploads (consider making this configurable)
UPLOAD_DIR = "/home/ubuntu/uploads/imagery"
# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

# Note: Imagery endpoints are typically nested under projects, e.g., /projects/{project_id}/imagery/
# For simplicity here, we use a top-level /imagery/ endpoint, but nesting is recommended.

# Endpoint to upload imagery file and create metadata record
@router.post("/upload/", response_model=schemas.Imagery, status_code=status.HTTP_201_CREATED)
def upload_imagery(
    *, 
    db: Session = Depends(get_db),
    project_id: int = Form(...),
    source: models.ImagerySourceEnum = Form(models.ImagerySourceEnum.UPLOADED),
    acquisition_date: datetime = Form(...),
    sensor_type: Optional[str] = Form(None),
    resolution_m: Optional[float] = Form(None),
    cloud_cover_percent: Optional[float] = Form(None),
    file: UploadFile = File(...),
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Upload an imagery file and create its metadata record.
    (Requires user to have write access to the project - to be added later)
    """
    # Check if project exists
    project = crud.project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    # Add authorization check: does current_user have access to this project?
    # Placeholder: Use user_id 1 until auth is implemented
    uploader_id = 1 # Replace with current_user.user_id later

    # Define file path
    file_location = os.path.join(UPLOAD_DIR, f"project_{project_id}_{file.filename}")

    # Save the uploaded file
    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        # Clean up partially saved file if error occurs
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
        status=models.ImageryStatusEnum.RECEIVED, # Initial status
        uploaded_by_id=uploader_id
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
    db: Session = Depends(get_db),
    project_id: Optional[int] = None, # Allow filtering by project_id
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Retrieve imagery records, optionally filtered by project.
    (Requires user to have read access - to be added later)
    """
    if project_id:
        # Check if project exists and user has access
        project = crud.project.get_project(db, project_id=project_id)
        if not project:
             raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
        # Add authorization check here
        imagery_list = crud.imagery.get_imagery_by_project(db, project_id=project_id, skip=skip, limit=limit)
    else:
        # Retrieving ALL imagery might need admin privileges
         raise HTTPException(status_code=400, detail="Project ID must be provided to list imagery")
    
    return imagery_list

@router.get("/{imagery_id}", response_model=schemas.Imagery)
def read_imagery_by_id(
    imagery_id: int,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Get a specific imagery record by id.
    (Requires user to have access to the imagery/project - to be added later)
    """
    imagery = crud.imagery.get_imagery(db, imagery_id=imagery_id)
    if not imagery:
        raise HTTPException(status_code=404, detail="Imagery not found")
    
    # Add authorization check here (e.g., check project access)
    return imagery

@router.put("/{imagery_id}", response_model=schemas.Imagery)
def update_imagery_metadata(
    *,
    db: Session = Depends(get_db),
    imagery_id: int,
    imagery_in: schemas.ImageryUpdate,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Update imagery metadata (e.g., status, processing log).
    (Requires user to have write access - to be added later)
    """
    db_imagery = crud.imagery.get_imagery(db, imagery_id=imagery_id)
    if not db_imagery:
        raise HTTPException(
            status_code=404,
            detail="The imagery with this id does not exist in the system",
        )
    
    # Add authorization check here (e.g., check project access)
    
    updated_imagery = crud.imagery.update_imagery(db=db, db_imagery=db_imagery, imagery_in=imagery_in)
    return updated_imagery

@router.delete("/{imagery_id}", response_model=schemas.Imagery)
def delete_imagery_record(
    *,
    db: Session = Depends(get_db),
    imagery_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Delete an imagery record (and optionally the file).
    (Requires user to have delete access - to be added later)
    """
    imagery = crud.imagery.get_imagery(db=db, imagery_id=imagery_id)
    if not imagery:
        raise HTTPException(status_code=404, detail="Imagery not found")
        
    # Add authorization check here (e.g., check project access)
    
    # Optionally delete the associated file from storage
    # file_path = imagery.file_path
    # if file_path and os.path.exists(file_path):
    #     try:
    #         os.remove(file_path)
    #     except Exception as e:
    #         print(f"Warning: Could not delete imagery file {file_path}: {e}")
            # Decide if failure to delete file should prevent DB record deletion

    deleted_imagery = crud.imagery.delete_imagery(db=db, imagery_id=imagery_id)
    return deleted_imagery

print("API endpoints for Imagery defined.")


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import schemas, crud, models
from app.db.session import get_db
# Import dependency for authentication/authorization later
# from app.api import deps

router = APIRouter()

# Note: Forest endpoints are typically nested under projects, e.g., /projects/{project_id}/forests/
# For simplicity here, we use a top-level /forests/ endpoint, but nesting is recommended.

@router.post("/", response_model=schemas.Forest, status_code=status.HTTP_201_CREATED)
def create_forest(
    *, # Force keyword arguments
    db: Session = Depends(get_db),
    forest_in: schemas.ForestCreate,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Create new forest area within a project.
    (Requires user to have write access to the project - to be added later)
    """
    # Check if project exists
    project = crud.project.get_project(db, project_id=forest_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {forest_in.project_id} not found")
    
    # Add authorization check: does current_user have access to this project?

    try:
        forest = crud.forest.create_forest(db=db, forest=forest_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # The CRUD function now returns the object with geometry as GeoJSON
    return forest

@router.get("/", response_model=List[schemas.Forest])
def read_forests(
    db: Session = Depends(get_db),
    project_id: Optional[int] = None, # Allow filtering by project_id
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Retrieve forests, optionally filtered by project.
    (Requires user to have read access - to be added later)
    """
    if project_id:
        # Check if project exists and user has access
        project = crud.project.get_project(db, project_id=project_id)
        if not project:
             raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
        # Add authorization check here
        forests = crud.forest.get_forests_by_project(db, project_id=project_id, skip=skip, limit=limit)
    else:
        # Retrieving ALL forests might need admin privileges
        # For now, let's prevent fetching all forests without a project filter
        # forests = crud.forest.get_forests(db, skip=skip, limit=limit) # Implement get_forests if needed
         raise HTTPException(status_code=400, detail="Project ID must be provided to list forests")
    
    # The CRUD function returns objects with geometry as GeoJSON
    return forests

@router.get("/{forest_id}", response_model=schemas.Forest)
def read_forest_by_id(
    forest_id: int,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Get a specific forest by id.
    (Requires user to have access to the forest/project - to be added later)
    """
    forest = crud.forest.get_forest(db, forest_id=forest_id)
    if not forest:
        raise HTTPException(status_code=404, detail="Forest not found")
    
    # Add authorization check here (e.g., check project access)
    # The CRUD function returns the object with geometry as GeoJSON
    return forest

@router.put("/{forest_id}", response_model=schemas.Forest)
def update_forest(
    *,
    db: Session = Depends(get_db),
    forest_id: int,
    forest_in: schemas.ForestUpdate,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Update a forest.
    (Requires user to have write access to the forest/project - to be added later)
    """
    # Fetch the ORM model instance for update
    db_forest_orm = db.query(models.Forest).filter(models.Forest.forest_id == forest_id).first()
    if not db_forest_orm:
        raise HTTPException(
            status_code=404,
            detail="The forest with this id does not exist in the system",
        )
    
    # Add authorization check here (e.g., check project access)
    
    try:
        updated_forest = crud.forest.update_forest(db=db, db_forest=db_forest_orm, forest_in=forest_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # The CRUD function returns the object with geometry as GeoJSON
    return updated_forest

@router.delete("/{forest_id}", response_model=schemas.Forest)
def delete_forest(
    *,
    db: Session = Depends(get_db),
    forest_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Delete a forest.
    (Requires user to have delete access to the forest/project - to be added later)
    """
    # Fetch data first to return it, as delete returns the fetched data
    forest_data = crud.forest.get_forest(db=db, forest_id=forest_id)
    if not forest_data:
        raise HTTPException(status_code=404, detail="Forest not found")
        
    # Add authorization check here (e.g., check project access)
    
    deleted_forest_data = crud.forest.delete_forest(db=db, forest_id=forest_id)
    # CRUD returns the data fetched before deletion
    return deleted_forest_data

print("API endpoints for Forest defined.")


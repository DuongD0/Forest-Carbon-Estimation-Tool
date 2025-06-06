from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app import schemas, crud, models
from app.api import deps

router = APIRouter()

# Note: Forest endpoints are typically nested under projects, e.g., /projects/{project_id}/forests/
# For simplicity here, we use a top-level /forests/ endpoint, but nesting is recommended.

@router.post("/", response_model=schemas.Forest, status_code=status.HTTP_201_CREATED)
def create_forest(
    *,
    db: Session = Depends(deps.get_db),
    forest_in: schemas.ForestCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new forest area within a project.
    """
    project = crud.project.get_project(db, project_id=forest_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {forest_in.project_id} not found")
    
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to add a forest to this project")

    try:
        forest = crud.forest.create_forest(db=db, forest=forest_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return forest

@router.get("/", response_model=List[schemas.Forest])
def read_forests(
    db: Session = Depends(deps.get_db),
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve forests, filtered by project.
    """
    if not project_id:
        raise HTTPException(status_code=400, detail="Project ID must be provided to list forests")
        
    project = crud.project.get_project(db, project_id=project_id)
    if not project:
         raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
    
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to view forests for this project")

    forests = crud.forest.get_forests_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return forests

@router.get("/{forest_id}", response_model=schemas.Forest)
def read_forest_by_id(
    forest_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific forest by id.
    """
    forest = crud.forest.get_forest(db, forest_id=forest_id)
    if not forest:
        raise HTTPException(status_code=404, detail="Forest not found")
    
    project = crud.project.get_project(db, project_id=forest.project_id)
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to view this forest")
        
    return forest

@router.put("/{forest_id}", response_model=schemas.Forest)
def update_forest(
    *,
    db: Session = Depends(deps.get_db),
    forest_id: int,
    forest_in: schemas.ForestUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a forest.
    """
    db_forest_orm = db.query(models.Forest).filter(models.Forest.forest_id == forest_id).first()
    if not db_forest_orm:
        raise HTTPException(
            status_code=404,
            detail="The forest with this id does not exist in the system",
        )
    
    project = crud.project.get_project(db, project_id=db_forest_orm.project_id)
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to update this forest")
    
    try:
        updated_forest = crud.forest.update_forest(db=db, db_forest=db_forest_orm, forest_in=forest_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_forest

@router.delete("/{forest_id}", response_model=schemas.Forest)
def delete_forest(
    *,
    db: Session = Depends(deps.get_db),
    forest_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a forest.
    """
    forest_data = crud.forest.get_forest(db=db, forest_id=forest_id)
    if not forest_data:
        raise HTTPException(status_code=404, detail="Forest not found")
        
    project = crud.project.get_project(db, project_id=forest_data.project_id)
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this forest")
    
    deleted_forest_data = crud.forest.delete_forest(db=db, forest_id=forest_id)
    return deleted_forest_data

print("API endpoints for Forest defined.")


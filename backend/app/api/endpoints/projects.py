from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import schemas, crud, models
from app.db.session import get_db
# Import dependency for authentication/authorization later
# from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    *, # Force keyword arguments
    db: Session = Depends(get_db),
    project_in: schemas.ProjectCreate,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Create new project.
    (Requires authenticated user - to be added later)
    """
    # Placeholder: Use user_id 1 until auth is implemented
    owner_id = 1 # Replace with current_user.user_id later
    # Check if owner exists (optional, depends on FK constraints)
    owner = crud.user.get_user(db, user_id=owner_id)
    if not owner:
         raise HTTPException(status_code=404, detail="Owner user not found (placeholder error)")

    try:
        project = crud.project.create_project(db=db, project=project_in, owner_id=owner_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return project

@router.get("/", response_model=List[schemas.Project])
def read_projects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Retrieve projects.
    (Should filter by user or role later)
    """
    # Placeholder: Return all projects until auth/filtering is implemented
    projects = crud.project.get_projects(db, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=schemas.Project)
def read_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Get a specific project by id.
    (Requires user to have access to the project - to be added later)
    """
    project = crud.project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Add authorization check here later (e.g., if current_user.user_id == project.owner_id or is_superuser)
    return project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    project_in: schemas.ProjectUpdate,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Update a project.
    (Requires user to have write access to the project - to be added later)
    """
    db_project = crud.project.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(
            status_code=404,
            detail="The project with this id does not exist in the system",
        )
    # Add authorization check here later (e.g., if current_user.user_id == db_project.owner_id or is_superuser)
    try:
        project = crud.project.update_project(db=db, db_project=db_project, project_in=project_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return project

@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Delete a project.
    (Requires user to have delete access to the project - to be added later)
    """
    project = crud.project.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Add authorization check here later (e.g., if current_user.user_id == project.owner_id or is_superuser)
    deleted_project = crud.project.delete_project(db=db, project_id=project_id)
    return deleted_project

print("API endpoints for Project defined.")


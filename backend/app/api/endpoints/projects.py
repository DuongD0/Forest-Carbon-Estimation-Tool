from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Any

from app import schemas, crud, models
from app.api import deps
from app.processing.carbon_calculator import CarbonCalculator

router = APIRouter()

@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: schemas.ProjectCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new project.
    """
    try:
        project = crud.project.create_project(db=db, project=project_in, owner_id=current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return project

@router.get("/", response_model=List[schemas.Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve projects for the current user.
    """
    if crud.user.is_superuser(current_user):
        projects = crud.project.get_projects(db, skip=skip, limit=limit)
    else:
        projects = crud.project.get_projects_by_owner(db, owner_id=current_user.user_id, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=schemas.Project)
def read_project_by_id(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific project by id.
    """
    project = crud.project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    project_in: schemas.ProjectUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a project.
    """
    db_project = crud.project.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(
            status_code=404,
            detail="The project with this id does not exist in the system",
        )
    if not crud.user.is_superuser(current_user) and (db_project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        project = crud.project.update_project(db=db, db_project=db_project, project_in=project_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return project

@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a project.
    """
    project = crud.project.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    deleted_project = crud.project.delete_project(db=db, project_id=project_id)
    return deleted_project

@router.post("/{project_id}/calculate", response_model=schemas.ProjectCalculationResponse, status_code=status.HTTP_202_ACCEPTED)
def calculate_project_carbon(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Triggers the carbon credit calculation for a specific project as a background task.
    """
    project = crud.project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not crud.user.is_superuser(current_user) and (project.owner_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    def run_calculation_task(db_session: Session, proj_id: int):
        """Wrapper function to be run in the background."""
        try:
            calculator = CarbonCalculator(db_session=db_session, project_id=proj_id)
            calculator.run_full_calculation()
        except Exception as e:
            # A more robust system would update the project status to 'FAILED' in the DB
            print(f"Background calculation failed for project {proj_id}: {e}")

    background_tasks.add_task(run_calculation_task, db, project_id)

    return {
        "project_id": project_id,
        "status": "Accepted",
        "message": "Carbon calculation has been initiated in the background. Results will be saved upon completion.",
    }

print("API endpoints for Project defined.")


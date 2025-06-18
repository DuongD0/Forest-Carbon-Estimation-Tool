from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Project])
def get_bookmarked_projects(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    get my bookmarked projects
    """
    return current_user.bookmarked_projects

@router.post("/{project_id}", response_model=schemas.Project)
def add_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    bookmark a project for me
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project not in current_user.bookmarked_projects:
        current_user.bookmarked_projects.append(project)
        db.add(current_user)
        db.commit()

    return project

@router.delete("/{project_id}", response_model=schemas.Project)
def remove_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    remove my bookmark for a project
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project in current_user.bookmarked_projects:
        current_user.bookmarked_projects.remove(project)
        db.add(current_user)
        db.commit()

    return project 
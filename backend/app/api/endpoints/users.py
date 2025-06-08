from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
from typing import List
from fastapi import HTTPException

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get current user profile.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Update own user profile.
    """
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/me/bookmarks", response_model=List[schemas.Project])
def get_user_bookmarks(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get all projects bookmarked by the current user.
    """
    return current_user.bookmarked_projects

@router.post("/me/bookmarks", response_model=schemas.Project)
def add_user_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    bookmark_in: schemas.ProjectBookmarkCreate,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Add a project to the current user's bookmarks.
    """
    project_to_bookmark = crud.project.get(db, id=bookmark_in.project_id)
    if not project_to_bookmark:
        raise HTTPException(status_code=404, detail="Project not found")
    
    current_user.bookmarked_projects.append(project_to_bookmark)
    db.add(current_user)
    db.commit()
    db.refresh(project_to_bookmark)

    return project_to_bookmark

@router.delete("/me/bookmarks/{project_id}", response_model=schemas.Project)
def remove_user_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Remove a project from the current user's bookmarks.
    """
    project_to_remove = crud.project.get(db, id=project_id)
    if not project_to_remove:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_to_remove in current_user.bookmarked_projects:
        current_user.bookmarked_projects.remove(project_to_remove)
        db.add(current_user)
        db.commit()
    
    return project_to_remove

@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(deps.get_current_user, scopes=["read:users"]),
):
    """
    Retrieve all users. (Admin only)
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(deps.get_current_user, scopes=["read:users"]),
):
    """
    Get a specific user by ID. (Admin only)
    """
    user = crud.user.get(db, id=user_id)
    return user 
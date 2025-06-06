from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import schemas, crud, models
from app.db.session import get_db
from app.api import deps

router = APIRouter()

# --- User Endpoints ---

@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *, # Force keyword arguments
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create_user(db=db, user=user_in)
    return user

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get_user(db, user_id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud.user.update_user(db=db, db_user=user, user_in=user_in)
    return user

@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user.
    """
    user = crud.user.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    deleted_user = crud.user.delete_user(db=db, user_id=user_id)
    return deleted_user

# --- Role Endpoints ---

@router.post("/roles/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def create_role(
    *, 
    db: Session = Depends(deps.get_db),
    role_in: schemas.RoleCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new role.
    """
    role = crud.user.get_role_by_name(db, name=role_in.role_name)
    if role:
        raise HTTPException(
            status_code=400,
            detail="The role with this name already exists in the system.",
        )
    role = crud.user.create_role(db=db, role=role_in)
    return role

@router.get("/roles/", response_model=List[schemas.Role])
def read_roles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve roles.
    """
    roles = crud.user.get_roles(db, skip=skip, limit=limit)
    return roles

@router.get("/roles/{role_id}", response_model=schemas.Role)
def read_role_by_id(
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a specific role by id.
    """
    role = crud.user.get_role(db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    role_in: schemas.RoleUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a role.
    """
    db_role = crud.user.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(
            status_code=404,
            detail="The role with this id does not exist in the system",
        )
    updated_role = crud.user.update_role(db=db, db_role=db_role, role_in=role_in)
    return updated_role

@router.delete("/roles/{role_id}", response_model=schemas.Role)
def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a role.
    """
    role = crud.user.get_role(db=db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    deleted_role = crud.user.delete_role(db=db, role_id=role_id)
    return deleted_role

# --- Permission Endpoints ---

@router.post("/permissions/", response_model=schemas.Permission, status_code=status.HTTP_201_CREATED)
def create_permission(
    *, 
    db: Session = Depends(deps.get_db),
    permission_in: schemas.PermissionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new permission.
    """
    permission = crud.user.get_permission_by_name(db, name=permission_in.permission_name)
    if permission:
        raise HTTPException(
            status_code=400,
            detail="The permission with this name already exists in the system.",
        )
    permission = crud.user.create_permission(db=db, permission=permission_in)
    return permission

@router.get("/permissions/", response_model=List[schemas.Permission])
def read_permissions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve permissions.
    """
    permissions = crud.user.get_permissions(db, skip=skip, limit=limit)
    return permissions

print("API endpoints for User, Role, Permission defined.")


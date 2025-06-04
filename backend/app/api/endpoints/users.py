from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import schemas, crud, models
from app.db.session import get_db
# Import dependency for authentication/authorization later
# from app.api import deps

router = APIRouter()

# --- User Endpoints ---

@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *, # Force keyword arguments
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Create new user.
    (Requires superuser privileges - to be added later)
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
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Retrieve users.
    (Requires superuser privileges - to be added later)
    """
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/me", response_model=schemas.User)
def read_user_me(
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
    db: Session = Depends(get_db) # Placeholder until auth is added
) -> Any:
    """
    Get current user.
    """
    # Placeholder: return the first user until auth is implemented
    current_user = crud.user.get_user(db, user_id=1)
    if not current_user:
         raise HTTPException(status_code=404, detail="User not found (placeholder error)")
    return current_user

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Get a specific user by id.
    (Requires user to be reading self or superuser - to be added later)
    """
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Add authorization check here later
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    # current_user: models.User = Depends(deps.get_current_active_user) # Add authorization later
) -> Any:
    """
    Update a user.
    (Requires user to be updating self or superuser - to be added later)
    """
    db_user = crud.user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    # Add authorization check here later
    user = crud.user.update_user(db=db, db_user=db_user, user_in=user_in)
    return user

@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Delete a user.
    (Requires superuser privileges - to be added later)
    """
    user = crud.user.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Add authorization check here later
    deleted_user = crud.user.delete_user(db=db, user_id=user_id)
    return deleted_user

# --- Role Endpoints ---

@router.post("/roles/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def create_role(
    *, 
    db: Session = Depends(get_db),
    role_in: schemas.RoleCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Create new role.
    (Requires superuser privileges - to be added later)
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
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Retrieve roles.
    (Requires superuser privileges - to be added later)
    """
    roles = crud.user.get_roles(db, skip=skip, limit=limit)
    return roles

@router.get("/roles/{role_id}", response_model=schemas.Role)
def read_role_by_id(
    role_id: int,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Get a specific role by id.
    (Requires superuser privileges - to be added later)
    """
    role = crud.user.get_role(db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    role_in: schemas.RoleUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Update a role.
    (Requires superuser privileges - to be added later)
    """
    db_role = crud.user.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(
            status_code=404,
            detail="The role with this id does not exist in the system",
        )
    role = crud.user.update_role(db=db, db_role=db_role, role_in=role_in)
    return role

@router.delete("/roles/{role_id}", response_model=schemas.Role)
def delete_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Delete a role.
    (Requires superuser privileges - to be added later)
    """
    role = crud.user.get_role(db=db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    # Add check for users assigned to role before deleting?
    deleted_role = crud.user.delete_role(db=db, role_id=role_id)
    return deleted_role

# --- Permission Endpoints ---

@router.post("/permissions/", response_model=schemas.Permission, status_code=status.HTTP_201_CREATED)
def create_permission(
    *, 
    db: Session = Depends(get_db),
    permission_in: schemas.PermissionCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Create new permission.
    (Requires superuser privileges - to be added later)
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
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Add authorization later
) -> Any:
    """
    Retrieve permissions.
    (Requires superuser privileges - to be added later)
    """
    permissions = crud.user.get_permissions(db, skip=skip, limit=limit)
    return permissions

print("API endpoints for User, Role, Permission defined.")


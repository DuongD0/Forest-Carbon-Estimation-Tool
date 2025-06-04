from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.user import User, Role, Permission
from app.schemas.user import UserCreate, UserUpdate, RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate
from app.core.security import get_password_hash

# --- Permission CRUD ---

def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.permission_id == permission_id).first()

def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.permission_name == name).first()

def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    return db.query(Permission).offset(skip).limit(limit).all()

def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    db_permission = Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def update_permission(db: Session, db_permission: Permission, permission_in: PermissionUpdate) -> Permission:
    update_data = permission_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_permission, key, value)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def delete_permission(db: Session, permission_id: int) -> Optional[Permission]:
    db_permission = get_permission(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
    return db_permission

# --- Role CRUD ---

def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).options(joinedload(Role.permissions)).filter(Role.role_id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.role_name == name).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).options(joinedload(Role.permissions)).offset(skip).limit(limit).all()

def create_role(db: Session, role: RoleCreate) -> Role:
    db_role = Role(role_name=role.role_name, description=role.description)
    if role.permission_ids:
        permissions = db.query(Permission).filter(Permission.permission_id.in_(role.permission_ids)).all()
        db_role.permissions = permissions
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    # Eager load permissions after creation for the return value
    db.expire(db_role)
    db_role = get_role(db, db_role.role_id) # Re-fetch to load permissions
    return db_role

def update_role(db: Session, db_role: Role, role_in: RoleUpdate) -> Role:
    update_data = role_in.dict(exclude_unset=True, exclude={"permission_ids"})
    for key, value in update_data.items():
        setattr(db_role, key, value)

    if role_in.permission_ids is not None:
        if not role_in.permission_ids:
            db_role.permissions = []
        else:
            permissions = db.query(Permission).filter(Permission.permission_id.in_(role_in.permission_ids)).all()
            db_role.permissions = permissions

    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    # Eager load permissions after update for the return value
    db.expire(db_role)
    db_role = get_role(db, db_role.role_id) # Re-fetch to load permissions
    return db_role

def delete_role(db: Session, role_id: int) -> Optional[Role]:
    db_role = get_role(db, role_id)
    if db_role:
        # Check if any users are assigned this role before deleting (optional constraint)
        # users_with_role = db.query(User).filter(User.role_id == role_id).count()
        # if users_with_role > 0:
        #     raise ValueError("Cannot delete role assigned to users")
        db.delete(db_role)
        db.commit()
    return db_role

# --- User CRUD ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).options(joinedload(User.role)).filter(User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).options(joinedload(User.role)).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
     return db.query(User).options(joinedload(User.role)).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).options(joinedload(User.role)).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role_id=user.role_id,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Eager load role after creation
    db.expire(db_user)
    db_user = get_user(db, db_user.user_id)
    return db_user

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    else:
        # Ensure password field is not accidentally set to None or empty string if not provided
        if "password" in update_data:
            del update_data["password"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Eager load role after update
    db.expire(db_user)
    db_user = get_user(db, db_user.user_id)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

print("CRUD functions for User, Role, Permission defined.")


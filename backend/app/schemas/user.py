from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Shared properties
class PermissionBase(BaseModel):
    permission_name: str
    description: Optional[str] = None

# Properties to receive via API on creation
class PermissionCreate(PermissionBase):
    pass

# Properties to receive via API on update
class PermissionUpdate(PermissionBase):
    pass

# Properties shared by models stored in DB
class PermissionInDBBase(PermissionBase):
    permission_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Permission(PermissionInDBBase):
    pass

# Properties stored in DB
class PermissionInDB(PermissionInDBBase):
    pass

# --- Role Schemas ---

class RoleBase(BaseModel):
    role_name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: List[int] = []

class RoleUpdate(RoleBase):
    permission_ids: Optional[List[int]] = None

class RoleInDBBase(RoleBase):
    role_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Role(RoleInDBBase):
    permissions: List[Permission] = []

class RoleInDB(RoleInDBBase):
    pass

# --- User Schemas ---

class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None # Assign a default role if needed

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    user_id: int
    role_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    role: Optional[Role] = None # Include role details

# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

print("Pydantic schemas for User, Role, Permission defined.")


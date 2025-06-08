from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    id: uuid.UUID
    email: EmailStr

# Properties to receive via API on update
class UserUpdate(UserBase):
    pass

class UserInDBBase(UserBase):
    id: uuid.UUID
    
    class Config:
        orm_mode = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    pass 
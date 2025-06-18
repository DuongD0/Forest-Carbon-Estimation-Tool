from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, ConfigDict

# shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None

# properties for creating
class UserCreate(UserBase):
    email: EmailStr

# properties for updating
class UserUpdate(UserBase):
    pass

class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID

# properties to return to client
class User(UserInDBBase):
    pass

# properties stored in db
class UserInDB(UserInDBBase):
    pass 
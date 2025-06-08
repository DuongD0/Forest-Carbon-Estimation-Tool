import uuid
from typing import Optional
from pydantic import BaseModel
from app.models.project import ProjectType, ProjectStatus

# Shared properties
class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = ProjectStatus.DRAFT
    ecosystem_id: Optional[uuid.UUID] = None

# Properties to receive on project creation
class ProjectCreate(ProjectBase):
    name: str
    project_type: ProjectType

# Properties to receive on project update
class ProjectUpdate(ProjectBase):
    pass

# Properties shared by models in DB
class ProjectInDBBase(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    ecosystem_id: Optional[uuid.UUID] = None
    
    class Config:
        orm_mode = True

# Properties to return to client
class Project(ProjectInDBBase):
    pass

# Properties stored in DB
class ProjectInDB(ProjectInDBBase):
    pass 
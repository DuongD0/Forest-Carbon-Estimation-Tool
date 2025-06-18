import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.project import ProjectType, ProjectStatus

# shared properties
class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = ProjectStatus.DRAFT
    ecosystem_id: Optional[uuid.UUID] = None

# properties for creating a project
class ProjectCreate(ProjectBase):
    name: str
    project_type: ProjectType

# properties for updating a project
class ProjectUpdate(ProjectBase):
    pass

# properties for projects in the db
class ProjectInDBBase(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    owner_id: uuid.UUID
    ecosystem_id: Optional[uuid.UUID] = None

# properties to return to client
class Project(ProjectInDBBase):
    pass

# properties stored in db
class ProjectInDB(ProjectInDBBase):
    pass 
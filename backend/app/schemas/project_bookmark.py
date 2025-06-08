import uuid
from pydantic import BaseModel
 
class ProjectBookmarkCreate(BaseModel):
    project_id: uuid.UUID 
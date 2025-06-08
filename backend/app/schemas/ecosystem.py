import uuid
from typing import Optional
from pydantic import BaseModel

class EcosystemBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    carbon_factor: Optional[float] = None
    biomass_factor: Optional[float] = None

class EcosystemCreate(EcosystemBase):
    name: str
    carbon_factor: float
    biomass_factor: float

class EcosystemUpdate(EcosystemBase):
    pass

class EcosystemInDBBase(EcosystemBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class Ecosystem(EcosystemInDBBase):
    pass

class EcosystemInDB(EcosystemInDBBase):
    pass 
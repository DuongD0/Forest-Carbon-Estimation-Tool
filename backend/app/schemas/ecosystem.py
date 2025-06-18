import uuid
from typing import Optional, List
from pydantic import BaseModel

class EcosystemBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    carbon_factor: Optional[float] = None
    max_biomass_per_ha: Optional[float] = None
    biomass_growth_rate: Optional[float] = None
    lower_rgb: Optional[List[int]] = None
    upper_rgb: Optional[List[int]] = None
    forest_type: Optional[str] = None

class EcosystemCreate(EcosystemBase):
    name: str
    carbon_factor: float
    max_biomass_per_ha: float
    biomass_growth_rate: float

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
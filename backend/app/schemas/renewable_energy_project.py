import uuid
from typing import Optional
from pydantic import BaseModel
from app.models.renewable_energy_project import RenewableEnergyType

class RenewableEnergyProjectBase(BaseModel):
    energy_type: Optional[RenewableEnergyType] = None
    capacity_mw: Optional[float] = None
    annual_generation_mwh: Optional[float] = None
    grid_emission_factor: Optional[float] = None

class RenewableEnergyProjectCreate(RenewableEnergyProjectBase):
    project_id: uuid.UUID
    energy_type: RenewableEnergyType
    capacity_mw: float
    annual_generation_mwh: float
    grid_emission_factor: float

class RenewableEnergyProjectUpdate(RenewableEnergyProjectBase):
    pass

class RenewableEnergyProjectInDBBase(RenewableEnergyProjectBase):
    id: uuid.UUID
    project_id: uuid.UUID
    
    class Config:
        orm_mode = True

class RenewableEnergyProject(RenewableEnergyProjectInDBBase):
    pass 
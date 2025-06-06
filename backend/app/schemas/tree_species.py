from pydantic import BaseModel, Field
from typing import Optional

class TreeSpeciesBase(BaseModel):
    scientific_name: str = Field(..., max_length=150)
    common_name_en: Optional[str] = Field(None, max_length=150)
    common_name_vi: Optional[str] = Field(None, max_length=150)
    wood_density: Optional[float] = None
    notes: Optional[str] = None

class TreeSpeciesCreate(TreeSpeciesBase):
    pass

class TreeSpeciesUpdate(TreeSpeciesBase):
    pass

class TreeSpeciesInDBBase(TreeSpeciesBase):
    species_id: int

    class Config:
        orm_mode = True

class TreeSpecies(TreeSpeciesInDBBase):
    pass

class TreeSpeciesInDB(TreeSpeciesInDBBase):
    pass 
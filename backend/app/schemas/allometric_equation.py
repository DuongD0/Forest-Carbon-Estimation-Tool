from pydantic import BaseModel, Field
from typing import Optional

class AllometricEquationBase(BaseModel):
    equation_name: str = Field(..., max_length=255)
    equation_formula: str = Field(..., max_length=500)
    region: Optional[str] = Field(None, max_length=100)
    species_group: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = None
    notes: Optional[str] = None

class AllometricEquationCreate(AllometricEquationBase):
    pass

class AllometricEquationUpdate(AllometricEquationBase):
    pass

class AllometricEquationInDBBase(AllometricEquationBase):
    equation_id: int

    class Config:
        orm_mode = True

class AllometricEquation(AllometricEquationInDBBase):
    pass

class AllometricEquationInDB(AllometricEquationInDBBase):
    pass 
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class PlotCompositionBase(BaseModel):
    percentage_cover: Optional[float] = Field(None, ge=0, le=100)
    stem_density: Optional[float] = Field(None, ge=0)
    average_dbh: Optional[float] = Field(None, ge=0)
    average_height: Optional[float] = Field(None, ge=0)
    measurement_date: date
    source: Optional[str] = None

class PlotCompositionCreate(PlotCompositionBase):
    plot_id: int
    species_id: int

class PlotCompositionUpdate(PlotCompositionBase):
    pass

class PlotCompositionInDBBase(PlotCompositionBase):
    plot_composition_id: int
    plot_id: int
    species_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        orm_mode = True

class PlotComposition(PlotCompositionInDBBase):
    pass

class PlotCompositionInDB(PlotCompositionInDBBase):
    pass 
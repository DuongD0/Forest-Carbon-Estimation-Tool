from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class ForestPlotBase(BaseModel):
    plot_name: str = Field(..., max_length=150)
    description: Optional[str] = None
    geometry: Any

class ForestPlotCreate(ForestPlotBase):
    forest_id: int

class ForestPlotUpdate(ForestPlotBase):
    plot_name: Optional[str] = Field(None, max_length=150)
    geometry: Optional[Any] = None

class ForestPlotInDBBase(ForestPlotBase):
    plot_id: int
    forest_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        orm_mode = True

class ForestPlot(ForestPlotInDBBase):
    pass

class ForestPlotInDB(ForestPlotInDBBase):
    pass 
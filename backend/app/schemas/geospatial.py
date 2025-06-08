from pydantic import BaseModel, Field
from typing import List, Any, Dict

class GeoJSON(BaseModel):
    type: str = Field(..., example="Polygon")
    coordinates: List[Any]

    class Config:
        schema_extra = {
            "example": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [10.0, 10.0],
                        [10.0, 20.0],
                        [20.0, 20.0],
                        [20.0, 10.0],
                        [10.0, 10.0]
                    ]
                ]
            }
        } 
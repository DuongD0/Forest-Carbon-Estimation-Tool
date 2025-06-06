# CRUD operations for Forest Plots

from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_AsGeoJSON

from app.crud.base import CRUDBase
from app.models.forest_plot import ForestPlot
from app.schemas.forest_plot import ForestPlotCreate, ForestPlotUpdate # Assuming schemas exist

class CRUDForestPlot(CRUDBase[ForestPlot, ForestPlotCreate, ForestPlotUpdate]):
    def get_multi_by_forest(self, db: Session, *, forest_id: int, skip: int = 0, limit: int = 100) -> List[ForestPlot]:
        return db.query(self.model).filter(ForestPlot.forest_id == forest_id).offset(skip).limit(limit).all()

    # Add method to get plot with geometry as GeoJSON
    def get_plot_geojson(self, db: Session, *, plot_id: int) -> Optional[Dict[str, Any]]:
        result = db.query(
            self.model.plot_id,
            self.model.plot_name,
            self.model.forest_id,
            self.model.description,
            self.model.created_at,
            self.model.updated_at,
            self.model.created_by,
            func.ST_Area(self.model.geometry.cast(Geography)).label("area_ha_calculated"), # Calculate area on the fly if needed
            ST_AsGeoJSON(self.model.geometry).label("geometry_geojson")
        ).filter(ForestPlot.plot_id == plot_id).first()

        if result:
            plot_dict = result._asdict()
            plot_dict["geometry"] = json.loads(plot_dict.pop("geometry_geojson"))
            return plot_dict
        return None

    # Add any other specific query methods needed for forest plots
    # e.g., spatial queries (find plots intersecting a bounding box)

forest_plot = CRUDForestPlot(ForestPlot)


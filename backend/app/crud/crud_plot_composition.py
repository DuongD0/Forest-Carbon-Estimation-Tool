# CRUD operations for Plot Composition

from typing import Any, Dict, Optional, Union, List
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.plot_composition import PlotComposition
from app.schemas.plot_composition import PlotCompositionCreate, PlotCompositionUpdate # Assuming schemas exist

class CRUDPlotComposition(CRUDBase[PlotComposition, PlotCompositionCreate, PlotCompositionUpdate]):
    def get_multi_by_plot(self, db: Session, *, plot_id: int, skip: int = 0, limit: int = 1000) -> List[PlotComposition]:
        """Retrieve composition records for a specific plot."""
        return db.query(self.model).filter(PlotComposition.plot_id == plot_id).offset(skip).limit(limit).all()

    def get_by_plot_species_date(self, db: Session, *, plot_id: int, species_id: int, measurement_date: date) -> Optional[PlotComposition]:
        """Retrieve a specific composition record by plot, species, and date."""
        return db.query(self.model).filter(
            PlotComposition.plot_id == plot_id,
            PlotComposition.species_id == species_id,
            PlotComposition.measurement_date == measurement_date
        ).first()

    def get_latest_composition_for_plot(self, db: Session, *, plot_id: int) -> List[PlotComposition]:
        """Retrieve the most recent composition data for all species in a plot."""
        # Find the latest measurement date for the plot
        latest_date = db.query(func.max(PlotComposition.measurement_date)).filter(PlotComposition.plot_id == plot_id).scalar()
        if not latest_date:
            return []
        # Retrieve all composition records for that plot on the latest date
        return db.query(self.model).filter(
            PlotComposition.plot_id == plot_id,
            PlotComposition.measurement_date == latest_date
        ).all()

    def get_composition_for_plot_at_date(self, db: Session, *, plot_id: int, target_date: date) -> List[PlotComposition]:
        """Retrieve the composition data for a plot effective at a specific target date (most recent on or before)."""
        # Find the most recent measurement date on or before the target date
        effective_date = db.query(func.max(PlotComposition.measurement_date))\
            .filter(PlotComposition.plot_id == plot_id, PlotComposition.measurement_date <= target_date)\
            .scalar()

        if not effective_date:
            return [] # No composition data available on or before the target date

        # Retrieve all composition records for that plot on the effective date
        return db.query(self.model).filter(
            PlotComposition.plot_id == plot_id,
            PlotComposition.measurement_date == effective_date
        ).all()

    # Add any other specific query methods needed for plot composition

plot_composition = CRUDPlotComposition(PlotComposition)


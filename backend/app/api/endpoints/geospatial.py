from typing import List, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/projects/near", response_model=List[schemas.Project])
def find_projects_near(
    db: Session = Depends(deps.get_db),
    lat: float = Query(..., description="Latitude of the center point"),
    lon: float = Query(..., description="Longitude of the center point"),
    distance_km: float = Query(10.0, description="Distance in kilometers"),
):
    """
    Find projects within a certain distance from a geographic point.
    """
    # Create a point from the input lat/lon
    point = f'POINT({lon} {lat})'
    
    # Convert distance from km to meters
    distance_m = distance_km * 1000

    # Query projects within the distance using PostGIS ST_DWithin
    # We cast the project's geometry to geography for distance calculations in meters
    projects = (
        db.query(models.Project)
        .filter(
            ST_DWithin(
                models.Project.location_geometry.cast(Geography),
                func.ST_GeogFromText(point),
                distance_m
            )
        )
        .all()
    )
    return projects 
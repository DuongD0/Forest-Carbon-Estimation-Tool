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
    find projects near a lat/lon point
    """
    # make a point from the lat/lon
    point = f'POINT({lon} {lat})'
    
    # convert km to meters for the query
    distance_m = distance_km * 1000

    # find projects inside the distance with postgis ST_DWithin
    # have to cast to geography to get meters
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
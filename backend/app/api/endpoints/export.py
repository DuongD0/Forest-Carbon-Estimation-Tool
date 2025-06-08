from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

from app import crud, models
from app.api import deps

router = APIRouter()

@router.get("/project/{project_id}/geojson", response_class=JSONResponse)
def export_project_as_geojson(
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Export a project's geometry as a GeoJSON Feature.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Optional: Check if the user has permission to view this project
    if project.owner_id != current_user.id:
        # Or if it's a public project, etc.
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if not project.location_geometry:
        raise HTTPException(status_code=404, detail="Project does not have a geometry to export.")

    # Convert the WKBElement to a Shapely geometry object
    geom = to_shape(project.location_geometry)

    # Create a GeoJSON Feature dictionary
    feature = {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": {
            "project_id": str(project.id),
            "project_name": project.name,
            "project_type": project.project_type,
        },
    }

    return JSONResponse(content=feature) 
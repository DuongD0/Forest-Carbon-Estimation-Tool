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
    get a project's geometry as a geojson thingy
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # check if user is allowed to see this
    if project.owner_id != current_user.id:
        # or if it's a public project or whatever
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if not project.location_geometry:
        raise HTTPException(status_code=404, detail="Project does not have a geometry to export.")

    # convert the wkb thing to a shapely geometry
    geom = to_shape(project.location_geometry)

    # make a geojson feature dict
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
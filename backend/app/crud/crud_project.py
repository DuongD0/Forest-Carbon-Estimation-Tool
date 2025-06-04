from sqlalchemy.orm import Session
from typing import List, Optional, Any
from sqlalchemy import func
from geoalchemy2.functions import ST_AsGeoJSON

from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.user import User # For type hinting owner

# Helper to convert geometry to GeoJSON if it exists
def geometry_to_geojson(geometry):
    if geometry is None:
        return None
    # Use ST_AsGeoJSON which returns a string, then parse it (or handle directly if needed)
    # This requires executing a query, so it's better done at the query level if possible
    # For simplicity here, we assume the ORM handles it or we fetch it separately.
    # A raw query might look like: db.query(ST_AsGeoJSON(Project.location_geometry))... 
    # For now, return a placeholder or handle in the schema/endpoint if needed.
    return "GeoJSON representation requires query-level conversion (ST_AsGeoJSON)"

def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).options(joinedload(Project.owner)).filter(Project.project_id == project_id).first()

def get_projects_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
    return db.query(Project).options(joinedload(Project.owner)).filter(Project.owner_id == owner_id).offset(skip).limit(limit).all()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    return db.query(Project).options(joinedload(Project.owner)).offset(skip).limit(limit).all()

def create_project(db: Session, project: ProjectCreate, owner_id: int) -> Project:
    # Convert GeoJSON input to WKT for storage if needed, or use GeoAlchemy's handling
    geometry_wkt = None
    if project.location_geometry:
        # Basic validation example (more robust needed)
        if isinstance(project.location_geometry, dict) and project.location_geometry.get("type") == "Polygon":
             # GeoAlchemy handles dicts with SRID; ensure input is valid GeoJSON
             # For WKT: from shapely.geometry import shape; geometry_wkt = shape(project.location_geometry).wkt
             # Assuming GeoAlchemy handles the dict directly with SRID 4326
             pass 
        else:
             raise ValueError("Invalid GeoJSON format for location_geometry")

    db_project = Project(
        project_name=project.project_name,
        description=project.description,
        status=project.status or ProjectStatus.DRAFT,
        owner_id=owner_id, # Use the provided owner_id
        location_geometry=project.location_geometry # Pass the GeoJSON dict directly if GeoAlchemy supports it
        # If using WKT: location_geometry=f'SRID=4326;{geometry_wkt}'
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    # Eager load owner after creation
    db.expire(db_project)
    db_project = get_project(db, db_project.project_id)
    return db_project

def update_project(db: Session, db_project: Project, project_in: ProjectUpdate) -> Project:
    update_data = project_in.dict(exclude_unset=True)

    if "location_geometry" in update_data and update_data["location_geometry"]:
        geometry_input = update_data["location_geometry"]
        if isinstance(geometry_input, dict) and geometry_input.get("type") == "Polygon":
            # Assuming GeoAlchemy handles dict directly
            setattr(db_project, "location_geometry", geometry_input)
        else:
             raise ValueError("Invalid GeoJSON format for location_geometry")
        del update_data["location_geometry"] # Remove from dict after handling

    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    # Eager load owner after update
    db.expire(db_project)
    db_project = get_project(db, db_project.project_id)
    return db_project

def delete_project(db: Session, project_id: int) -> Optional[Project]:
    db_project = get_project(db, project_id)
    if db_project:
        # Add checks here if needed (e.g., cannot delete project with active calculations)
        db.delete(db_project)
        db.commit()
    return db_project

print("CRUD functions for Project defined.")


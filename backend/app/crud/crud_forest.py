from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Any
from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromGeoJSON

from app.models.forest import Forest, ForestTypeEnum
from app.schemas.forest import ForestCreate, ForestUpdate

# Helper to convert GeoJSON input to a format GeoAlchemy2 understands
# GeoAlchemy2 can often handle GeoJSON-like dictionaries directly if the SRID is included or known
def geojson_to_geometry(geojson_data: Any, srid: int = 4326):
    if not geojson_data or not isinstance(geojson_data, dict):
        return None
    # Ensure it looks like GeoJSON (basic check)
    if "type" not in geojson_data or "coordinates" not in geojson_data:
        raise ValueError("Invalid GeoJSON structure")
    # GeoAlchemy2 expects a WKT string or a GeoJSON-like dict. 
    # Let's assume it handles the dict directly. If not, convert to WKT:
    # from shapely.geometry import shape
    # geom = shape(geojson_data)
    # return f"SRID={srid};{geom.wkt}"
    # For direct dict handling, ensure SRID is implicitly handled or set:
    return ST_SetSRID(ST_GeomFromGeoJSON(str(geojson_data)), srid) # Use database functions

def get_forest(db: Session, forest_id: int) -> Optional[Forest]:
    # Use ST_AsGeoJSON to fetch geometry in GeoJSON format
    return db.query(
        Forest.forest_id, Forest.project_id, Forest.forest_name, Forest.forest_type, 
        Forest.description, Forest.area_ha, Forest.created_at, Forest.updated_at,
        ST_AsGeoJSON(Forest.geometry).label("geometry")
    ).filter(Forest.forest_id == forest_id).first()

def get_forests_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Forest]:
    # Use ST_AsGeoJSON here as well
    query = db.query(
        Forest.forest_id, Forest.project_id, Forest.forest_name, Forest.forest_type, 
        Forest.description, Forest.area_ha, Forest.created_at, Forest.updated_at,
        ST_AsGeoJSON(Forest.geometry).label("geometry")
    ).filter(Forest.project_id == project_id).offset(skip).limit(limit)
    return query.all()

def create_forest(db: Session, forest: ForestCreate) -> Forest:
    geometry_wkt = None
    if forest.geometry:
        # Basic validation example (more robust needed)
        if isinstance(forest.geometry, dict) and forest.geometry.get("type") == "MultiPolygon":
             # Convert GeoJSON dict to WKT with SRID for storage
             from shapely.geometry import shape
             geom = shape(forest.geometry)
             geometry_wkt = f'SRID=4326;{geom.wkt}' # Assuming input is WGS84 (SRID 4326)
        else:
             raise ValueError("Invalid GeoJSON format for geometry, expected MultiPolygon")
    else:
        raise ValueError("Geometry is required to create a forest")

    db_forest = Forest(
        project_id=forest.project_id,
        forest_name=forest.forest_name,
        forest_type=forest.forest_type,
        description=forest.description,
        geometry=geometry_wkt, # Store as WKT with SRID
        area_ha=forest.area_ha # Area might be calculated later
    )
    db.add(db_forest)
    db.commit()
    db.refresh(db_forest)
    # Re-fetch with ST_AsGeoJSON to return GeoJSON
    return get_forest(db, db_forest.forest_id)

def update_forest(db: Session, db_forest: Forest, forest_in: ForestUpdate) -> Forest:
    update_data = forest_in.dict(exclude_unset=True)

    if "geometry" in update_data and update_data["geometry"]:
        geometry_input = update_data["geometry"]
        if isinstance(geometry_input, dict) and geometry_input.get("type") == "MultiPolygon":
            from shapely.geometry import shape
            geom = shape(geometry_input)
            geometry_wkt = f'SRID=4326;{geom.wkt}'
            setattr(db_forest, "geometry", geometry_wkt)
        else:
             raise ValueError("Invalid GeoJSON format for geometry, expected MultiPolygon")
        del update_data["geometry"] # Remove from dict after handling

    for key, value in update_data.items():
        setattr(db_forest, key, value)

    db.add(db_forest)
    db.commit()
    db.refresh(db_forest)
    # Re-fetch with ST_AsGeoJSON
    return get_forest(db, db_forest.forest_id)

def delete_forest(db: Session, forest_id: int) -> Optional[Forest]:
    # Fetch first to return the object before deletion
    db_forest_data = get_forest(db, forest_id)
    if db_forest_data:
        # Get the ORM object to delete
        db_forest_orm = db.query(Forest).filter(Forest.forest_id == forest_id).first()
        if db_forest_orm:
            db.delete(db_forest_orm)
            db.commit()
            return db_forest_data # Return the data fetched before deletion
    return None

print("CRUD functions for Forest defined.")


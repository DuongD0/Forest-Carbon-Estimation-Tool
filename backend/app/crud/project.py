from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from app.crud.base import CRUDBase
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: ProjectCreate, owner_id: uuid.UUID
    ) -> Project:
        db_obj = Project(
            **obj_in.dict(),
            owner_id=owner_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: uuid.UUID, skip: int = 0, limit: int = 100, project_type: Optional[str] = None
    ) -> List[Project]:
        query = db.query(self.model).filter(Project.owner_id == owner_id)
        if project_type:
            query = query.filter(Project.project_type == project_type)
        return query.offset(skip).limit(limit).all()

    def get_projects_near(
        self, db: Session, *, lat: float, lon: float, distance_km: float
    ) -> List[Project]:
        """
        finds projects within a certain distance (in km) from a lat/lon point.
        """
        # postgis wants meters, so convert km to m
        distance_meters = distance_km * 1000
        
        # make a point from the lat/lon and cast to geography
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        point_geography = func.geography(point)

        return (
            db.query(self.model)
            .filter(func.ST_DWithin(
                self.model.location_geometry,
                point_geography,
                distance_meters
            ))
            .all()
        )

project = CRUDProject(Project) 
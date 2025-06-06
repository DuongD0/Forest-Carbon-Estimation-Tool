from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.imagery import Imagery, ImageryStatusEnum, ImagerySourceEnum
from app.schemas.imagery import ImageryCreate, ImageryUpdate


class CRUDImagery(CRUDBase[Imagery, ImageryCreate, ImageryUpdate]):
    pass


imagery = CRUDImagery(Imagery)


def get_imagery(db: Session, imagery_id: int) -> Optional[Imagery]:
    return db.query(Imagery).options(joinedload(Imagery.uploaded_by)).filter(Imagery.imagery_id == imagery_id).first()

def get_imagery_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Imagery]:
    return db.query(Imagery).options(joinedload(Imagery.uploaded_by)).filter(Imagery.project_id == project_id).offset(skip).limit(limit).all()

def create_imagery(db: Session, imagery: ImageryCreate) -> Imagery:
    # uploaded_by_id should be set based on the current user in the endpoint
    db_imagery = Imagery(**imagery.dict())
    db.add(db_imagery)
    db.commit()
    db.refresh(db_imagery)
    # Eager load uploader after creation
    db.expire(db_imagery)
    db_imagery = get_imagery(db, db_imagery.imagery_id)
    return db_imagery

def update_imagery(db: Session, db_imagery: Imagery, imagery_in: ImageryUpdate) -> Imagery:
    update_data = imagery_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_imagery, key, value)
    db.add(db_imagery)
    db.commit()
    db.refresh(db_imagery)
    # Eager load uploader after update
    db.expire(db_imagery)
    db_imagery = get_imagery(db, db_imagery.imagery_id)
    return db_imagery

def delete_imagery(db: Session, imagery_id: int) -> Optional[Imagery]:
    db_imagery = get_imagery(db, imagery_id)
    if db_imagery:
        # Add checks here if needed (e.g., cannot delete imagery used in calculations)
        db.delete(db_imagery)
        db.commit()
    return db_imagery

print("CRUD functions for Imagery defined.")


import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.crud.base import CRUDBase
from app.models.imagery import Imagery, ImageryProcessingResult, ImageryStatus, SatelliteType
from app.schemas.imagery import (
    ImageryCreate, 
    ImageryUpdate, 
    ProcessingResultCreate, 
    ProcessingResultUpdate,
    ImageryMetadata
)

class CRUDImagery(CRUDBase[Imagery, ImageryCreate, ImageryUpdate]):
    def create_with_metadata(
        self, 
        db: Session, 
        *, 
        obj_in: ImageryCreate, 
        file_path: str,
        metadata: Optional[ImageryMetadata] = None
    ) -> Imagery:
        """Create imagery with metadata"""
        db_obj_data = obj_in.model_dump()
        
        # Add file path
        db_obj_data["file_path"] = file_path
        
        # Flatten metadata if provided
        if metadata:
            metadata_dict = metadata.model_dump()
            for key, value in metadata_dict.items():
                if value is not None:
                    db_obj_data[key] = value
        
        db_obj = self.model(**db_obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_project(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ImageryStatus] = None,
        satellite_type: Optional[SatelliteType] = None
    ) -> List[Imagery]:
        """Get imagery by project with optional filters"""
        query = db.query(self.model).filter(self.model.project_id == project_id)
        
        if status:
            query = query.filter(self.model.status == status)
        
        if satellite_type:
            query = query.filter(self.model.satellite_type == satellite_type)
        
        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def get_by_project_and_owner(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        owner_id: uuid.UUID,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Imagery]:
        """Get imagery by project and verify owner"""
        from app.models.project import Project
        
        return (
            db.query(self.model)
            .join(Project)
            .filter(
                and_(
                    self.model.project_id == project_id,
                    Project.owner_id == owner_id
                )
            )
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_imagery(
        self,
        db: Session,
        *,
        owner_id: uuid.UUID,
        search_term: Optional[str] = None,
        satellite_types: Optional[List[SatelliteType]] = None,
        status_list: Optional[List[ImageryStatus]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Imagery]:
        """Search imagery with multiple filters"""
        from app.models.project import Project
        
        query = (
            db.query(self.model)
            .join(Project)
            .filter(Project.owner_id == owner_id)
        )
        
        if search_term:
            search_filter = or_(
                self.model.name.ilike(f"%{search_term}%"),
                self.model.description.ilike(f"%{search_term}%"),
                self.model.file_name.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)
        
        if satellite_types:
            query = query.filter(self.model.satellite_type.in_(satellite_types))
        
        if status_list:
            query = query.filter(self.model.status.in_(status_list))
        
        if date_from:
            query = query.filter(self.model.capture_date >= date_from)
        
        if date_to:
            query = query.filter(self.model.capture_date <= date_to)
        
        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def update_status(
        self, 
        db: Session, 
        *, 
        imagery_id: uuid.UUID, 
        status: ImageryStatus,
        processing_log: Optional[str] = None
    ) -> Optional[Imagery]:
        """Update imagery status and processing log"""
        db_obj = db.query(self.model).filter(self.model.id == imagery_id).first()
        if db_obj:
            db_obj.status = status
            if processing_log:
                db_obj.processing_log = processing_log
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_statistics(
        self, 
        db: Session, 
        *, 
        owner_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get imagery statistics for a user"""
        from app.models.project import Project
        from sqlalchemy import func
        
        # Total count
        total_count = (
            db.query(func.count(self.model.id))
            .join(Project)
            .filter(Project.owner_id == owner_id)
            .scalar()
        )
        
        # Count by status
        status_counts = (
            db.query(self.model.status, func.count(self.model.id))
            .join(Project)
            .filter(Project.owner_id == owner_id)
            .group_by(self.model.status)
            .all()
        )
        
        # Count by satellite type
        satellite_counts = (
            db.query(self.model.satellite_type, func.count(self.model.id))
            .join(Project)
            .filter(Project.owner_id == owner_id)
            .filter(self.model.satellite_type.isnot(None))
            .group_by(self.model.satellite_type)
            .all()
        )
        
        # Total file size
        total_size = (
            db.query(func.sum(self.model.file_size))
            .join(Project)
            .filter(Project.owner_id == owner_id)
            .scalar()
        ) or 0
        
        return {
            "total_count": total_count,
            "status_counts": {status.value: count for status, count in status_counts},
            "satellite_counts": {sat_type.value: count for sat_type, count in satellite_counts},
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

class CRUDProcessingResult(CRUDBase[ImageryProcessingResult, ProcessingResultCreate, ProcessingResultUpdate]):
    def get_by_imagery(
        self, 
        db: Session, 
        *, 
        imagery_id: uuid.UUID,
        result_type: Optional[str] = None
    ) -> List[ImageryProcessingResult]:
        """Get processing results by imagery"""
        query = db.query(self.model).filter(self.model.imagery_id == imagery_id)
        
        if result_type:
            query = query.filter(self.model.result_type == result_type)
        
        return query.order_by(desc(self.model.created_at)).all()

    def get_latest_by_type(
        self, 
        db: Session, 
        *, 
        imagery_id: uuid.UUID, 
        result_type: str
    ) -> Optional[ImageryProcessingResult]:
        """Get the latest processing result of a specific type"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.imagery_id == imagery_id,
                    self.model.result_type == result_type
                )
            )
            .order_by(desc(self.model.created_at))
            .first()
        )

# Create instances
imagery = CRUDImagery(Imagery)
processing_result = CRUDProcessingResult(ImageryProcessingResult)
from app.crud.base import CRUDBase
from app.models.p2p_listing import P2PListing
from app.schemas.p2p_listing import P2PListingCreate, P2PListingUpdate
from sqlalchemy.orm import Session
import uuid

class CRUDP2PListing(CRUDBase[P2PListing, P2PListingCreate, P2PListingUpdate]):
    def create_with_seller(
        self, db: Session, *, obj_in: P2PListingCreate, seller_id: uuid.UUID
    ) -> P2PListing:
        db_obj = P2PListing(
            **obj_in.dict(),
            seller_id=seller_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

p2p_listing = CRUDP2PListing(P2PListing) 
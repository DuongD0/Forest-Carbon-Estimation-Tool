import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.p2p_listing import ListingStatus

class P2PListingBase(BaseModel):
    price_per_ton: Optional[float] = None
    quantity: Optional[float] = None
    status: Optional[ListingStatus] = ListingStatus.ACTIVE

class P2PListingCreate(P2PListingBase):
    credit_id: uuid.UUID
    price_per_ton: float
    quantity: float

class P2PListingUpdate(BaseModel):
    status: Optional[ListingStatus] = None

class P2PListingInDBBase(P2PListingBase):
    id: uuid.UUID
    seller_id: uuid.UUID
    credit_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True

class P2PListing(P2PListingInDBBase):
    pass 
import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.transaction import TransactionStatus

class TransactionBase(BaseModel):
    quantity: Optional[float] = None
    total_price: Optional[float] = None
    status: Optional[TransactionStatus] = TransactionStatus.PENDING

class TransactionCreate(BaseModel):
    listing_id: uuid.UUID
    quantity: float

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus]
    stripe_charge_id: Optional[str]

class TransactionInDBBase(TransactionBase):
    id: uuid.UUID
    listing_id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    stripe_charge_id: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class Transaction(TransactionInDBBase):
    pass 
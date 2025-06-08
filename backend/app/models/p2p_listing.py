import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class ListingStatus(str, enum.Enum):
    ACTIVE = "Active"
    SOLD = "Sold"
    CANCELLED = "Cancelled"

class P2PListing(Base):
    __tablename__ = "p2p_listings"
    __table_args__ = {"schema": "p2p_marketplace"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credit_id = Column(UUID(as_uuid=True), ForeignKey("carbon_mgmt.carbon_credits.id"), unique=True, nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.users.id"), nullable=False)
    price_per_ton = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    status = Column(SQLEnum(ListingStatus), default=ListingStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    credit = relationship("CarbonCredit", back_populates="p2p_listing")
    seller = relationship("User", back_populates="listings")
    transaction = relationship("Transaction", back_populates="listing", uselist=False) 
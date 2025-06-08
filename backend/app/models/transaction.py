import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class TransactionStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "p2p_marketplace"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("p2p_marketplace.p2p_listings.id"), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.users.id"), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.users.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    stripe_charge_id = Column(String(255), unique=True, nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    listing = relationship("P2PListing", back_populates="transaction")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="transactions_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="transactions_as_seller") 
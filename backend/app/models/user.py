import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.shared import project_bookmarks

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    organization = Column(String(100))
    is_active = Column(Boolean, default=True)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    projects = relationship("Project", back_populates="owner")
    listings = relationship("P2PListing", back_populates="seller")
    transactions_as_buyer = relationship("Transaction", foreign_keys="[Transaction.buyer_id]", back_populates="buyer")
    transactions_as_seller = relationship("Transaction", foreign_keys="[Transaction.seller_id]", back_populates="seller")
    bookmarked_projects = relationship("Project", secondary=project_bookmarks, back_populates="bookmarked_by") 
import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class CreditStatus(str, enum.Enum):
    ISSUED = "Issued"
    LISTED = "Listed" # for the p2p marketplace
    SOLD = "Sold"
    RETIRED = "Retired"

class CarbonCredit(Base):
    __tablename__ = "carbon_credits"
    __table_args__ = {"schema": "carbon_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_mgmt.projects.id"), nullable=False)
    vcs_serial_number = Column(String(255), unique=True, index=True, nullable=False)
    quantity_co2e = Column(Float, nullable=False) # tonnes
    vintage_year = Column(Integer, nullable=False)
    status = Column(SQLEnum(CreditStatus), default=CreditStatus.ISSUED, nullable=False)
    issuance_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="carbon_credits")
    p2p_listing = relationship("P2PListing", back_populates="credit", uselist=False) 
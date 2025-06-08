import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class Ecosystem(Base):
    __tablename__ = "ecosystems"
    __table_args__ = {"schema": "carbon_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String)
    carbon_factor = Column(Float, nullable=False) # tCO2e per hectare per year
    biomass_factor = Column(Float, nullable=False) # biomass per hectare 
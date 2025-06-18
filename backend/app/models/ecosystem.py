import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base

class Ecosystem(Base):
    __tablename__ = "ecosystems"
    __table_args__ = {"schema": "carbon_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String)
    # simple factor for co2e per hectare per year.
    # basically a fallback if the growth model isn't set up for an ecosystem.
    carbon_factor = Column(Float, nullable=False)
    
    # params for the biomass growth model: B(t) = B_max * (1 - exp(-k*t))
    max_biomass_per_ha = Column(Float, nullable=False) # B_max: max biomass in tonnes/ha
    biomass_growth_rate = Column(Float, nullable=False) # k: the growth rate

    # RGB color ranges for forest detection (replaces HSV)
    lower_rgb = Column(JSONB) # e.g., [20, 40, 20] for dark green
    upper_rgb = Column(JSONB) # e.g., [80, 120, 80] for light green
    
    # Forest type classification for carbon density
    forest_type = Column(String(100), default="mixed_tropical") # dense_tropical, medium_tropical, etc. 
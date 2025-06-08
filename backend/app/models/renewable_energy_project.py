import uuid
import enum
from sqlalchemy import Column, String, Float, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class RenewableEnergyType(str, enum.Enum):
    SOLAR = "Solar"
    WIND = "Wind"
    HYDRO = "Hydro"
    GEOTHERMAL = "Geothermal"

class RenewableEnergyProject(Base):
    __tablename__ = "renewable_energy_projects"
    __table_args__ = {"schema": "project_mgmt"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_mgmt.projects.id"), nullable=False)
    energy_type = Column(SQLEnum(RenewableEnergyType), nullable=False)
    capacity_mw = Column(Float, nullable=False)
    annual_generation_mwh = Column(Float, nullable=False)
    grid_emission_factor = Column(Float, nullable=False) # tCO2e/MWh

    project = relationship("Project") 
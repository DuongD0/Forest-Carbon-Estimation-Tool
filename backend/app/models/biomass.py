# Models for Biomass Calculation Results

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base

class Biomass(Base):
    __tablename__ = "biomass"
    __table_args__ = {"schema": "calculation"}

    biomass_id = Column(Integer, primary_key=True, index=True)
    # Foreign keys to link calculation to project, forest, plot, species
    project_id = Column(Integer, ForeignKey("project_mgmt.projects.project_id"), nullable=False, index=True)
    forest_id = Column(Integer, ForeignKey("spatial.forest_boundaries.forest_id"), nullable=True, index=True)
    plot_id = Column(Integer, ForeignKey("spatial.forest_plots.plot_id", ondelete="SET NULL"), nullable=True, index=True)
    species_id = Column(Integer, ForeignKey("reference.tree_species.species_id", ondelete="SET NULL"), nullable=True, index=True)

    calculation_level = Column(String(20), nullable=False, default="forest", index=True) # 'forest', 'plot', 'plot_species'
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    agb_per_ha = Column(Numeric(12, 2)) # Above-ground biomass per hectare
    agb_total = Column(Numeric(15, 2)) # Total above-ground biomass
    bgb_total = Column(Numeric(15, 2)) # Total below-ground biomass
    total_biomass = Column(Numeric(15, 2)) # Total biomass
    allometric_equation_details = Column(String(255)) # Store equation name or ID used
    parameters = Column(JSON) # Equation parameters used
    uncertainty = Column(Numeric(5, 2)) # Percentage uncertainty
    created_by = Column(Integer, ForeignKey("user_mgmt.users.user_id"))

    # Relationships
    project = relationship("Project") # Assuming Project model exists
    forest = relationship("ForestBoundary") # Assuming ForestBoundary model exists
    plot = relationship("ForestPlot", back_populates="biomass_calculations")
    species = relationship("TreeSpecies") # Assuming TreeSpecies model exists
    creator = relationship("User") # Assuming User model exists
    carbon_stock_calculation = relationship("CarbonStock", back_populates="biomass_calculation", uselist=False)


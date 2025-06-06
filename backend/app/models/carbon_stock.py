# Models for Carbon Stock Calculation Results

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base

class CarbonStock(Base):
    __tablename__ = "carbon_stock"
    __table_args__ = {"schema": "calculation"}

    carbon_id = Column(Integer, primary_key=True, index=True)
    biomass_id = Column(Integer, ForeignKey("calculation.biomass.biomass_id"), nullable=False, unique=True) # One-to-one with biomass result
    # Foreign keys to link calculation to project, forest, plot, species
    project_id = Column(Integer, ForeignKey("project_mgmt.projects.project_id"), nullable=False, index=True)
    forest_id = Column(Integer, ForeignKey("spatial.forest_boundaries.forest_id"), nullable=True, index=True)
    plot_id = Column(Integer, ForeignKey("spatial.forest_plots.plot_id", ondelete="SET NULL"), nullable=True, index=True)
    species_id = Column(Integer, ForeignKey("reference.tree_species.species_id", ondelete="SET NULL"), nullable=True, index=True)

    calculation_level = Column(String(20), nullable=False, default="forest", index=True) # 'forest', 'plot', 'plot_species'
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    agb_carbon = Column(Numeric(15, 2)) # Above-ground carbon
    bgb_carbon = Column(Numeric(15, 2)) # Below-ground carbon
    total_carbon = Column(Numeric(15, 2)) # Total carbon
    carbon_density = Column(Numeric(8, 2)) # Carbon per hectare
    agb_co2e = Column(Numeric(15, 2)) # CO2 equivalent for AGB
    bgb_co2e = Column(Numeric(15, 2)) # CO2 equivalent for BGB
    total_co2e = Column(Numeric(15, 2)) # Total CO2 equivalent
    uncertainty = Column(Numeric(5, 2)) # Percentage uncertainty (propagated from biomass)
    created_by = Column(Integer, ForeignKey("user_mgmt.users.user_id"))

    # Relationships
    biomass_calculation = relationship("Biomass", back_populates="carbon_stock_calculation")
    project = relationship("Project") # Assuming Project model exists
    forest = relationship("ForestBoundary") # Assuming ForestBoundary model exists
    plot = relationship("ForestPlot", back_populates="carbon_stock_calculations")
    species = relationship("TreeSpecies") # Assuming TreeSpecies model exists
    creator = relationship("User") # Assuming User model exists
    # Relationship to carbon credit calculation (one-to-many, as one stock calc can be part of multiple credit calcs over time? Or one-to-one? Check logic)
    # Assuming one stock calculation leads to one credit calculation at a time:
    carbon_credit_calculation = relationship("CarbonCredit", back_populates="carbon_stock_calculation", uselist=False)


# Models for Baseline Calculation Results

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Date, func, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base

class Baseline(Base):
    __tablename__ = "baseline"
    __table_args__ = {"schema": "calculation"}

    baseline_id = Column(Integer, primary_key=True, index=True)
    # Foreign keys to link calculation to project, forest, plot, species
    project_id = Column(Integer, ForeignKey("project_mgmt.projects.project_id"), nullable=False, index=True)
    forest_id = Column(Integer, ForeignKey("spatial.forest_boundaries.forest_id"), nullable=True, index=True)
    plot_id = Column(Integer, ForeignKey("spatial.forest_plots.plot_id", ondelete="SET NULL"), nullable=True, index=True)
    species_id = Column(Integer, ForeignKey("reference.tree_species.species_id", ondelete="SET NULL"), nullable=True, index=True)

    calculation_level = Column(String(20), nullable=False, default="forest", index=True) # 'forest', 'plot', 'plot_species'
    reference_period_start = Column(Date)
    reference_period_end = Column(Date)
    baseline_type = Column(String(50)) # e.g., 'historical', 'projected'
    baseline_carbon = Column(Numeric(15, 2)) # Baseline carbon stock in tonnes C
    baseline_co2e = Column(Numeric(15, 2)) # Baseline CO2 equivalent in tonnes CO2e
    parameters = Column(JSON) # Baseline calculation parameters
    uncertainty = Column(Numeric(5, 2)) # Percentage uncertainty
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("user_mgmt.users.user_id"))

    # Relationships
    project = relationship("Project") # Assuming Project model exists
    forest = relationship("ForestBoundary") # Assuming ForestBoundary model exists
    plot = relationship("ForestPlot", back_populates="baseline_calculations")
    species = relationship("TreeSpecies") # Assuming TreeSpecies model exists
    creator = relationship("User") # Assuming User model exists
    # Relationship to carbon credit calculation (one baseline can be used for multiple credit calculations)
    carbon_credit_calculations = relationship("CarbonCredit", back_populates="baseline_calculation")


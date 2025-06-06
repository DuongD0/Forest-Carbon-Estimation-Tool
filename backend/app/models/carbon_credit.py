# Models for Carbon Credit Calculation Results

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base

class CarbonCredit(Base):
    __tablename__ = "carbon_credits"
    __table_args__ = {"schema": "calculation"}

    credit_id = Column(Integer, primary_key=True, index=True)
    # Foreign keys to link calculation to project, forest, plot, species
    project_id = Column(Integer, ForeignKey("project_mgmt.projects.project_id"), nullable=False, index=True)
    forest_id = Column(Integer, ForeignKey("spatial.forest_boundaries.forest_id"), nullable=True, index=True)
    plot_id = Column(Integer, ForeignKey("spatial.forest_plots.plot_id", ondelete="SET NULL"), nullable=True, index=True)
    species_id = Column(Integer, ForeignKey("reference.tree_species.species_id", ondelete="SET NULL"), nullable=True, index=True)

    # Link to the specific carbon stock calculation and baseline used
    carbon_id = Column(Integer, ForeignKey("calculation.carbon_stock.carbon_id"), nullable=False)
    baseline_id = Column(Integer, ForeignKey("calculation.baseline.baseline_id"), nullable=False)

    calculation_level = Column(String(20), nullable=False, default="forest", index=True) # 'forest', 'plot', 'plot_species'
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    emission_reduction = Column(Numeric(15, 2)) # Emission reduction in tonnes C
    emission_reduction_co2e = Column(Numeric(15, 2)) # Emission reduction in tonnes CO2e
    buffer_percentage = Column(Numeric(5, 2)) # Buffer percentage applied
    buffer_amount = Column(Numeric(15, 2)) # Buffer amount withheld in tonnes CO2e
    leakage_factor = Column(Numeric(5, 4)) # Leakage factor applied (e.g., 0.1 for 10%)
    leakage_deduction = Column(Numeric(15, 2)) # Leakage deduction in tonnes CO2e
    uncertainty_deduction = Column(Numeric(15, 2)) # Deduction due to uncertainty (if applicable)
    creditable_amount = Column(Numeric(15, 2)) # Net creditable amount in tonnes CO2e
    methodology = Column(String(50)) # Methodology used (e.g., 'VCS_VM0015')
    uncertainty = Column(Numeric(5, 2)) # Combined uncertainty percentage for the delta
    verification_status = Column(String(20), default="pending") # e.g., 'pending', 'verified', 'rejected'
    verified_by = Column(Integer, ForeignKey("user_mgmt.users.user_id"))
    verified_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("user_mgmt.users.user_id"))

    # Relationships
    project = relationship("Project") # Assuming Project model exists
    forest = relationship("ForestBoundary") # Assuming ForestBoundary model exists
    plot = relationship("ForestPlot", back_populates="carbon_credit_calculations")
    species = relationship("TreeSpecies") # Assuming TreeSpecies model exists
    creator = relationship("User") # Assuming User model exists
    verifier = relationship("User", foreign_keys=[verified_by])
    # Link back to the specific carbon stock and baseline calculations
    carbon_stock_calculation = relationship("CarbonStock", back_populates="carbon_credit_calculation")
    baseline_calculation = relationship("Baseline", back_populates="carbon_credit_calculations")


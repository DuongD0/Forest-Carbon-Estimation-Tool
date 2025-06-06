# Models for Forest Plots

from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.session import Base

class ForestPlot(Base):
    __tablename__ = "forest_plots"
    __table_args__ = (
        CheckConstraint("ST_IsValid(geometry)", name="enforce_valid_plot_geometry"),
        {"schema": "spatial"}
    )

    plot_id = Column(Integer, primary_key=True, index=True)
    forest_id = Column(Integer, ForeignKey("spatial.forest_boundaries.forest_id", ondelete="CASCADE"), nullable=False, index=True)
    plot_name = Column(String(150))
    # Ensure SRID is defined, e.g., 4326 for WGS84. Adjust if VN-2000 is used.
    geometry = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    description = Column(Text)
    # area_ha is auto-calculated in the DB schema provided, so not explicitly defined here unless needed for ORM access without refresh.
    # If needed: area_ha = Column(Numeric(12, 4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("user_mgmt.users.user_id"))

    # Relationships
    forest = relationship("ForestBoundary", back_populates="plots")
    plot_compositions = relationship("PlotComposition", back_populates="plot", cascade="all, delete-orphan")
    # Relationships to calculation results
    biomass_calculations = relationship("Biomass", back_populates="plot")
    carbon_stock_calculations = relationship("CarbonStock", back_populates="plot")
    baseline_calculations = relationship("Baseline", back_populates="plot")
    carbon_credit_calculations = relationship("CarbonCredit", back_populates="plot")
    creator = relationship("User") # Assuming User model exists in user_mgmt

# Add back-population to ForestBoundary model if not already present
# In forest.py:
# plots = relationship("ForestPlot", back_populates="forest", cascade="all, delete-orphan")


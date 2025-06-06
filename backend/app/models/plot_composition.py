# Models for Plot Composition

from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, Date, func, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base

class PlotComposition(Base):
    __tablename__ = "plot_composition"
    __table_args__ = (
        CheckConstraint("percentage_cover >= 0 AND percentage_cover <= 100", name="check_percentage_cover_range"),
        UniqueConstraint("plot_id", "species_id", "measurement_date", name="uq_plot_species_date"),
        {"schema": "spatial"}
    )

    plot_composition_id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("spatial.forest_plots.plot_id", ondelete="CASCADE"), nullable=False, index=True)
    species_id = Column(Integer, ForeignKey("reference.tree_species.species_id", ondelete="RESTRICT"), nullable=False, index=True)
    percentage_cover = Column(Numeric(5, 2)) # Percentage of plot area
    stem_density = Column(Numeric(10, 2)) # Trees per hectare (optional)
    average_dbh = Column(Numeric(8, 2)) # Average Diameter at Breast Height in cm (optional)
    average_height = Column(Numeric(8, 2)) # Average tree height in meters (optional)
    measurement_date = Column(Date, nullable=False, index=True)
    source = Column(Text) # Source of composition data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("user_mgmt.users.user_id"))

    # Relationships
    plot = relationship("ForestPlot", back_populates="plot_compositions")
    species = relationship("TreeSpecies", back_populates="plot_compositions")
    creator = relationship("User") # Assuming User model exists in user_mgmt


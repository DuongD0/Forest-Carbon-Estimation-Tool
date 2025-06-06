# Models for Tree Species

from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class TreeSpecies(Base):
    __tablename__ = "tree_species"
    __table_args__ = {"schema": "reference"}

    species_id = Column(Integer, primary_key=True, index=True)
    scientific_name = Column(String(150), unique=True, nullable=False, index=True)
    common_name_en = Column(String(150))
    common_name_vi = Column(String(150))
    wood_density = Column(Numeric(6, 4))  # g/cm³
    default_allometric_equation_id = Column(Integer, ForeignKey("reference.allometric_equations.equation_id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    allometric_equations = relationship("AllometricEquation", back_populates="species")
    plot_compositions = relationship("PlotComposition", back_populates="species")
    # Relationship to the default equation
    default_allometric_equation = relationship("AllometricEquation", foreign_keys=[default_allometric_equation_id])


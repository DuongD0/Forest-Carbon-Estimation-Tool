from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, JSON, Numeric
from sqlalchemy.orm import relationship

from app.db.session import Base

class AllometricEquation(Base):
    __tablename__ = "allometric_equations"
    __table_args__ = {"schema": "reference"}

    equation_id = Column(Integer, primary_key=True, index=True)
    equation_name = Column(String(255), nullable=False)
    equation_formula = Column(String(500), nullable=False)
    region = Column(String(100))
    species_group = Column(String(100))
    source = Column(Text)
    notes = Column(Text)

    # Relationships
    species = relationship("TreeSpecies", back_populates="allometric_equations") 
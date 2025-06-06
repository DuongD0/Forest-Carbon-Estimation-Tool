# CRUD operations for Tree Species

from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.tree_species import TreeSpecies
from app.schemas.tree_species import TreeSpeciesCreate, TreeSpeciesUpdate # Assuming schemas exist

class CRUDTreeSpecies(CRUDBase[TreeSpecies, TreeSpeciesCreate, TreeSpeciesUpdate]):
    def get_by_scientific_name(self, db: Session, *, scientific_name: str) -> Optional[TreeSpecies]:
        return db.query(TreeSpecies).filter(TreeSpecies.scientific_name == scientific_name).first()

    # Add any other specific query methods needed for tree species
    # For example, searching by common name, filtering by region applicability (if added)

tree_species = CRUDTreeSpecies(TreeSpecies)


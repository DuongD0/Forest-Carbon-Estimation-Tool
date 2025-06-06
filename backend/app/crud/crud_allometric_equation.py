from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.allometric_equation import AllometricEquation
from app.schemas.allometric_equation import AllometricEquationCreate, AllometricEquationUpdate


class CRUDAllometricEquation(CRUDBase[AllometricEquation, AllometricEquationCreate, AllometricEquationUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[AllometricEquation]:
        return db.query(AllometricEquation).filter(AllometricEquation.equation_name == name).first()


allometric_equation = CRUDAllometricEquation(AllometricEquation) 
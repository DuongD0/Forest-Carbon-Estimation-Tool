from app.crud.base import CRUDBase
from app.models.carbon_credit import CarbonCredit
from app.schemas.carbon_credit import CarbonCreditCreate, CarbonCreditUpdate
from sqlalchemy.orm import Session
import uuid

class CRUDCarbonCredit(CRUDBase[CarbonCredit, CarbonCreditCreate, CarbonCreditUpdate]):
    def get_issuance_count_for_project(self, db: Session, *, project_id: uuid.UUID) -> int:
        return db.query(CarbonCredit).filter(CarbonCredit.project_id == project_id).count()

carbon_credit = CRUDCarbonCredit(CarbonCredit) 
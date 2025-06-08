from sqlalchemy.orm import Session
import uuid
from app.crud.base import CRUDBase
from app.models.renewable_energy_project import RenewableEnergyProject
from app.schemas.renewable_energy_project import RenewableEnergyProjectCreate, RenewableEnergyProjectUpdate

class CRUDRenewableEnergyProject(CRUDBase[RenewableEnergyProject, RenewableEnergyProjectCreate, RenewableEnergyProjectUpdate]):
    def get_by_project_id(self, db: Session, *, project_id: uuid.UUID) -> RenewableEnergyProject | None:
        return db.query(RenewableEnergyProject).filter(RenewableEnergyProject.project_id == project_id).first()

renewable_energy_project = CRUDRenewableEnergyProject(RenewableEnergyProject) 
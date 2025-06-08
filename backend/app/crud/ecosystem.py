from app.crud.base import CRUDBase
from app.models.ecosystem import Ecosystem
from app.schemas.ecosystem import EcosystemCreate, EcosystemUpdate

class CRUDEcosystem(CRUDBase[Ecosystem, EcosystemCreate, EcosystemUpdate]):
    pass

ecosystem = CRUDEcosystem(Ecosystem) 
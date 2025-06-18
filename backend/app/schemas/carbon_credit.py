import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.carbon_credit import CreditStatus

class CarbonCreditBase(BaseModel):
    vcs_serial_number: Optional[str] = None
    quantity_co2e: Optional[float] = None
    vintage_year: Optional[int] = None
    status: Optional[CreditStatus] = CreditStatus.ISSUED

# schema for the api request to issue credits.
# project_id is from the url path.
# serial number is generated on the fly.
class CreditIssuanceRequest(BaseModel):
    """schema for an admin's request to issue credits."""
    project_id: uuid.UUID
    quantity_co2e: float
    vintage_year: int

class CarbonCreditCreate(CarbonCreditBase):
    project_id: uuid.UUID
    vcs_serial_number: str
    quantity_co2e: float
    vintage_year: int

class CarbonCreditUpdate(BaseModel):
    status: Optional[CreditStatus] = None

class CarbonCreditInDBBase(CarbonCreditBase):
    id: uuid.UUID
    project_id: uuid.UUID
    issuance_date: datetime

    class Config:
        orm_mode = True

class CarbonCredit(CarbonCreditInDBBase):
    pass 
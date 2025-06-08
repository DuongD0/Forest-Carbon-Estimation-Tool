# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base
from app.models import (
    User,
    Project,
    CarbonCredit,
    P2PListing,
    Transaction,
    Ecosystem,
    RenewableEnergyProject,
    AnalyticsEvent,
    project_bookmarks,
)
print("Base models for v2 imported for Alembic discovery.")


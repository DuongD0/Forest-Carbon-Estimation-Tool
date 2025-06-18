# import all the models, so Base has them before alembic runs
from app.db.session import Base
from app.models import (
    User,
    Project,
    CarbonCredit,
    P2PListing,
    Transaction,
    Ecosystem,
    AnalyticsEvent,
    project_bookmarks,
)


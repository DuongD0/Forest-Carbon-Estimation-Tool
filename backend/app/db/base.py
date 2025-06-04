# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa
from app.models.user import User, Role, Permission  # noqa
# Import other models here as they are created
from app.models.project import Project # noqa
from app.models.forest import Forest # noqa

print("Base models imported for Alembic discovery.")


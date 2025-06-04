# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa
from app.models.user import User, Role, Permission, RolePermission  # noqa
# Import other models here as they are created
# e.g., from app.models.project import Project # noqa

print("Base models imported for Alembic discovery.")


"""Create placeholder for missing revision

Revision ID: ea0749a335ca
Revises: 
Create Date: 2024-07-25 10:14:26.586617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea0749a335ca'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Drop schemas with cascade, which should remove all tables, indexes, types, etc. within them.
    op.execute("DROP SCHEMA IF EXISTS user_mgmt CASCADE")
    op.execute("DROP SCHEMA IF EXISTS spatial CASCADE")
    op.execute("DROP SCHEMA IF EXISTS reference CASCADE")
    op.execute("DROP SCHEMA IF EXISTS project_mgmt CASCADE")
    op.execute("DROP SCHEMA IF EXISTS imagery_data CASCADE")
    op.execute("DROP SCHEMA IF EXISTS calculation CASCADE")

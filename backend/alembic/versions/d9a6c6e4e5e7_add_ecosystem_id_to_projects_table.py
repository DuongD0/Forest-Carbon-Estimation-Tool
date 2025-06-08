"""Add ecosystem_id to projects table

Revision ID: d9a6c6e4e5e7
Revises: efe7aea77b25
Create Date: 2025-06-08 08:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd9a6c6e4e5e7'
down_revision: Union[str, None] = 'efe7aea77b25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('ecosystem_id', sa.UUID(), nullable=True), schema='project_mgmt')
    op.create_foreign_key(
        'fk_projects_ecosystem_id', 'projects', 'ecosystems',
        ['ecosystem_id'], ['id'],
        source_schema='project_mgmt', referent_schema='carbon_mgmt'
    )


def downgrade() -> None:
    op.drop_constraint('fk_projects_ecosystem_id', 'projects', schema='project_mgmt', type_='foreignkey')
    op.drop_column('projects', 'ecosystem_id', schema='project_mgmt') 
"""Update ecosystem biomass parameters

Revision ID: 1c3a7e4b2d5f
Revises: d9a6c6e4e5e7
Create Date: 2025-06-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1c3a7e4b2d5f'
down_revision: Union[str, None] = 'd9a6c6e4e5e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # alembic commands here
    op.add_column('ecosystems', sa.Column('max_biomass_per_ha', sa.Float(), nullable=False), schema='carbon_mgmt')
    op.add_column('ecosystems', sa.Column('biomass_growth_rate', sa.Float(), nullable=False), schema='carbon_mgmt')
    # Add the new RGB and forest type columns
    op.add_column('ecosystems', sa.Column('lower_rgb', postgresql.JSONB(), nullable=True), schema='carbon_mgmt')
    op.add_column('ecosystems', sa.Column('upper_rgb', postgresql.JSONB(), nullable=True), schema='carbon_mgmt')
    op.add_column('ecosystems', sa.Column('forest_type', sa.String(100), nullable=True), schema='carbon_mgmt')
    op.drop_column('ecosystems', 'biomass_factor', schema='carbon_mgmt')
    # end alembic commands


def downgrade() -> None:
    # alembic commands here
    op.add_column('ecosystems', sa.Column('biomass_factor', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False), schema='carbon_mgmt')
    op.drop_column('ecosystems', 'forest_type', schema='carbon_mgmt')
    op.drop_column('ecosystems', 'upper_rgb', schema='carbon_mgmt')
    op.drop_column('ecosystems', 'lower_rgb', schema='carbon_mgmt')
    op.drop_column('ecosystems', 'biomass_growth_rate', schema='carbon_mgmt')
    op.drop_column('ecosystems', 'max_biomass_per_ha', schema='carbon_mgmt')
    # end alembic commands 
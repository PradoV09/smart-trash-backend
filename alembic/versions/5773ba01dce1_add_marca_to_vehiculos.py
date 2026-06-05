"""add_marca_to_vehiculos

Revision ID: 5773ba01dce1
Revises: d271aa0eecc3
Create Date: 2026-06-05 05:34:36.154473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5773ba01dce1'
down_revision: Union[str, Sequence[str], None] = 'd271aa0eecc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('vehiculos', sa.Column('marca', sa.String(100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('vehiculos', 'marca')

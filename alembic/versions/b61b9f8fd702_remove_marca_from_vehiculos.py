"""remove_marca_from_vehiculos

Revision ID: b61b9f8fd702
Revises: 5773ba01dce1
Create Date: 2026-06-05 05:53:14.124277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b61b9f8fd702'
down_revision: Union[str, Sequence[str], None] = '5773ba01dce1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('vehiculos', 'marca')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('vehiculos', sa.Column('marca', sa.String(100), nullable=True))

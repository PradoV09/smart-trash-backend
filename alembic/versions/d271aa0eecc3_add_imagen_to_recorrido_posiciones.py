"""add imagen to recorrido_posiciones

Revision ID: d271aa0eecc3
Revises: add_uuid_recorrido
Create Date: 2026-06-03 20:18:29.625605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd271aa0eecc3'
down_revision: Union[str, Sequence[str], None] = 'add_uuid_recorrido'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "recorrido_posiciones",
        sa.Column("imagen", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("recorrido_posiciones", "imagen")

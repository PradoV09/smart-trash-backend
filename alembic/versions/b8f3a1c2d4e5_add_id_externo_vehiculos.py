"""add id_externo to vehiculos

Revision ID: b8f3a1c2d4e5
Revises: 6abd37ead668
Create Date: 2026-04-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8f3a1c2d4e5"
down_revision: Union[str, Sequence[str], None] = "6abd37ead668"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "vehiculos",
        sa.Column("id_externo", sa.String(length=36), nullable=True),
    )
    op.create_index(
        op.f("ix_vehiculos_id_externo"),
        "vehiculos",
        ["id_externo"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_vehiculos_id_externo"), table_name="vehiculos")
    op.drop_column("vehiculos", "id_externo")

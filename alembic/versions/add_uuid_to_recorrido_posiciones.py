"""add uuid to recorrido_posiciones

Revision ID: add_uuid_recorrido
Revises: b8f3a1c2d4e5
Create Date: 2026-06-03

"""
from typing import Sequence, Union
import uuid as uuid_lib

from alembic import op
import sqlalchemy as sa


revision: str = "add_uuid_recorrido"
down_revision: Union[str, Sequence[str], None] = "add_latitud_longitud"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the uuid column as nullable first
    op.add_column(
        "recorrido_posiciones",
        sa.Column("uuid", sa.String(length=36), nullable=True),
    )
    
    # Add the imagen column
    op.add_column(
        "recorrido_posiciones",
        sa.Column("imagen", sa.String(length=255), nullable=True),
    )
    
    # Generate UUIDs for existing rows
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE recorrido_posiciones SET uuid = gen_random_uuid()::text WHERE uuid IS NULL"
        )
    )
    
    # Now make the uuid column NOT NULL and add unique constraint
    op.alter_column(
        "recorrido_posiciones",
        "uuid",
        nullable=False,
    )
    op.create_unique_constraint(
        op.f("uq_recorrido_posiciones_uuid"),
        "recorrido_posiciones",
        ["uuid"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("uq_recorrido_posiciones_uuid"),
        "recorrido_posiciones",
        type_="unique",
    )
    op.drop_column("recorrido_posiciones", "uuid")
    op.drop_column("recorrido_posiciones", "imagen")

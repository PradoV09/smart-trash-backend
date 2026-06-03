"""add latitud and longitud to ft_reporte_actividad

Revision ID: add_latitud_longitud
Revises: b8f3a1c2d4e5
Create Date: 2026-06-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'add_latitud_longitud'
down_revision: Union[str, Sequence[str], None] = 'b8f3a1c2d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Agregar columnas latitud y longitud como nullable
    op.add_column('ft_reporte_actividad', sa.Column('latitud', sa.Float(), nullable=True))
    op.add_column('ft_reporte_actividad', sa.Column('longitud', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('ft_reporte_actividad', 'longitud')
    op.drop_column('ft_reporte_actividad', 'latitud')

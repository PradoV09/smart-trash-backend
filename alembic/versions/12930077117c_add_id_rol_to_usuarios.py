"""add id_rol to usuarios

Revision ID: 12930077117c
Revises: ed7b20e04bb7
Create Date: 2026-03-30 22:33:51.456584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '12930077117c'
down_revision: Union[str, Sequence[str], None] = 'ed7b20e04bb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # La columna nombre ya es tipo_rol correcto, no hay que tocarla
    
    # Agregar id_rol como nullable primero
    op.add_column('usuarios', sa.Column('id_rol', sa.Integer(), nullable=True))
    
    # Asignar el id_rol del admin a los usuarios existentes
    op.execute("UPDATE usuarios SET id_rol = (SELECT id_rol FROM roles WHERE nombre = 'admin') WHERE id_rol IS NULL")
    
    # Ahora sí hacerlo NOT NULL
    op.alter_column('usuarios', 'id_rol', nullable=False)
    
    # Agregar username como nullable primero
    op.add_column('usuarios', sa.Column('username', sa.String(length=50), nullable=True))
    op.execute("UPDATE usuarios SET username = correo WHERE username IS NULL")
    op.alter_column('usuarios', 'username', nullable=False)
    
    op.create_index(op.f('ix_usuarios_username'), 'usuarios', ['username'], unique=True)
    op.create_foreign_key(None, 'usuarios', 'roles', ['id_rol'], ['id_rol'])


def downgrade() -> None:
    op.drop_constraint(None, 'usuarios', type_='foreignkey')
    op.drop_index(op.f('ix_usuarios_username'), table_name='usuarios')
    op.drop_column('usuarios', 'id_rol')
    op.drop_column('usuarios', 'username')
    op.execute("DROP TYPE IF EXISTS tipo_rol")
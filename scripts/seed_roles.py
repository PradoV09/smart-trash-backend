"""Seeder para crear roles base del sistema.

Uso:
    python scripts/seed_roles.py
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import SessionLocal
from models.model_roles import Rol, TipoRol


ROLES_BASE = (
    TipoRol.admin,
    TipoRol.driver,
    TipoRol.recolector,
)


async def seed_roles(db: AsyncSession | None = None) -> None:
    """Crea los roles base si no existen (idempotente)."""
    owns_session = db is None
    created: list[str] = []

    if owns_session:
        async with SessionLocal() as local_db:
            async with local_db.begin():
                await _seed_roles_in_session(local_db, created)
    else:
        await _seed_roles_in_session(db, created)

    if created:
        print(f"[seed-roles] Roles creados: {', '.join(created)}")
    else:
        print("[seed-roles] Los roles base ya existen.")


async def _seed_roles_in_session(db: AsyncSession, created: list[str]) -> None:
    for rol_tipo in ROLES_BASE:
        result = await db.execute(select(Rol).where(Rol.nombre == rol_tipo))
        rol = result.scalar_one_or_none()
        if rol is None:
            db.add(Rol(nombre=rol_tipo))
            created.append(rol_tipo.value)

    await db.flush()


if __name__ == "__main__":
    asyncio.run(seed_roles())

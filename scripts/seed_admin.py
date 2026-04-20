"""Seeder para crear usuario administrador por defecto.

Uso:
    python scripts/seed_admin.py

Variables de entorno opcionales:
    ADMIN_USERNAME
    ADMIN_EMAIL
    ADMIN_PASSWORD
    ADMIN_NOMBRE_PERFIL
"""

from __future__ import annotations

import asyncio
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password
from database import SessionLocal
from models.model_perfiles import Perfil
from models.model_roles import Rol, TipoRol
from models.model_usuarios import Usuario
from scripts.seed_roles import seed_roles


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_EMAIL = "admin@gmail.com"
DEFAULT_ADMIN_PASSWORD = "admin12345"
DEFAULT_ADMIN_NOMBRE_PERFIL = "Administrador principal"


async def get_or_create_admin_role(db: AsyncSession) -> Rol:
    result = await db.execute(select(Rol).where(Rol.nombre == TipoRol.admin))
    rol = result.scalar_one_or_none()
    if rol:
        return rol

    rol = Rol(nombre=TipoRol.admin)
    db.add(rol)
    await db.flush()
    return rol


async def get_or_create_admin_profile(
    db: AsyncSession,
    id_rol: int,
    nombre_perfil: str,
) -> Perfil:
    result = await db.execute(
        select(Perfil).where(
            Perfil.id_rol == id_rol,
            Perfil.nombre == nombre_perfil,
        )
    )
    perfil = result.scalar_one_or_none()
    if perfil:
        return perfil

    perfil = Perfil(id_rol=id_rol, nombre=nombre_perfil)
    db.add(perfil)
    await db.flush()
    return perfil


async def get_existing_admin_user(
    db: AsyncSession,
    username: str,
    email: str,
) -> Usuario | None:
    result = await db.execute(
        select(Usuario).where(
            (Usuario.username == username) | (Usuario.correo == email)
        )
    )
    return result.scalar_one_or_none()


async def seed_admin() -> None:
    username = os.getenv("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME).strip()
    email = os.getenv("ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL).strip().lower()
    password = os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD).strip()
    nombre_perfil = os.getenv(
        "ADMIN_NOMBRE_PERFIL",
        DEFAULT_ADMIN_NOMBRE_PERFIL,
    ).strip()

    if not username or not email or not password or not nombre_perfil:
        raise ValueError(
            "ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD y ADMIN_NOMBRE_PERFIL no pueden estar vacios."
        )

    async with SessionLocal() as db:
        async with db.begin():
            await seed_roles(db)
            rol_admin = await get_or_create_admin_role(db)
            perfil_admin = await get_or_create_admin_profile(
                db,
                rol_admin.id_rol,
                nombre_perfil,
            )

            existing_user = await get_existing_admin_user(db, username, email)
            if existing_user:
                print(
                    f"[seed-admin] Ya existe un usuario admin: username='{existing_user.username}', email='{existing_user.correo}'."
                )
                return

            usuario_admin = Usuario(
                id_perfil=perfil_admin.id_perfil,
                id_rol=rol_admin.id_rol,
                username=username,
                correo=email,
                contraseña=hash_password(password),
                activo=True,
            )
            db.add(usuario_admin)

        print(
            f"[seed-admin] Usuario administrador creado: username='{username}', email='{email}'."
        )


if __name__ == "__main__":
    asyncio.run(seed_admin())

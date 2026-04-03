"""Dependencias reutilizables de FastAPI.

Este módulo concentra la apertura/cierre de sesiones de base de datos,
la autenticación por JWT y la autorización por roles.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import SessionLocal
from core.security import verificar_token
from models.model_usuarios import Usuario
from models.model_roles import TipoRol
from typing import AsyncGenerator

bearer_scheme = HTTPBearer(auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Entrega una sesión asíncrona de SQLAlchemy por request.

    Si todo sale bien, hace `commit` al final.
    Si ocurre una excepción, hace `rollback` para no dejar cambios parciales.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Resuelve el usuario autenticado a partir del JWT enviado por el cliente."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de acceso ausente. Proporciona un token válido para continuar.",
        )
    payload = verificar_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Inicia sesión nuevamente para obtener un token válido.",
        )
    result = await db.execute(
        select(Usuario)
        .options(selectinload(Usuario.rol), selectinload(Usuario.perfil))
        .where(Usuario.id_usuario == int(payload["sub"]))
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró un usuario asociado al token proporcionado.",
        )
    return usuario

def require_rol(*roles: TipoRol):
    """Genera una dependencia que restringe el acceso a uno o más roles."""
    async def guard(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol.nombre not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para esta acción. Roles permitidos: {', '.join(role.value for role in roles)}.",
            )
        return usuario
    return guard

AdminDep      = Depends(require_rol(TipoRol.admin))
DriverDep     = Depends(require_rol(TipoRol.driver))
RecolectorDep = Depends(require_rol(TipoRol.recolector))
UserDep       = Depends(require_rol(TipoRol.user))
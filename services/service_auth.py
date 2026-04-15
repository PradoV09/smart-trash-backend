"""Servicios de autenticación.

Aquí vive la lógica para validar credenciales y emitir tokens JWT.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from models.model_usuarios import Usuario
from models.model_roles import Rol, TipoRol
from schemas.schema_auth import LoginRequest, TokenResponse
from core.security import verify_password_async, crear_token


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Autentica un usuario y genera su token de acceso.

        Pasos:
        1. Busca por username o correo (con relación de rol cargada).
        2. Verifica la contraseña con la versión async.
        3. Rechaza usuarios con rol 'user' (no tienen acceso de autenticación).
        4. Genera un JWT con el id y rol del usuario.
        """
        result = await self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .where(
                or_(
                    Usuario.username == data.identifier,
                    Usuario.correo   == data.identifier,
                )
            )
        )
        usuario = result.scalar_one_or_none()

        # Si el usuario no existe o la contraseña no coincide, se rechaza el acceso.
        if not usuario or not await verify_password_async(data.contraseña, usuario.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas. Verifica el identificador y la contraseña e inténtalo de nuevo.",
            )

        # Los usuarios con rol 'user' (públicos) no tienen acceso de autenticación.
        if usuario.rol.nombre == TipoRol.user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Los usuarios públicos no tienen permiso para autenticarse en el sistema.",
            )

        # El token conserva la identidad mínima necesaria para autorización posterior.
        token = crear_token({
            "sub": str(usuario.id_usuario),
            "rol": usuario.id_rol,
        })

        return TokenResponse(access_token=token)

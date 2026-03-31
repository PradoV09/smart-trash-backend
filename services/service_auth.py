"""Servicios de autenticación.

Aquí vive la lógica para validar credenciales y emitir tokens JWT.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from models.model_usuarios import Usuario
from schemas.schema_auth import LoginRequest, TokenResponse
from core.security import verify_password_async, crear_token


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Autentica un usuario y genera su token de acceso.

        Pasos:
        1. Busca por username o correo.
        2. Verifica la contraseña con la versión async.
        3. Genera un JWT con el id y rol del usuario.
        """
        result = await self.db.execute(
            select(Usuario).where(
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

        # El token conserva la identidad mínima necesaria para autorización posterior.
        token = crear_token({
            "sub": str(usuario.id_usuario),
            "rol": usuario.id_rol,
        })

        return TokenResponse(access_token=token)
